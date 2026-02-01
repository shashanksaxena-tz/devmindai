#!/bin/bash
# DevMind CLI Setup - Gemini + Claude
# Full CLI with Claude for complex reasoning tasks

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}=====================================${NC}"
    echo -e "${BLUE}DevMind CLI Setup - Gemini + Claude${NC}"
    echo -e "${BLUE}=====================================${NC}"
    echo ""
}

print_step() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[i]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

show_instructions() {
    print_header

    echo "This setup requires:"
    echo "  - Python 3.9+"
    echo "  - A Google API key (free at https://aistudio.google.com)"
    echo "  - An Anthropic API key (https://console.anthropic.com)"
    echo ""
    echo "Why both providers?"
    echo "  - Gemini: Fast, free tier for simple tasks"
    echo "  - Claude: Better reasoning for complex security/correctness analysis"
    echo ""
    echo "Steps to set up DevMind CLI:"
    echo ""
    echo -e "${YELLOW}1. Create virtual environment:${NC}"
    echo "   cd $PROJECT_DIR"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo ""
    echo -e "${YELLOW}2. Install DevMind CLI:${NC}"
    echo "   pip install -e \".[cli]\""
    echo ""
    echo -e "${YELLOW}3. Get API keys:${NC}"
    echo "   Gemini:  https://aistudio.google.com"
    echo "   Claude:  https://console.anthropic.com"
    echo ""
    echo -e "${YELLOW}4. Set environment variables:${NC}"
    echo "   export GOOGLE_API_KEY=your-gemini-key"
    echo "   export ANTHROPIC_API_KEY=your-claude-key"
    echo ""
    echo -e "${YELLOW}5. Verify installation:${NC}"
    echo "   devmind --help"
    echo ""
    echo -e "${YELLOW}6. Try it out:${NC}"
    echo "   devmind document /path/to/project --analyze"
    echo "   devmind review src/ --focus security  # Uses Claude"
    echo ""
    echo "For persistent configuration, create .env:"
    echo "   cat > $PROJECT_DIR/.env << 'EOF'"
    echo "   GOOGLE_API_KEY=your-gemini-key"
    echo "   ANTHROPIC_API_KEY=your-claude-key"
    echo "   EOF"
    echo ""
}

run_interactive() {
    print_header

    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        echo "Please install Python 3.9+ and try again"
        exit 1
    fi
    print_step "Python 3 found"

    # Create venv if not exists
    if [ ! -d "$PROJECT_DIR/venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv "$PROJECT_DIR/venv"
        print_step "Virtual environment created"
    else
        print_step "Virtual environment exists"
    fi

    # Activate venv
    source "$PROJECT_DIR/venv/bin/activate"
    print_step "Virtual environment activated"

    # Install package
    print_info "Installing DevMind CLI..."
    pip install -q -e "$PROJECT_DIR[cli]"
    print_step "DevMind CLI installed"

    # Gemini API key
    if [ -n "$GOOGLE_API_KEY" ]; then
        print_step "GOOGLE_API_KEY already set"
    else
        echo ""
        echo -e "${YELLOW}Enter your Google API key (Gemini)${NC}"
        echo "Get one free at: https://aistudio.google.com"
        echo ""
        read -p "GOOGLE_API_KEY: " gemini_key

        if [ -n "$gemini_key" ]; then
            echo "GOOGLE_API_KEY=$gemini_key" >> "$PROJECT_DIR/.env"
            export GOOGLE_API_KEY="$gemini_key"
            print_step "Gemini API key saved"
        fi
    fi

    # Claude API key
    if [ -n "$ANTHROPIC_API_KEY" ]; then
        print_step "ANTHROPIC_API_KEY already set"
    else
        echo ""
        echo -e "${YELLOW}Enter your Anthropic API key (Claude)${NC}"
        echo "Get one at: https://console.anthropic.com"
        echo ""
        read -p "ANTHROPIC_API_KEY: " claude_key

        if [ -n "$claude_key" ]; then
            echo "ANTHROPIC_API_KEY=$claude_key" >> "$PROJECT_DIR/.env"
            export ANTHROPIC_API_KEY="$claude_key"
            print_step "Claude API key saved"
        fi
    fi

    echo ""
    print_step "Setup complete!"
    echo ""
    echo "To use DevMind:"
    echo "  cd $PROJECT_DIR"
    echo "  source venv/bin/activate"
    echo "  devmind --help"
    echo ""
    echo "LLM routing:"
    echo "  - Simple tasks → Gemini (free)"
    echo "  - Complex tasks → Claude (security review, etc.)"
    echo ""
    echo "Try it out:"
    echo "  devmind document /path/to/project --analyze"
    echo "  devmind review src/ --focus security"
}

# Main
if [ "$1" == "--interactive" ] || [ "$1" == "-i" ]; then
    run_interactive
else
    show_instructions
    echo ""
    echo -e "Run with ${YELLOW}--interactive${NC} to set up automatically:"
    echo "  $0 --interactive"
fi
