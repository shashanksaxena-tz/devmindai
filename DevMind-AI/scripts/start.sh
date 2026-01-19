#!/bin/bash
set -e

echo "🚀 Starting DevMind AI development environment..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your API keys before continuing."
    exit 1
fi

# Start infrastructure services
echo "🐳 Starting Docker services..."
docker-compose up -d postgres redis qdrant

# Wait for services to be ready
echo "⏳ Waiting for services to be healthy..."
sleep 5

# Run migrations
echo "📊 Running database migrations..."
alembic upgrade head

# Start the API server
echo "🌐 Starting API server..."
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
