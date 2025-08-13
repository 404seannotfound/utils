#!/usr/bin/env python3
"""
ollama_folder_to_diff.py

Feed the contents of a folder to an Ollama model (e.g., gpt-oss:20b) and
ask it to output a patch (unified diff) or another patch-like format.

Usage:
  python ollama_folder_to_diff.py \
      --dir /path/to/folder \
      --instruction "Refactor foo into bar; update docs" \
      --model gpt-oss:20b \
      --output-format diff \
      --max-chars 250000 \
      --exclude ".git,.venv,*.png,*.jpg,*.pdf,*.lock"

Notes:
- By default, only text-like files are included. Binary files are skipped.
- Large repositories get truncated by --max-chars; files are added in a
  stable order until the limit is reached.
- The prompt requests a clean unified diff suitable for `git apply`.
- If you prefer a different format (e.g., "bbpack"), use --output-format bbpack
  and adjust the header instructions below to match your desired spec.

Requires:
- Python 3.9+
- ollama CLI installed and running (https://ollama.com)

Example:
  python ollama_folder_to_diff.py --dir . \
      --instruction file:./change_request.txt \
      --model gpt-oss:20b --output-format diff > patch.diff
"""

import argparse
import fnmatch
import mimetypes
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def is_probably_text(path: Path, sniff_bytes: int = 2048) -> bool:
    """Heuristic to skip binaries. Returns True if file seems texty."""
    try:
        with path.open('rb') as f:
            chunk = f.read(sniff_bytes)
        if b"\x00" in chunk:
            return False
        # Some obvious binary extensions
        bin_exts = {
            '.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp',
            '.pdf', '.zip', '.gz', '.tar', '.xz', '.7z', '.rar',
            '.mp3', '.wav', '.ogg', '.flac', '.mp4', '.mov', '.avi', '.mkv',
            '.woff', '.woff2', '.ttf', '.otf', '.ico', '.dll', '.so', '.dylib',
            '.class', '.o', '.a', '.jar', '.war', '.exe'
        }
        if path.suffix.lower() in bin_exts:
            return False
        # Fallback to mimetypes
        mt, _ = mimetypes.guess_type(str(path))
        if mt is not None and not mt.startswith('text') and 'json' not in (mt or ''):
            # allow json-like even if not marked text
            # but exclude generic application/* binaries
            if not any(x in mt for x in ('json', 'xml', 'yaml')):
                return False
        return True
    except Exception:
        return False


def should_exclude(path: Path, root: Path, patterns: list[str]) -> bool:
    rel = str(path.relative_to(root))
    for pat in patterns:
        pat = pat.strip()
        if not pat:
            continue
        # Support folder globs like .git and file globs like *.png
        if pat.startswith('/'):
            pat = pat[1:]
        if rel == pat or rel.startswith(pat.rstrip('/') + '/'):
            return True
        if fnmatch.fnmatch(rel, pat):
            return True
    return False


def collect_files(root: Path, excludes: list[str], max_chars: int) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    total = 0
    for p in sorted(root.rglob('*')):
        if not p.is_file():
            continue
        if should_exclude(p, root, excludes):
            continue
        if not is_probably_text(p):
            continue
        try:
            text = p.read_text(encoding='utf-8', errors='replace')
        except Exception:
            continue
        addition = len(text) + len(str(p.relative_to(root))) + 64
        if total + addition > max_chars:
            # Stop once we hit the limit; you can raise --max-chars to include more
            break
        pairs.append((str(p.relative_to(root)), text))
        total += addition
    return pairs


def load_instruction(instruction_arg: str) -> str:
    if instruction_arg.startswith('file:'):
        instr_path = Path(instruction_arg[5:]).expanduser().resolve()
        return instr_path.read_text(encoding='utf-8')
    return instruction_arg


def build_prompt(files: list[tuple[str, str]], instruction: str, output_format: str) -> str:
    header_common = (
        "You are a code-editing engine. You will be given a repository snapshot "
        "and a change request. Respond with ONLY the requested artifact, no prose, "
        "no markdown fences."
    )

    if output_format.lower() == 'diff':
        header_specific = (
            " Produce a valid unified diff (git-style) that applies cleanly using `git apply` or `patch`. "
            "Use headers like: `diff --git a/<path> b/<path>`, `--- a/<path>`, `+++ b/<path>`, and proper @@ hunks. "
            "Include a proper line range in the patch output."
            "If creating new files, include the appropriate /dev/null headers. If deleting, use /dev/null accordingly."
        )
    else:
        # Generic; user can define their own packer format downstream
        header_specific = (
            f" Produce a valid {output_format} artifact per its conventional schema. "
            "Do not include any commentary or code fences."
        )

    preface = header_common + header_specific

    buf = []
    buf.append(preface)
    buf.append("\n\n<INSTRUCTION>\n")
    buf.append(instruction.strip())
    buf.append("\n</INSTRUCTION>\n\n")
    buf.append("<REPOSITORY_ROOT>\n")
    for relpath, content in files:
        buf.append(f"=== FILE: {relpath} ===\n")
        buf.append(content)
        if not content.endswith('\n'):
            buf.append('\n')
        buf.append(f"=== END FILE: {relpath} ===\n\n")
    buf.append("</REPOSITORY_ROOT>\n")
    return ''.join(buf)


def call_ollama(model: str, prompt: str, stream: bool) -> int:
    """Call `ollama run` with the given prompt. Return subprocess return code."""
    cmd = ["ollama", "run", model]
    # If you prefer the generate form, swap to: ["ollama", "generate", "-m", model, "-p", prompt]
    try:
        if stream:
            # Stream output directly to stdout
            with subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
                assert proc.stdin is not None
                proc.stdin.write(prompt.encode('utf-8'))
                proc.stdin.close()
                # Relay stdout and stderr
                for chunk in proc.stdout:
                    sys.stdout.buffer.write(chunk)
                    sys.stdout.buffer.flush()
                stderr = proc.stderr.read().decode('utf-8', errors='replace')
                rc = proc.wait()
                if rc != 0:
                    print(f"\n[ollama stderr]\n{stderr}", file=sys.stderr)
                return rc
        else:
            result = subprocess.run(cmd, input=prompt.encode('utf-8'), capture_output=True)
            sys.stdout.buffer.write(result.stdout)
            if result.returncode != 0:
                sys.stderr.write(result.stderr.decode('utf-8', errors='replace'))
            return result.returncode
    except FileNotFoundError:
        print("Error: 'ollama' CLI not found in PATH.", file=sys.stderr)
        return 127


def main():
    start = datetime.now()
    try:
        ap = argparse.ArgumentParser(description="Feed a folder to Ollama and request a diff/patch output.")
        ap.add_argument('--dir', required=True, help='Folder to snapshot and feed as context')
        ap.add_argument('--instruction', required=True, help='Change request text, or file:<path> to read from file')
        ap.add_argument('--model', default='gpt-oss:20b', help='Ollama model name (default: gpt-oss:20b)')
        ap.add_argument('--output-format', default='diff', help='diff | bbpack | <custom> (default: diff)')
        ap.add_argument('--exclude', default='.git,.hg,.svn,.venv,node_modules,*.png,*.jpg,*.jpeg,*.gif,*.webp,*.pdf,*.zip,*.mp4,*.mov,*.avi,*.mkv,*.mp3,*.wav,*.ogg,*.flac,*.dll,*.so,*.dylib,*.o,*.a,*.exe,*.class,*.jar',
                        help='Comma-separated patterns to exclude (globs and folders supported)')
        ap.add_argument('--max-chars', type=int, default=300_000, help='Max total characters of repo content to include')
        ap.add_argument('--stream', action='store_true', help='Stream model output directly to stdout')

        args = ap.parse_args()

        root = Path(args.dir).expanduser().resolve()
        if not root.is_dir():
            print(f"Not a directory: {root}", file=sys.stderr)
            sys.exit(2)

        excludes = [x.strip() for x in args.exclude.split(',') if x.strip()]

        instruction = load_instruction(args.instruction)

        files = collect_files(root, excludes, args.max_chars)
        if not files:
            print("No files collected (maybe everything excluded or directory is empty).", file=sys.stderr)
            sys.exit(3)

        prompt = build_prompt(files, instruction, args.output_format)

        rc = call_ollama(args.model, prompt, args.stream)
        sys.exit(rc)
    finally:
        end = datetime.now()
        elapsed = end - start
        # Print to stderr to avoid contaminating stdout outputs
        print(f"[Timing] Start Time: {start.isoformat()}", file=sys.stderr)
        print(f"[Timing] End Time:   {end.isoformat()}", file=sys.stderr)
        # Format elapsed as total seconds with microseconds for brevity
        secs = elapsed.total_seconds()
        print(f"[Timing] Elapsed:     {secs:.6f}s", file=sys.stderr)


if __name__ == '__main__':
    main()
