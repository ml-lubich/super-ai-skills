#!/usr/bin/env bash
# bootstrap-dev.sh - One-command developer environment setup for macOS and Linux

set -euo pipefail

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
RED="\033[0;31m"
RESET="\033[0m"

info() { echo -e "${CYAN}${BOLD}[INFO]${RESET} $*"; }
success() { echo -e "${GREEN}${BOLD}[✓]${RESET} $*"; }
warn() { echo -e "${YELLOW}${BOLD}[!]${RESET} $*"; }
err() { echo -e "${RED}${BOLD}[ERROR]${RESET} $*" >&2; }

OS="$(uname -s)"
ARCH="$(uname -m)"

info "Starting developer environment setup on ${OS} (${ARCH})..."

# 1. Package Manager Setup
if [ "$OS" = "Darwin" ]; then
    if ! command -v brew >/dev/null 2>&1; then
        info "Installing Homebrew for macOS..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        if [ -d "/opt/homebrew/bin" ]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
    else
        success "Homebrew already installed"
    fi

    info "Installing core CLI tools via Homebrew..."
    BREW_PKGS=(gh git jq curl uv python node ffmpeg)
    for pkg in "${BREW_PKGS[@]}"; do
        if ! brew list "$pkg" >/dev/null 2>&1; then
            info "Installing $pkg..."
            brew install "$pkg" || warn "Could not install $pkg"
        else
            success "$pkg already installed"
        fi
    done

elif [ "$OS" = "Linux" ]; then
    info "Detected Linux. Checking package manager..."
    if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update -y
        sudo apt-get install -y git curl jq python3 python3-pip python3-venv build-essential
        
        # Install GitHub CLI if not present
        if ! command -v gh >/dev/null 2>&1; then
            info "Installing GitHub CLI (gh)..."
            (type -p wget >/dev/null || (sudo apt update && sudo apt-get install wget -y)) \
            && sudo mkdir -p -m 755 /etc/apt/keyrings \
            && out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
            && cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
            && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
            && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
            && sudo apt update \
            && sudo apt install gh -y || warn "Failed to install gh"
        fi

        # Install uv
        if ! command -v uv >/dev/null 2>&1; then
            info "Installing uv..."
            curl -LsSf https://astral.sh/uv/install.sh | sh
        fi
    elif command -v dnf >/dev/null 2>&1; then
        sudo dnf install -y git curl jq python3 python3-pip gh
    elif command -v pacman >/dev/null 2>&1; then
        sudo pacman -Sy --noconfirm git curl jq python python-pip github-cli
    fi
fi

# 2. Python Environment & UV
if ! command -v uv >/dev/null 2>&1; then
    info "Installing uv (fast Python package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi
success "uv ready: $(uv --version)"

# 3. Super AI Skills Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
info "Setting up Super AI Skills in ${SCRIPT_DIR}..."

# Initialize submodules
git -C "$SCRIPT_DIR" submodule update --init --recursive

# Install super-ai-skills package
if command -v uv >/dev/null 2>&1; then
    info "Installing super-ai-skills via uv tool..."
    uv tool install --editable "$SCRIPT_DIR" --force
elif command -v pip >/dev/null 2>&1; then
    info "Installing super-ai-skills via pip..."
    pip install -e "$SCRIPT_DIR"
fi

# Deploy agent skills
if command -v super-skills >/dev/null 2>&1; then
    info "Running super-skills installer..."
    super-skills install-skills --target all
    super-skills doctor
fi

success "============================================================"
success " Developer environment and Super AI Skills setup complete!  "
success "============================================================"
