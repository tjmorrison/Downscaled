#!/bin/bash
echo "🚀 Starting Snowpack Portal Development Environment"

# Start the backend services
echo "Starting database and Redis..."
docker-compose up -d db redis

# Wait for database to be ready
echo "Waiting for database to initialize..."
sleep 10

# Start the backend
echo "Starting FastAPI backend..."
docker-compose up -d backend

# Start Celery workers
echo "Starting Celery workers..."
docker-compose up -d celery-worker celery-beat

echo "✅ Development environment is running!"
echo ""
echo "🌐 API available at: http://localhost:8000"
echo "📊 API docs at: http://localhost:8000/docs"
echo "🗄️  Database at: localhost:5432"
echo "🔴 Redis at: localhost:6379"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
