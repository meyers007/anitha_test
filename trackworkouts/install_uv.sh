#!/bin/bash

# UV Installation Script
# This script installs uv (fast Python package installer and resolver)

set -e  # Exit on any error

echo "🚀 Installing UV - Fast Python Package Installer"
echo "================================================"

# Check if uv is already installed
if command -v uv &> /dev/null; then
    echo "✅ UV is already installed!"
    uv --version
    echo ""
    echo "To update UV to the latest version, run:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 0
fi

echo "📥 Downloading and installing UV..."

# Method 1: Official installer (recommended)
if command -v curl &> /dev/null; then
    echo "Using curl to install UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
elif command -v wget &> /dev/null; then
    echo "Using wget to install UV..."
    wget -qO- https://astral.sh/uv/install.sh | sh
else
    echo "❌ Error: Neither curl nor wget is available."
    echo "Please install curl or wget first, or install UV manually:"
    echo ""
    echo "Alternative installation methods:"
    echo "1. Using pip: pip install uv"
    echo "2. Using pipx: pipx install uv"
    echo "3. Using conda: conda install -c conda-forge uv"
    echo "4. Using homebrew (macOS): brew install uv"
    exit 1
fi

# Add UV to PATH for current session
export PATH="$HOME/.cargo/bin:$PATH"

# Check if installation was successful
if command -v uv &> /dev/null; then
    echo ""
    echo "✅ UV installed successfully!"
    echo "Version: $(uv --version)"
    echo ""
    echo "🎉 You can now use UV to manage Python packages!"
    echo ""
    echo "Common UV commands:"
    echo "  uv pip install <package>  # Install a package"
    echo "  uv run <script.py>        # Run a Python script"
    echo "  uv venv                   # Create a virtual environment"
    echo "  uv pip list               # List installed packages"
    echo ""
    echo "💡 Note: You may need to restart your terminal or run:"
    echo "   source ~/.bashrc  (or ~/.zshrc)"
    echo "   to ensure UV is in your PATH."
else
    echo ""
    echo "❌ Installation may have failed. Please try manual installation:"
    echo ""
    echo "Manual installation options:"
    echo "1. pip install uv"
    echo "2. pipx install uv"
    echo "3. Visit https://github.com/astral-sh/uv for more options"
    exit 1
fi

echo ""
echo "🔧 Setting up shell integration..."

# Add UV to shell profile if not already present
SHELL_PROFILE=""
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_PROFILE="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_PROFILE="$HOME/.bashrc"
fi

if [[ -n "$SHELL_PROFILE" ]] && [[ -f "$SHELL_PROFILE" ]]; then
    if ! grep -q 'export PATH="$HOME/.cargo/bin:$PATH"' "$SHELL_PROFILE"; then
        echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> "$SHELL_PROFILE"
        echo "✅ Added UV to $SHELL_PROFILE"
    else
        echo "✅ UV path already in $SHELL_PROFILE"
    fi
fi

echo ""
echo "🎯 Installation complete! UV is ready to use."
echo "Run 'uv --help' to see all available commands."
