# util

This repository contains small utilities and LLM-powered commands.

Below are usage examples for commands currently staged in this branch.

- explain
- refactor
- games/backup_Factorio.sh
- games/restore_Factorio.sh
- setup_ollama_gpt-oss20b.mac.sh

If you intended to include other commands, stage them (git add …) and we can amend this README.

## explain

Explain a single file or a directory snapshot using an Ollama model.

Flags:
- --file <path>  Provide exactly one of --file or --dir
- --dir <path>
- --instruction <text|file:/path>  Optional; defaults to a simple explanation request
- --model <name>  Default: gpt-oss:20b
- --exclude <patterns>  Dir mode only; comma-separated
- --max-chars <n>  Dir mode only; default 300000
- --stream  Stream model output directly to stdout

Examples:

Single file:
```bash
# Default instruction: basic explanation of the file and anything significant
go run ./llm/cmds/explain --file path/to/file.go

# Custom instruction
go run ./llm/cmds/explain --file path/to/file.go \
  --instruction "Explain for a junior dev: purpose, key functions, and pitfalls."

# Instruction from file
go run ./llm/cmds/explain --file path/to/file.go --instruction file:/abs/path/to/instruction.txt
```

Directory snapshot:
```bash
go run ./llm/cmds/explain --dir path/to/project \
  --exclude ".git,node_modules,*.png,*.jpg" \
  --max-chars 250000

# Stream output as it is generated
go run ./llm/cmds/explain --dir path/to/project --stream
```

## refactor

Feed a directory snapshot and a change request to an Ollama model. Produces artifacts driven by the output format (default: unified diff).

Flags:
- --dir <path>  Required
- --instruction <text|file:/path>  Required
- --model <name>  Default: gpt-oss:20b
- --output-format <diff|bbpack|custom>  Default: diff
- --exclude <patterns>  Comma-separated patterns to skip
- --max-chars <n>  Default 300000
- --stream  Stream model output directly to stdout

Examples:
```bash
# Generate a unified diff for a small refactor
go run ./llm/cmds/refactor --dir path/to/project \
  --instruction "Rename Foo to Bar across the codebase and update references." \
  --output-format diff

# Instruction from file
go run ./llm/cmds/refactor --dir path/to/project \
  --instruction file:/abs/path/to/change_request.txt

# Stream output
go run ./llm/cmds/refactor --dir path/to/project --instruction "Modernize http client" --stream
```

## setup_ollama_gpt-oss20b.mac.sh

Bootstrap Ollama on macOS and pull the `gpt-oss:20b` model, then run a couple of demos.

Example:
```bash
./llm/setup_ollama_gpt-oss20b.mac.sh
```

Notes:
- Requires macOS. Installs Homebrew and Ollama if absent.
- Ensures the Ollama server is running and pulls `gpt-oss:20b` on first run.

## games/backup_Factorio.sh

Back up the latest Factorio save file to iCloud Drive with a timestamped name.

Defaults (macOS):
- Save dir: `~/Library/Application Support/factorio/saves`
- Backup dir: `~/Library/Mobile Documents/com~apple~CloudDocs/Games/Factorio`

Example:
```bash
./games/backup_Factorio.sh
```

This finds the newest `*.zip` in the saves directory and copies it to the backup folder as:
`backup_<YYYYmmddHHMMSS>_<original_name>.zip`

## games/restore_Factorio.sh

Restore the most recent backup from iCloud Drive into the Factorio saves folder.

Defaults (macOS):
- Save dir: `~/Library/Application Support/factorio/saves`
- Backup dir: `~/Library/Mobile Documents/com~apple~CloudDocs/Games/Factorio`

Example:
```bash
./games/restore_Factorio.sh
```

This locates the newest `*.zip` in the backup folder and copies it into the saves directory using the same file name.

---

