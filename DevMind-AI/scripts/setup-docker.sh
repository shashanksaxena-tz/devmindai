#!/bin/bash
# DevMind Docker Setup - Full Stack
# API server with PostgreSQL, Redis, Qdrant

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
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}DevMind Docker Setup - Full Stack${NC}"
    echo -e "${BLUE}======================================${NC}"
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

    echo "This setup deploys the full DevMind stack:"
    echo "  - API server (FastAPI)"
    echo "  - PostgreSQL (persistence)"
    echo "  - Redis (caching, job queue)"
    echo "  - Qdrant (vector search)"
    echo "  - Dashboard (Streamlit)"
    echo ""
    echo "Required:"
    echo "  - Docker & Docker Compose"
    echo "  - At least one LLM API key"
    echo "  - 4GB RAM minimum"
    echo ""
    echo "Steps:"
    echo ""
    echo -e "${YELLOW}1. Copy environment template:${NC}"
    echo "   cp $PROJECT_DIR/.env.example $PROJECT_DIR/.env"
    echo ""
    echo -e "${YELLOW}2. Edit .env with your API keys:${NC}"
    echo "   # Required: At least one LLM"
    echo "   GOOGLE_API_KEY=your-gemini-key"
    echo "   ANTHROPIC_API_KEY=your-claude-key"
    echo ""
    echo "   # Required: Security"
    echo "   SECRET_KEY=generate-random-32-char-string"
    echo ""
    echo -e "${YELLOW}3. Start services:${NC}"
    echo "   cd $PROJECT_DIR"
    echo "   docker-compose up -d"
    echo ""
    echo -e "${YELLOW}4. Verify:${NC}"
    echo "   curl http://localhost:8000/health"
    echo "   open http://localhost:8000/docs  # API docs"
    echo "   open http://localhost:8501       # Dashboard"
    echo ""
    echo "Common commands:"
    echo "   docker-compose ps          # Check status"
    echo "   docker-compose logs -f api # View logs"
    echo "   docker-compose down        # Stop all"
    echo "   docker-compose down -v     # Stop and remove data"
    echo ""
}

run_interactive() {
    print_header

    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        echo "Please install Docker and try again"
        echo "https://docs.docker.com/get-docker/"
        exit 1
    fi
    print_step "Docker found"

    # Check Docker Compose
    if ! docker compose version &> /dev/null && ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    print_step "Docker Compose found"

    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        echo "Please start Docker and try again"
        exit 1
    fi
    print_step "Docker daemon running"

    # Create .env if not exists
    if [ ! -f "$PROJECT_DIR/.env" ]; then
        cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
        print_step "Created .env from template"
    else
        print_step ".env file exists"
    fi

    # Get API keys
    echo ""
    echo -e "${YELLOW}Configure API keys:${NC}"
    echo ""

    read -p "GOOGLE_API_KEY (Gemini, recommended): " gemini_key
    if [ -n "$gemini_key" ]; then
        sed -i.bak "s|^GOOGLE_API_KEY=.*|GOOGLE_API_KEY=$gemini_key|" "$PROJECT_DIR/.env"
        print_step "Gemini API key set"
    fi

    read -p "ANTHROPIC_API_KEY (Claude, optional): " claude_key
    if [ -n "$claude_key" ]; then
        sed -i.bak "s|^ANTHROPIC_API_KEY=.*|ANTHROPIC_API_KEY=$claude_key|" "$PROJECT_DIR/.env"
        print_step "Claude API key set"
    fi

    # Generate secret key
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | head -c 32 | xxd -p)
    sed -i.bak "s|^SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" "$PROJECT_DIR/.env"
    print_step "Secret key generated"

    # Clean up backup files
    rm -f "$PROJECT_DIR/.env.bak"

    # Start services
    echo ""
    print_info "Starting Docker services..."
    cd "$PROJECT_DIR"
    docker compose up -d

    # Wait for services
    echo ""
    print_info "Waiting for services to be ready..."
    sleep 10

    # Check health
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        print_step "API server is healthy"
    else
        print_error "API server health check failed"
        echo "Check logs: docker compose logs api"
    fi

    echo ""
    print_step "Setup complete!"
    echo ""
    echo "Services running:"
    docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo "Access:"
    echo "  API:       http://localhost:8000"
    echo "  API Docs:  http://localhost:8000/docs"
    echo "  Dashboard: http://localhost:8501"
    echo "  Qdrant:    http://localhost:6333/dashboard"
    echo ""
    echo "Commands:"
    echo "  docker compose logs -f api  # View API logs"
    echo "  docker compose down         # Stop services"
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
