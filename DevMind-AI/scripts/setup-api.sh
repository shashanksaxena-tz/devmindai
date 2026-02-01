#!/bin/bash
# DevMind API Development Setup
# API server with infrastructure for development

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
    echo -e "${BLUE}DevMind API Development Setup${NC}"
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

    echo "This setup is for API development:"
    echo "  - Python environment with API dependencies"
    echo "  - Infrastructure via Docker (PostgreSQL, Redis, Qdrant)"
    echo "  - Hot reload API server"
    echo ""
    echo "Required:"
    echo "  - Python 3.9+"
    echo "  - Docker (for infrastructure)"
    echo "  - At least one LLM API key"
    echo ""
    echo "Steps:"
    echo ""
    echo -e "${YELLOW}1. Start infrastructure:${NC}"
    echo "   cd $PROJECT_DIR"
    echo "   docker compose up -d postgres redis qdrant"
    echo ""
    echo -e "${YELLOW}2. Create virtual environment:${NC}"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo ""
    echo -e "${YELLOW}3. Install API dependencies:${NC}"
    echo "   pip install -e \".[api,dev]\""
    echo ""
    echo -e "${YELLOW}4. Configure environment:${NC}"
    echo "   cp .env.example .env"
    echo "   # Edit .env with your API keys"
    echo ""
    echo -e "${YELLOW}5. Run database migrations:${NC}"
    echo "   alembic upgrade head"
    echo ""
    echo -e "${YELLOW}6. Start API server:${NC}"
    echo "   uvicorn src.api.main:app --reload --port 8000"
    echo ""
    echo -e "${YELLOW}7. Access:${NC}"
    echo "   http://localhost:8000/docs  # Interactive API docs"
    echo ""
    echo "Environment variables for development:"
    echo "   DATABASE_URL=postgresql+asyncpg://devmind:devmind@localhost:5432/devmind"
    echo "   REDIS_URL=redis://localhost:6379/0"
    echo "   QDRANT_URL=http://localhost:6333"
    echo ""
}

run_interactive() {
    print_header

    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    print_step "Python 3 found"

    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    print_step "Docker found"

    # Start infrastructure
    print_info "Starting infrastructure services..."
    cd "$PROJECT_DIR"
    docker compose up -d postgres redis qdrant
    print_step "Infrastructure started"

    # Create venv
    if [ ! -d "$PROJECT_DIR/venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv "$PROJECT_DIR/venv"
        print_step "Virtual environment created"
    fi

    # Activate venv
    source "$PROJECT_DIR/venv/bin/activate"
    print_step "Virtual environment activated"

    # Install dependencies
    print_info "Installing API dependencies..."
    pip install -q -e "$PROJECT_DIR[api,dev]"
    print_step "Dependencies installed"

    # Create .env
    if [ ! -f "$PROJECT_DIR/.env" ]; then
        cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
        print_step "Created .env from template"
    fi

    # Configure local URLs
    echo ""
    echo -e "${YELLOW}Configuring for local development...${NC}"

    # Update .env for local development
    sed -i.bak 's|postgresql+asyncpg://devmind:devmind@postgres:5432|postgresql+asyncpg://devmind:devmind@localhost:5432|g' "$PROJECT_DIR/.env"
    sed -i.bak 's|redis://redis:6379|redis://localhost:6379|g' "$PROJECT_DIR/.env"
    sed -i.bak 's|http://qdrant:6333|http://localhost:6333|g' "$PROJECT_DIR/.env"
    rm -f "$PROJECT_DIR/.env.bak"
    print_step "Configured local URLs"

    # Get API key
    echo ""
    read -p "GOOGLE_API_KEY (required): " api_key
    if [ -n "$api_key" ]; then
        sed -i.bak "s|^GOOGLE_API_KEY=.*|GOOGLE_API_KEY=$api_key|" "$PROJECT_DIR/.env"
        rm -f "$PROJECT_DIR/.env.bak"
        print_step "API key set"
    else
        print_error "API key required"
        exit 1
    fi

    # Generate secret key
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i.bak "s|^SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" "$PROJECT_DIR/.env"
    rm -f "$PROJECT_DIR/.env.bak"
    print_step "Secret key generated"

    # Wait for database
    print_info "Waiting for PostgreSQL..."
    sleep 5

    # Run migrations
    print_info "Running database migrations..."
    cd "$PROJECT_DIR"
    alembic upgrade head 2>/dev/null || print_info "Migrations not found or already applied"
    print_step "Database ready"

    echo ""
    print_step "Setup complete!"
    echo ""
    echo "Infrastructure running:"
    docker compose ps postgres redis qdrant --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo "To start the API server:"
    echo "  cd $PROJECT_DIR"
    echo "  source venv/bin/activate"
    echo "  uvicorn src.api.main:app --reload"
    echo ""
    echo "Then open: http://localhost:8000/docs"
    echo ""
    echo "To stop infrastructure:"
    echo "  docker compose down"
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
