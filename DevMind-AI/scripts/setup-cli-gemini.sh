#!/bin/bash
# DevMind CLI Setup - Gemini Only
# Minimal setup with free Gemini API

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
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}DevMind CLI Setup - Gemini Only${NC}"
    echo -e "${BLUE}================================${NC}"
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
    echo ""
    echo "Steps to set up DevMind CLI with Gemini:"
    echo ""
    echo -e "${YELLOW}1. Create virtual environment:${NC}"
    echo "   cd $PROJECT_DIR"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo ""
    echo -e "${YELLOW}2. Install DevMind CLI:${NC}"
    echo "   pip install -e \".[cli]\""
    echo ""
    echo -e "${YELLOW}3. Get your Gemini API key:${NC}"
    echo "   Visit: https://aistudio.google.com"
    echo "   Click 'Get API key' and create a new key"
    echo ""
    echo -e "${YELLOW}4. Set environment variable:${NC}"
    echo "   export GOOGLE_API_KEY=your-api-key-here"
    echo ""
    echo -e "${YELLOW}5. Verify installation:${NC}"
    echo "   devmind --help"
    echo ""
    echo -e "${YELLOW}6. Try it out:${NC}"
    echo "   devmind document /path/to/project --analyze"
    echo ""
    echo "For persistent configuration, add to your shell profile:"
    echo "   echo 'export GOOGLE_API_KEY=your-key' >> ~/.bashrc"
    echo ""
    echo "Or create a .env file in the DevMind directory:"
    echo "   echo 'GOOGLE_API_KEY=your-key' > $PROJECT_DIR/.env"
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

    # Check for existing API key
    if [ -n "$GOOGLE_API_KEY" ]; then
        print_step "GOOGLE_API_KEY already set"
    else
        echo ""
        echo -e "${YELLOW}Enter your Google API key${NC}"
        echo "Get one free at: https://aistudio.google.com"
        echo ""
        read -p "GOOGLE_API_KEY: " api_key

        if [ -n "$api_key" ]; then
            # Save to .env
            echo "GOOGLE_API_KEY=$api_key" >> "$PROJECT_DIR/.env"
            export GOOGLE_API_KEY="$api_key"
            print_step "API key saved to .env"
        else
            print_error "No API key provided"
            echo "You can set it later with: export GOOGLE_API_KEY=your-key"
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
    echo "Try it out:"
    echo "  devmind document /path/to/project --analyze"
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
