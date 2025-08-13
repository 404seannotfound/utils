#!/usr/bin/env bash
set -euo pipefail

# -------- Helpers --------
msg() { printf "\n\033[1;32m▶ %s\033[0m\n" "$*"; }
warn() { printf "\n\033[1;33m⚠ %s\033[0m\n" "$*"; }
err() { printf "\n\033[1;31m✖ %s\033[0m\n" "$*"; }
have() { command -v "$1" >/dev/null 2>&1; }

# -------- Preflight (macOS) --------
if [[ "$(uname -s)" != "Darwin" ]]; then
  err "This script is for macOS. Aborting."
  exit 1
fi

# -------- Homebrew --------
if ! have brew; then
  msg "Installing Homebrew…"
  NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  if [[ -d "/opt/homebrew/bin" ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> "${HOME}/.zprofile"
  else
    eval "$(/usr/local/bin/brew shellenv)"
    echo 'eval "$(/usr/local/bin/brew shellenv)"' >> "${HOME}/.zprofile"
  fi
else
  msg "Homebrew already installed. Updating brew…"
  brew update
fi

# -------- Ollama --------
if ! have ollama; then
  msg "Installing Ollama via Homebrew…"
  brew install ollama
else
  msg "Ollama already installed. Version: $(ollama --version || true)"
  # Optional: uncomment to ensure you’re on a recent build
  # brew upgrade ollama || true
fi

# Ensure Ollama server is up
if ! curl -sSf http://localhost:11434/ >/dev/null 2>&1; then
  msg "Starting Ollama server…"
  nohup ollama serve >/tmp/ollama_server.log 2>&1 &
  for i in {1..20}; do
    sleep 0.5
    if curl -sSf http://localhost:11434/ >/dev/null 2>&1; then
      break
    fi
  done
fi
if ! curl -sSf http://localhost:11434/ >/dev/null 2>&1; then
  err "Could not confirm Ollama server is running. Check /tmp/ollama_server.log"
  exit 1
fi

# -------- Pull model --------
msg "Pulling model: gpt-oss:20b (one-time download)…"
ollama pull gpt-oss:20b

# -------- Demo 1: Count Rs in the word --------
WORD="Strawberrirriarriarium"
msg "Running Demo 1 (count Rs/r in the word)…"
PROMPT1=$(cat <<'EOF'
Count how many letters 'R' or 'r' are in the following string.
Answer with just the integer count.

String:
EOF
)
PROMPT1="${PROMPT1}
${WORD}
"

echo "Prompt:"
echo "-----"
printf "%s\n" "$PROMPT1"
echo "-----"
echo

DEMO1_OUT="$(printf "%s" "$PROMPT1" | ollama run gpt-oss:20b || true)"

echo "Model Output:"
echo "-----"
printf "%s\n" "$DEMO1_OUT"
echo "-----"

# -------- Demo 2: Ask about a file’s contents --------
DEMO_DIR="$(mktemp -d)"
FILE_PATH="${DEMO_DIR}/example.txt"

msg "Preparing Demo 2 file at: ${FILE_PATH}"
cat > "${FILE_PATH}" <<'EOF'
This is an example file created by the setup script.
It has multiple lines.
Line 3 is here.
EOF

# Build a prompt that embeds the file contents via a here-doc, then pipe to ollama
PROMPT2_HEAD=$(cat <<'EOF'
You will be given the full contents of a local text file below.
Please respond ONLY with the exact file contents (no extra commentary).

--- FILE START ---
EOF
)

PROMPT2_TAIL=$'\n--- FILE END ---\n'

FULL_PROMPT2="${PROMPT2_HEAD}
$(cat "${FILE_PATH}")${PROMPT2_TAIL}"

msg "Running Demo 2 (ask model for the file contents)…"
echo "Prompt (first 200 chars):"
echo "-----"
printf "%.200s" "$FULL_PROMPT2"
echo "…"
echo "-----"
echo

DEMO2_OUT="$(printf "%s" "$FULL_PROMPT2" | ollama run gpt-oss:20b || true)"

echo "Model Output:"
echo "-----"
printf "%s\n" "$DEMO2_OUT"
echo "-----"

# -------- Wrap up --------
msg "All done!"
echo "Demo 1 word: ${WORD}"
echo "Demo 1 result: ${DEMO1_OUT}"
echo
echo "Demo 2 file:  ${FILE_PATH}"
echo "You can inspect it with:  cat ${FILE_PATH}"
echo
warn "Tip: To re-run safely, delete the temp dir: rm -rf ${DEMO_DIR}"
