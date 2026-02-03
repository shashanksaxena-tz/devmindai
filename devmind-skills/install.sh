#!/bin/bash

# DevMind Skills Installer
# Install AI coding skills to your project

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR=""
EDITOR="all"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║             DevMind AI Skills Installer                       ║"
    echo "║   Production-ready skills for AI coding assistants            ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_usage() {
    echo "Usage: ./install.sh <target-directory> [options]"
    echo ""
    echo "Options:"
    echo "  --claude        Install Claude Code skills only"
    echo "  --cursor        Install Cursor AI rules only"
    echo "  --copilot       Install GitHub Copilot config only"
    echo "  --opencode      Install OpenCode commands only"
    echo "  --gemini        Install Gemini CLI commands only"
    echo "  --antigravity   Install Antigravity skills only"
    echo "  --all           Install all editors (default)"
    echo "  --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./install.sh ~/my-project --all"
    echo "  ./install.sh ~/my-project --claude --cursor"
    echo "  ./install.sh . --copilot"
}

install_claude() {
    echo -e "${GREEN}📦 Installing Claude Code skills...${NC}"
    mkdir -p "$TARGET_DIR/.claude/skills"
    cp -r "$SCRIPT_DIR/claude/.claude/skills/"* "$TARGET_DIR/.claude/skills/"
    echo -e "   ${GREEN}✅${NC} Installed to .claude/skills/"
    echo "   Skills: code-review, security-scan, test-generator, document-project, pr-review, per-folder-docs"
}

install_cursor() {
    echo -e "${GREEN}📦 Installing Cursor AI rules...${NC}"
    mkdir -p "$TARGET_DIR/.cursor/rules"
    cp -r "$SCRIPT_DIR/cursor/.cursor/rules/"* "$TARGET_DIR/.cursor/rules/"
    echo -e "   ${GREEN}✅${NC} Installed to .cursor/rules/"
    echo "   Rules: code-review.mdc, security-scan.mdc, test-generator.mdc, document-project.mdc, pr-review.mdc, per-folder-docs.mdc"
}

install_copilot() {
    echo -e "${GREEN}📦 Installing GitHub Copilot config...${NC}"
    mkdir -p "$TARGET_DIR/.github/instructions"
    cp "$SCRIPT_DIR/copilot/.github/copilot-instructions.md" "$TARGET_DIR/.github/"
    cp -r "$SCRIPT_DIR/copilot/.github/instructions/"* "$TARGET_DIR/.github/instructions/" 2>/dev/null || true
    
    # Install AGENTS.md if not exists or update
    if [ -f "$TARGET_DIR/AGENTS.md" ]; then
        echo -e "   ${YELLOW}⚠️${NC} AGENTS.md exists - creating AGENTS.devmind.md instead"
        cp "$SCRIPT_DIR/copilot/AGENTS.md" "$TARGET_DIR/AGENTS.devmind.md"
    else
        cp "$SCRIPT_DIR/copilot/AGENTS.md" "$TARGET_DIR/"
    fi
    
    echo -e "   ${GREEN}✅${NC} Installed to .github/"
    echo "   Files: copilot-instructions.md, AGENTS.md, python.instructions.md, typescript.instructions.md"
}

install_opencode() {
    echo -e "${GREEN}📦 Installing OpenCode commands...${NC}"
    mkdir -p "$TARGET_DIR/.opencode/commands"
    cp -r "$SCRIPT_DIR/opencode/.opencode/commands/"* "$TARGET_DIR/.opencode/commands/"
    
    if [ -f "$TARGET_DIR/AGENTS.md" ]; then
        echo -e "   ${YELLOW}⚠️${NC} AGENTS.md exists - skipping (commands installed)"
    else
        cp "$SCRIPT_DIR/opencode/AGENTS.md" "$TARGET_DIR/"
    fi
    
    echo -e "   ${GREEN}✅${NC} Installed to .opencode/commands/"
    echo "   Commands: /review, /scan, /test, /docs, /pr, /folder-docs"
}

install_gemini() {
    echo -e "${GREEN}📦 Installing Gemini CLI config...${NC}"
    mkdir -p "$TARGET_DIR/.gemini/commands"
    cp -r "$SCRIPT_DIR/gemini/.gemini/commands/"* "$TARGET_DIR/.gemini/commands/"
    
    if [ -f "$TARGET_DIR/GEMINI.md" ]; then
        echo -e "   ${YELLOW}⚠️${NC} GEMINI.md exists - creating GEMINI.devmind.md instead"
        cp "$SCRIPT_DIR/gemini/GEMINI.md" "$TARGET_DIR/GEMINI.devmind.md"
    else
        cp "$SCRIPT_DIR/gemini/GEMINI.md" "$TARGET_DIR/"
    fi
    
    echo -e "   ${GREEN}✅${NC} Installed to .gemini/commands/"
    echo "   Commands: /review, /scan, /test, /docs, /pr, /folder-docs"
}

install_antigravity() {
    echo -e "${GREEN}📦 Installing Antigravity skills...${NC}"
    mkdir -p "$TARGET_DIR/.agent/skills"
    cp -r "$SCRIPT_DIR/antigravity/.agent/skills/"* "$TARGET_DIR/.agent/skills/"
    
    if [ -f "$TARGET_DIR/AGENTS.md" ]; then
        echo -e "   ${YELLOW}⚠️${NC} AGENTS.md exists - skipping (skills installed)"
    else
        cp "$SCRIPT_DIR/antigravity/AGENTS.md" "$TARGET_DIR/"
    fi
    
    echo -e "   ${GREEN}✅${NC} Installed to .agent/skills/"
    echo "   Skills: code-review, security-scan, test-generator, document-project, pr-review, per-folder-docs"
}

print_post_install() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ Installation complete!${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "📚 Available Commands by Editor:"
    echo ""
    echo "  Claude Code:"
    echo "    /code-review <path>        Deep multi-pass code review"
    echo "    /security-scan <path>      OWASP Top 10 security scan"
    echo "    /generate-tests <file>     Generate comprehensive tests"
    echo "    /document-project          Generate AI-ready docs"
    echo ""
    echo "  Cursor AI:"
    echo "    @code-review               Auto-applies to matching files"
    echo "    @security-scan             Or invoke directly in chat"
    echo ""
    echo "  GitHub Copilot:"
    echo "    @workspace Review this code"
    echo "    @workspace Security scan src/"
    echo ""
    echo "  OpenCode:"
    echo "    /review <path>"
    echo "    /scan <path>"
    echo "    /test <file>"
    echo ""
    echo "  Gemini CLI:"
    echo "    /review <path>"
    echo "    /scan <path>"
    echo ""
    echo "  Antigravity:"
    echo "    /code-review <path>"
    echo "    /security-scan <path>"
    echo ""
    echo "📖 For detailed documentation, see: $SCRIPT_DIR/README.md"
}

# Parse arguments
print_header

if [ $# -eq 0 ]; then
    print_usage
    exit 1
fi

# First argument should be target directory
TARGET_DIR="$1"
shift

if [ "$TARGET_DIR" == "--help" ]; then
    print_usage
    exit 0
fi

# Check if target exists
if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${RED}Error: Target directory does not exist: $TARGET_DIR${NC}"
    exit 1
fi

# Convert to absolute path
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

echo "Source: $SCRIPT_DIR"
echo "Target: $TARGET_DIR"
echo ""

# Parse remaining flags
INSTALL_CLAUDE=false
INSTALL_CURSOR=false
INSTALL_COPILOT=false
INSTALL_OPENCODE=false
INSTALL_GEMINI=false
INSTALL_ANTIGRAVITY=false
INSTALL_ALL=false

if [ $# -eq 0 ]; then
    INSTALL_ALL=true
fi

while [ $# -gt 0 ]; do
    case "$1" in
        --claude)
            INSTALL_CLAUDE=true
            ;;
        --cursor)
            INSTALL_CURSOR=true
            ;;
        --copilot)
            INSTALL_COPILOT=true
            ;;
        --opencode)
            INSTALL_OPENCODE=true
            ;;
        --gemini)
            INSTALL_GEMINI=true
            ;;
        --antigravity)
            INSTALL_ANTIGRAVITY=true
            ;;
        --all)
            INSTALL_ALL=true
            ;;
        --help)
            print_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            print_usage
            exit 1
            ;;
    esac
    shift
done

# If --all or no specific editor selected, install all
if [ "$INSTALL_ALL" = true ]; then
    INSTALL_CLAUDE=true
    INSTALL_CURSOR=true
    INSTALL_COPILOT=true
    INSTALL_OPENCODE=true
    INSTALL_GEMINI=true
    INSTALL_ANTIGRAVITY=true
fi

# Run installations
if [ "$INSTALL_CLAUDE" = true ]; then
    install_claude
fi

if [ "$INSTALL_CURSOR" = true ]; then
    install_cursor
fi

if [ "$INSTALL_COPILOT" = true ]; then
    install_copilot
fi

if [ "$INSTALL_OPENCODE" = true ]; then
    install_opencode
fi

if [ "$INSTALL_GEMINI" = true ]; then
    install_gemini
fi

if [ "$INSTALL_ANTIGRAVITY" = true ]; then
    install_antigravity
fi

print_post_install
