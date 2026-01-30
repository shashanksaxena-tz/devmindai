#!/bin/bash
# DevMind CLI Setup - Full Configuration
# All AI providers + GitHub integration

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
    echo -e "${BLUE}=======================================${NC}"
    echo -e "${BLUE}DevMind CLI Setup - Full Configuration${NC}"
    echo -e "${BLUE}=======================================${NC}"
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

    echo "This setup includes:"
    echo "  - Gemini (primary, free tier)"
    echo "  - Claude (complex reasoning)"
    echo "  - OpenAI (fallback)"
    echo "  - GitHub CLI (PR features)"
    echo ""
    echo "Required:"
    echo "  - Python 3.9+"
    echo "  - At least one LLM API key"
    echo ""
    echo "Optional:"
    echo "  - GitHub CLI (gh) for generate-pr and pr-review"
    echo ""
    echo "Steps:"
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
    echo "   Gemini:  https://aistudio.google.com (free)"
    echo "   Claude:  https://console.anthropic.com"
    echo "   OpenAI:  https://platform.openai.com"
    echo ""
    echo -e "${YELLOW}4. Set environment variables:${NC}"
    echo "   export GOOGLE_API_KEY=your-gemini-key"
    echo "   export ANTHROPIC_API_KEY=your-claude-key"
    echo "   export OPENAI_API_KEY=your-openai-key"
    echo ""
    echo -e "${YELLOW}5. (Optional) Install GitHub CLI:${NC}"
    echo "   brew install gh   # macOS"
    echo "   gh auth login"
    echo ""
    echo -e "${YELLOW}6. Verify installation:${NC}"
    echo "   devmind --help"
    echo "   devmind tools  # Check AI tool availability"
    echo ""
    echo "For persistent configuration, create .env:"
    echo "   cat > $PROJECT_DIR/.env << 'EOF'"
    echo "   GOOGLE_API_KEY=your-gemini-key"
    echo "   ANTHROPIC_API_KEY=your-claude-key"
    echo "   OPENAI_API_KEY=your-openai-key"
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

    # Check GitHub CLI
    if command -v gh &> /dev/null; then
        print_step "GitHub CLI (gh) found"
    else
        print_info "GitHub CLI (gh) not found - PR features won't work"
        echo "Install with: brew install gh"
    fi

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

    # Clear existing .env
    > "$PROJECT_DIR/.env"

    # Gemini API key
    echo ""
    echo -e "${YELLOW}Enter your Google API key (Gemini) - Recommended, free tier${NC}"
    echo "Get one at: https://aistudio.google.com"
    echo "Press Enter to skip"
    read -p "GOOGLE_API_KEY: " gemini_key

    if [ -n "$gemini_key" ]; then
        echo "GOOGLE_API_KEY=$gemini_key" >> "$PROJECT_DIR/.env"
        export GOOGLE_API_KEY="$gemini_key"
        print_step "Gemini API key saved"
    fi

    # Claude API key
    echo ""
    echo -e "${YELLOW}Enter your Anthropic API key (Claude) - For complex tasks${NC}"
    echo "Get one at: https://console.anthropic.com"
    echo "Press Enter to skip"
    read -p "ANTHROPIC_API_KEY: " claude_key

    if [ -n "$claude_key" ]; then
        echo "ANTHROPIC_API_KEY=$claude_key" >> "$PROJECT_DIR/.env"
        export ANTHROPIC_API_KEY="$claude_key"
        print_step "Claude API key saved"
    fi

    # OpenAI API key
    echo ""
    echo -e "${YELLOW}Enter your OpenAI API key - Fallback provider${NC}"
    echo "Get one at: https://platform.openai.com"
    echo "Press Enter to skip"
    read -p "OPENAI_API_KEY: " openai_key

    if [ -n "$openai_key" ]; then
        echo "OPENAI_API_KEY=$openai_key" >> "$PROJECT_DIR/.env"
        export OPENAI_API_KEY="$openai_key"
        print_step "OpenAI API key saved"
    fi

    # Check at least one key is set
    if [ -z "$gemini_key" ] && [ -z "$claude_key" ] && [ -z "$openai_key" ]; then
        print_error "No API keys provided"
        echo "At least one LLM API key is required"
        exit 1
    fi

    echo ""
    print_step "Setup complete!"
    echo ""
    echo "Configured providers:"
    [ -n "$gemini_key" ] && echo "  ✓ Gemini (primary)"
    [ -n "$claude_key" ] && echo "  ✓ Claude (complex tasks)"
    [ -n "$openai_key" ] && echo "  ✓ OpenAI (fallback)"
    echo ""
    echo "To use DevMind:"
    echo "  cd $PROJECT_DIR"
    echo "  source venv/bin/activate"
    echo "  devmind --help"
    echo ""
    echo "Check available AI tools:"
    echo "  devmind tools"
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
