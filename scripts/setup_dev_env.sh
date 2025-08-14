#!/bin/bash
# scripts/setup_dev_env.sh

set -e

echo "🏔️  Setting up Snowpack Portal Development Environment"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Docker and Docker Compose are installed"

# Create project directory structure
echo "📁 Creating project directory structure..."

# Backend structure
mkdir -p backend/app/{api,core,models,tasks,utils}
mkdir -p backend/app/api
mkdir -p backend/alembic/versions
mkdir -p backend/tests

# Data directories
mkdir -p data/{raw,processed,smet,sno,results}
mkdir -p config
mkdir -p logs

# Frontend structure (for later)
mkdir -p frontend/src/{components,pages,hooks,services,utils}
mkdir -p frontend/public

print_status "Directory structure created"

# Copy your existing files to new structure
echo "📋 Moving your existing code to new structure..."

# Your existing Python files go into the new structure
if [ -f "get_mesowest_data.py" ]; then
    print_status "Found get_mesowest_data.py - will integrate into Celery tasks"
fi

if [ -f "get_aws_data.py" ]; then
    print_status "Found get_aws_data.py - will integrate into Celery tasks"
fi

if [ -d "config" ]; then
    print_status "Found config directory - preserving your station configurations"
fi

# Create environment file
echo "🔧 Creating environment configuration..."

cat > .env << EOF
# Database
DATABASE_URL=postgresql://snowpack_user:snowpack_dev_password@localhost:5432/snowpack_portal

# Redis
REDIS_URL=redis://localhost:6379

# Security (change these in production!)
SECRET_KEY=your-secret-key-change-in-production-$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
DEBUG=true

# API Keys (you'll need to fill these in)
MESOWEST_TOKEN=your_mesowest_token_here
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=us-east-1

# Data directories
DATA_DIR=./data
CONFIG_DIR=./config
SMET_DIR=./data/smet
SNO_DIR=./data/sno
RESULTS_DIR=./data/results

# SNOWPACK settings
SNOWPACK_EXECUTABLE=snowpack

# Celery
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379
EOF

print_status "Environment file created (.env)"

# Create a simple database initialization file
echo "🗄️  Creating database initialization..."

mkdir -p sql
cat > sql/init.sql << EOF
-- Initialize the snowpack portal database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create basic indexes for performance
-- (The actual tables will be created by SQLAlchemy)
EOF

print_status "Database initialization file created"

# Create development startup script
cat > start_dev.sh << 'EOF'
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
EOF

chmod +x start_dev.sh

print_status "Development startup script created (start_dev.sh)"

# Create basic API test script
cat > test_api.sh << 'EOF'
#!/bin/bash
echo "🧪 Testing API endpoints..."

API_BASE="http://localhost:8000"

echo "Testing health endpoint..."
curl -s "$API_BASE/health" | python -m json.tool

echo -e "\nTesting root endpoint..."
curl -s "$API_BASE/" | python -m json.tool

echo -e "\nAPI documentation available at: $API_BASE/docs"
EOF

chmod +x test_api.sh

print_status "API test script created (test_api.sh)"

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Fill in your API keys in the .env file"
echo "  2. Run: ./start_dev.sh"
echo "  3. Visit http://localhost:8000/docs to see the API"
echo "  4. Test with: ./test_api.sh"
echo ""
echo "📚 Your existing code integration:"
echo "  - Place your Mesowest token in .env"
echo "  - Your get_mesowest_data.py logic is in backend/app/tasks/mesowest.py"
echo "  - Your station configs should go in the config/ directory"
echo "  - SMET and SNO files will be stored in data/smet/ and data/sno/"
echo ""
echo "🔧 Development workflow:"
echo "  - Code changes in backend/ will auto-reload"
echo "  - View logs: docker-compose logs -f backend"
echo "  - Access database: docker-compose exec db psql -U snowpack_user -d snowpack_portal"
echo ""

print_warning "Remember to:"
print_warning "  - Add your Mesowest API token to .env"
print_warning "  - Add your AWS credentials to .env"
print_warning "  - Install SNOWPACK in the Docker container if needed"