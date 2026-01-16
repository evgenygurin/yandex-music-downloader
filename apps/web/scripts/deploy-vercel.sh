#!/bin/bash
# Manual Vercel deployment script

set -e

echo "🚀 DJ AI Studio - Vercel Deployment"
echo "===================================="

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    pnpm add --global vercel@latest
fi

VERCEL_VERSION=$(vercel --version)
echo "✓ Vercel CLI: $VERCEL_VERSION"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Run this script from apps/web directory"
    exit 1
fi

# Environment selection
echo ""
echo "Select deployment environment:"
echo "1) Preview (development)"
echo "2) Production"
read -p "Enter choice [1-2]: " env_choice

case $env_choice in
    1)
        ENVIRONMENT="preview"
        PROD_FLAG=""
        echo "📦 Deploying to PREVIEW..."
        ;;
    2)
        ENVIRONMENT="production"
        PROD_FLAG="--prod"
        echo "🚀 Deploying to PRODUCTION..."
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

# Check environment variables
echo ""
echo "🔧 Checking environment variables..."

if [ -z "$NEXT_PUBLIC_API_URL" ]; then
    echo "⚠️  NEXT_PUBLIC_API_URL not set"
    read -p "Enter API URL (or press Enter to skip): " api_url
    if [ -n "$api_url" ]; then
        export NEXT_PUBLIC_API_URL="$api_url"
        echo "✓ NEXT_PUBLIC_API_URL set to: $api_url"
    fi
else
    echo "✓ NEXT_PUBLIC_API_URL: $NEXT_PUBLIC_API_URL"
fi

# Run pre-deployment checks
echo ""
echo "🔍 Running pre-deployment checks..."
./scripts/check-build.sh || {
    echo "❌ Pre-deployment checks failed"
    exit 1
}

# Deploy
echo ""
echo "🚀 Deploying to Vercel..."
vercel $PROD_FLAG || {
    echo "❌ Deployment failed"
    exit 1
}

echo ""
echo "=================================="
echo "✅ Deployment successful!"
echo ""
echo "Next steps:"
echo "1. Check deployment status: vercel ls"
echo "2. View logs: vercel logs [deployment-url]"
echo "3. Configure domains: vercel domains"
