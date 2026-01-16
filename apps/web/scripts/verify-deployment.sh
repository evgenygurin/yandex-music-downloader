#!/bin/bash

# DJ AI Studio - Deployment Verification Script
# Run this after deploying to verify everything works

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 DJ AI Studio - Deployment Verification"
echo "=========================================="
echo ""

# Check if URLs are provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Backend URL required${NC}"
    echo "Usage: ./verify-deployment.sh <BACKEND_URL> [FRONTEND_URL]"
    echo "Example: ./verify-deployment.sh https://api.railway.app https://dj-ai.vercel.app"
    exit 1
fi

BACKEND_URL=$1
FRONTEND_URL=${2:-"http://localhost:3000"}

echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""

# Test Backend
echo "📡 Testing Backend..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health" || echo "000")

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ Backend health check passed${NC}"
else
    echo -e "${RED}✗ Backend health check failed (HTTP $HTTP_STATUS)${NC}"
    exit 1
fi

# Test API Docs
echo "📚 Testing API Documentation..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/docs" || echo "000")

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ API docs accessible${NC}"
else
    echo -e "${YELLOW}⚠ API docs not accessible (HTTP $HTTP_STATUS)${NC}"
fi

# Test CORS (if frontend URL provided)
if [ "$FRONTEND_URL" != "http://localhost:3000" ]; then
    echo ""
    echo "🔐 Testing CORS..."
    CORS_HEADER=$(curl -s -H "Origin: $FRONTEND_URL" -H "Access-Control-Request-Method: GET" -I "$BACKEND_URL/api/v1/library/stats" | grep -i "access-control-allow-origin" || echo "")
    
    if [ -n "$CORS_HEADER" ]; then
        echo -e "${GREEN}✓ CORS configured correctly${NC}"
    else
        echo -e "${RED}✗ CORS not configured - add $FRONTEND_URL to allow_origins${NC}"
    fi
fi

# Test Frontend (if URL provided)
if [ "$FRONTEND_URL" != "http://localhost:3000" ]; then
    echo ""
    echo "🌐 Testing Frontend..."
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" || echo "000")
    
    if [ "$HTTP_STATUS" = "200" ]; then
        echo -e "${GREEN}✓ Frontend accessible${NC}"
    else
        echo -e "${RED}✗ Frontend not accessible (HTTP $HTTP_STATUS)${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}=========================================="
echo "✅ Deployment verification complete!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Open $FRONTEND_URL in your browser"
echo "2. Test uploading a file on /analyze page"
echo "3. Check browser console for any errors"
echo ""
