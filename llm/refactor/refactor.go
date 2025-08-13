package main

import (
	"bufio"
	"bytes"
	"errors"
	"flag"
	"fmt"
	"io"
	"mime"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

// Heuristic to skip binaries. Returns true if file seems texty.
func isProbablyText(path string, sniffBytes int) bool {
	f, err := os.Open(path)
	if err != nil {
		return false
	}
	defer f.Close()

	buf := make([]byte, sniffBytes)
	n, _ := f.Read(buf)
	buf = buf[:n]
	if bytes.IndexByte(buf, 0x00) >= 0 { // contains NUL
		return false
	}

	binExts := map[string]struct{}{
		".png": {}, ".jpg": {}, ".jpeg": {}, ".gif": {}, ".webp": {}, ".bmp": {},
		".pdf": {}, ".zip": {}, ".gz": {}, ".tar": {}, ".xz": {}, ".7z": {}, ".rar": {},
		".mp3": {}, ".wav": {}, ".ogg": {}, ".flac": {}, ".mp4": {}, ".mov": {}, ".avi": {}, ".mkv": {},
		".woff": {}, ".woff2": {}, ".ttf": {}, ".otf": {}, ".ico": {}, ".dll": {}, ".so": {}, ".dylib": {},
		".class": {}, ".o": {}, ".a": {}, ".jar": {}, ".war": {}, ".exe": {},
	}
	if _, ok := binExts[strings.ToLower(filepath.Ext(path))]; ok {
		return false
	}

	// Fallback to mime type
	mt := mime.TypeByExtension(filepath.Ext(path))
	if mt != "" && !strings.HasPrefix(mt, "text") && !strings.Contains(mt, "json") {
		if !(strings.Contains(mt, "json") || strings.Contains(mt, "xml") || strings.Contains(mt, "yaml")) {
			return false
		}
	}
	return true
}

// shouldExclude checks if the path (relative to root) matches any of the patterns.
func shouldExclude(rel string, patterns []string) bool {
	for _, p := range patterns {
		p = strings.TrimSpace(p)
		if p == "" {
			continue
		}
		if strings.HasPrefix(p, "/") {
			p = strings.TrimPrefix(p, "/")
		}
		// Folder direct match or prefix
		if rel == p || strings.HasPrefix(rel, strings.TrimSuffix(p, "/")+"/") {
			return true
		}
		matched, _ := filepath.Match(p, rel)
		if matched {
			return true
		}
	}
	return false
}

type filePair struct {
	rel  string
	text string
}

func collectFiles(root string, excludes []string, maxChars int) ([]filePair, error) {
	var files []string
	// First, list all files to sort for stable order
	err := filepath.WalkDir(root, func(path string, d os.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if d.IsDir() {
			return nil
		}
		rel, err := filepath.Rel(root, path)
		if err != nil {
			return err
		}
		rel = filepath.ToSlash(rel)
		if shouldExclude(rel, excludes) {
			return nil
		}
		if !isProbablyText(path, 2048) {
			return nil
		}
		files = append(files, path)
		return nil
	})
	if err != nil {
		return nil, err
	}

	sort.Strings(files)

	pairs := make([]filePair, 0, len(files))
	total := 0
	for _, p := range files {
		rel, _ := filepath.Rel(root, p)
		rel = filepath.ToSlash(rel)
		b, err := os.ReadFile(p)
		if err != nil {
			continue
		}
		text := string(b)
		addition := len(text) + len(rel) + 64
		if total+addition > maxChars {
			break
		}
		pairs = append(pairs, filePair{rel: rel, text: text})
		total += addition
	}
	return pairs, nil
}

func loadInstruction(arg string) (string, error) {
	if strings.HasPrefix(arg, "file:") {
		p := strings.TrimPrefix(arg, "file:")
		b, err := os.ReadFile(p)
		if err != nil {
			return "", err
		}
		return string(b), nil
	}
	return arg, nil
}

func buildPrompt(files []filePair, instruction, outputFormat string) string {
	headerCommon := "You are a code-editing engine. You will be given a repository snapshot " +
		"and a change request. Respond with ONLY the requested artifact, no prose, " +
		"no markdown fences."

	var headerSpecific string
	if strings.EqualFold(outputFormat, "diff") {
		headerSpecific = " Produce a valid unified diff (git-style) that applies cleanly using `git apply` or `patch`. " +
			"Use headers like: `diff --git a/<path> b/<path>`, `--- a/<path>`, `+++ b/<path>`, and proper @@ hunks. " +
			"Include a proper line range in the patch output." +
			"If creating new files, include the appropriate /dev/null headers. If deleting, use /dev/null accordingly."
	} else {
		headerSpecific = fmt.Sprintf(" Produce a valid %s artifact per its conventional schema. ", outputFormat) +
			"Do not include any commentary or code fences."
	}
	preface := headerCommon + headerSpecific

	var b strings.Builder
	b.WriteString(preface)
	b.WriteString("\n\n<INSTRUCTION>\n")
	b.WriteString(strings.TrimSpace(instruction))
	b.WriteString("\n</INSTRUCTION>\n\n")
	b.WriteString("<REPOSITORY_ROOT>\n")
	for _, fp := range files {
		b.WriteString("=== FILE: ")
		b.WriteString(fp.rel)
		b.WriteString(" ===\n")
		b.WriteString(fp.text)
		if !strings.HasSuffix(fp.text, "\n") {
			b.WriteString("\n")
		}
		b.WriteString("=== END FILE: ")
		b.WriteString(fp.rel)
		b.WriteString(" ===\n\n")
	}
	b.WriteString("</REPOSITORY_ROOT>\n")
	return b.String()
}

func callOllama(model, prompt string, stream bool, stdout io.Writer, stderr io.Writer) (int, error) {
	cmd := exec.Command("ollama", "run", model)
	stdin, err := cmd.StdinPipe()
	if err != nil {
		return 0, err
	}
	cmd.Stdout = stdout
	cmd.Stderr = stderr

	if stream {
		if err := cmd.Start(); err != nil {
			return 0, err
		}
		go func() {
			w := bufio.NewWriter(stdin)
			_, _ = w.WriteString(prompt)
			w.Flush()
			stdin.Close()
		}()
		err = cmd.Wait()
		if err != nil {
			if exitErr, ok := err.(*exec.ExitError); ok {
				return exitErr.ExitCode(), nil
			}
			return 1, err
		}
		return 0, nil
	}

	// non-stream: capture output then write
	cmd.Stdout = &bytes.Buffer{}
	cmd.Stderr = &bytes.Buffer{}
	if err := cmd.Start(); err != nil {
		return 0, err
	}
	_, _ = io.WriteString(stdin, prompt)
	stdin.Close()
	err = cmd.Wait()
	// forward captured buffers
	if buf, ok := cmd.Stdout.(*bytes.Buffer); ok {
		_, _ = io.Copy(stdout, buf)
	}
	if buf, ok := cmd.Stderr.(*bytes.Buffer); ok {
		_, _ = io.Copy(stderr, buf)
	}
	if err != nil {
		if exitErr, ok := err.(*exec.ExitError); ok {
			return exitErr.ExitCode(), nil
		}
		return 1, err
	}
	return 0, nil
}

func run() int {
	dir := flag.String("dir", "", "Folder to snapshot and feed as context")
	instructionArg := flag.String("instruction", "", "Change request text, or file:<path> to read from file")
	model := flag.String("model", "gpt-oss:20b", "Ollama model name")
	outputFormat := flag.String("output-format", "diff", "diff | bbpack | <custom>")
	exclude := flag.String("exclude", ".git,.hg,.svn,.venv,node_modules,*.png,*.jpg,*.jpeg,*.gif,*.webp,*.pdf,*.zip,*.mp4,*.mov,*.avi,*.mkv,*.mp3,*.wav,*.ogg,*.flac,*.dll,*.so,*.dylib,*.o,*.a,*.exe,*.class,*.jar", "Comma-separated patterns to exclude")
	maxChars := flag.Int("max-chars", 300000, "Max total characters of repo content to include")
	stream := flag.Bool("stream", false, "Stream model output directly to stdout")
	flag.Parse()

	if *dir == "" {
		fmt.Fprintln(os.Stderr, "--dir is required")
		return 2
	}
	if *instructionArg == "" {
		fmt.Fprintln(os.Stderr, "--instruction is required")
		return 2
	}

	root, err := filepath.Abs(*dir)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 2
	}
	st, err := os.Stat(root)
	if err != nil || !st.IsDir() {
		fmt.Fprintf(os.Stderr, "Not a directory: %s\n", root)
		return 2
	}

	excludes := []string{}
	for _, x := range strings.Split(*exclude, ",") {
		x = strings.TrimSpace(x)
		if x != "" {
			excludes = append(excludes, x)
		}
	}

	instr, err := loadInstruction(*instructionArg)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 2
	}

	pairs, err := collectFiles(root, excludes, *maxChars)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 2
	}
	if len(pairs) == 0 {
		fmt.Fprintln(os.Stderr, "No files collected (maybe everything excluded or directory is empty).")
		return 3
	}

	prompt := buildPrompt(pairs, instr, *outputFormat)

	rc, err := callOllama(*model, prompt, *stream, os.Stdout, os.Stderr)
	if err != nil {
		var pathErr *exec.Error
		if errors.As(err, &pathErr) && pathErr.Err == exec.ErrNotFound {
			fmt.Fprintln(os.Stderr, "Error: 'ollama' CLI not found in PATH.")
			return 127
		}
		// Non-standard failure
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	return rc
}

func main() {
	start := time.Now()
	rc := run()
	end := time.Now()
	fmt.Fprintf(os.Stderr, "[Timing] Start Time: %s\n", start.Format(time.RFC3339Nano))
	fmt.Fprintf(os.Stderr, "[Timing] End Time:   %s\n", end.Format(time.RFC3339Nano))
	fmt.Fprintf(os.Stderr, "[Timing] Elapsed:     %.6fs\n", end.Sub(start).Seconds())
	os.Exit(rc)
}
