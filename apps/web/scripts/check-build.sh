#!/bin/bash
# Build validation script for Vercel deployment

set -e

echo "🔍 Vercel Build Validation Script"
echo "=================================="

# Check Node.js version
NODE_VERSION=$(node -v)
echo "✓ Node.js version: $NODE_VERSION"

# Check pnpm version
PNPM_VERSION=$(pnpm -v)
echo "✓ pnpm version: $PNPM_VERSION"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Run this script from apps/web directory"
    exit 1
fi

echo "✓ package.json found"

# Check environment variables
if [ -z "$NEXT_PUBLIC_API_URL" ]; then
    echo "⚠️  Warning: NEXT_PUBLIC_API_URL not set. Using default: http://localhost:8000"
else
    echo "✓ NEXT_PUBLIC_API_URL: $NEXT_PUBLIC_API_URL"
fi

# Check lockfile
if [ ! -f "pnpm-lock.yaml" ]; then
    echo "❌ Error: pnpm-lock.yaml not found"
    exit 1
fi

echo "✓ pnpm-lock.yaml found"

# Run type checking
echo ""
echo "🔧 Running type check..."
pnpm exec tsc --noEmit || {
    echo "❌ Type check failed"
    exit 1
}
echo "✓ Type check passed"

# Run linting
echo ""
echo "🔧 Running linter..."
pnpm lint || {
    echo "❌ Linting failed"
    exit 1
}
echo "✓ Linting passed"

# Test build
echo ""
echo "🏗️  Testing production build..."
pnpm build || {
    echo "❌ Build failed"
    exit 1
}
echo "✓ Build succeeded"

# Check output directory
if [ ! -d ".next" ]; then
    echo "❌ Error: .next directory not created"
    exit 1
fi

echo "✓ .next directory exists"

# Check standalone output
if [ ! -d ".next/standalone" ]; then
    echo "⚠️  Warning: .next/standalone directory not found (may be normal for Vercel)"
else
    echo "✓ Standalone output created"
fi

echo ""
echo "=================================="
echo "✅ All checks passed! Ready for Vercel deployment"
echo ""
echo "Next steps:"
echo "1. Push to GitHub: git push origin main"
echo "2. Import to Vercel: https://vercel.com/new"
echo "3. Set environment variable: NEXT_PUBLIC_API_URL"
echo "4. Deploy!"
