#!/bin/bash
echo "🧪 Testing API endpoints..."

API_BASE="http://localhost:8000"

echo "Testing health endpoint..."
curl -s "$API_BASE/health" | python -m json.tool

echo -e "\nTesting root endpoint..."
curl -s "$API_BASE/" | python -m json.tool

echo -e "\nAPI documentation available at: $API_BASE/docs"
