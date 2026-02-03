#!/bin/bash
# Start script for Skill Executor Backend API

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Skill Executor Backend API${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found${NC}"
    echo -e "${YELLOW}Creating .env from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env file with your configuration${NC}"
    echo ""
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Default values
PORT=${PORT:-8000}
HOST=${HOST:-0.0.0.0}
SKILLS_DIR=${SKILLS_DIR:-./skills}
DEFAULT_PROVIDER=${DEFAULT_PROVIDER:-openai}

echo -e "${GREEN}Configuration:${NC}"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Skills Dir: $SKILLS_DIR"
echo "  Provider: $DEFAULT_PROVIDER"
echo ""

# Check if skills directory exists
if [ ! -d "$SKILLS_DIR" ]; then
    echo -e "${RED}Error: Skills directory not found: $SKILLS_DIR${NC}"
    echo "Please create it or update SKILLS_DIR in .env"
    exit 1
fi

# Check Python dependencies
echo -e "${GREEN}Checking dependencies...${NC}"
cd backend

if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    pip install -r requirements.txt
fi

# Start server
echo ""
echo -e "${GREEN}Starting server...${NC}"
echo -e "${GREEN}API will be available at: http://$HOST:$PORT${NC}"
echo -e "${GREEN}API docs at: http://$HOST:$PORT/docs${NC}"
echo ""

# Run uvicorn
python3 -m uvicorn main:app \
    --host $HOST \
    --port $PORT \
    --reload \
    --log-level info
