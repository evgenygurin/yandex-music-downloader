# DJ AI Studio - Web Frontend

Modern Next.js 15 web application for DJ library management, audio analysis, and AI-powered set building.

## Features

- 🎵 **Track Library** - Search, filter, and manage your music collection
- 📊 **Audio Analysis** - BPM, key detection, energy levels
- 🎚️ **DJ Sets** - Create and manage sets with harmonic mixing
- 🎨 **Modern UI** - Built with Next.js 15, React 19, Tailwind CSS 4
- 🌙 **Dark Mode** - Beautiful dark theme optimized for DJs
- 📱 **Responsive** - Works on desktop, tablet, and mobile

## Quick Start

### Local Development

```bash
# Install dependencies
pnpm install

# Set up environment
cp .env.example .env.local
# Edit .env.local and set NEXT_PUBLIC_API_URL

# Start development server
pnpm dev

# Open http://localhost:3000
```

### Build for Production

```bash
# Build
pnpm build

# Start production server
pnpm start

# Preview on http://localhost:3000
```

## Deployment

### Deploy to Vercel (Recommended)

**Quick Deploy:**

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/llistochek/yandex-music-downloader&project-name=dj-ai-studio&repository-name=dj-ai-studio&root-directory=apps/web&env=NEXT_PUBLIC_API_URL&envDescription=FastAPI%20backend%20URL)

**Manual Setup:**

1. Push code to GitHub
2. Import project on [vercel.com](https://vercel.com/new)
3. Set root directory: `apps/web`
4. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = Your FastAPI backend URL
5. Deploy!

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions and backend deployment options.

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NEXT_PUBLIC_API_URL` | FastAPI backend URL | Yes | `http://localhost:8000` |

## Project Structure

```
apps/web/
├── src/
│   ├── app/              # Next.js App Router pages
│   │   ├── page.tsx      # Home page
│   │   ├── tracks/       # Track library
│   │   ├── sets/         # DJ sets
│   │   └── analyze/      # Audio analysis
│   ├── components/       # React components
│   │   └── ui/           # shadcn/ui components
│   └── lib/              # Utilities
│       ├── api.ts        # API client
│       └── utils.ts      # Helper functions
├── public/               # Static assets
├── next.config.ts        # Next.js config
└── vercel.json           # Vercel deployment config
```

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **React**: 19.2.3
- **Styling**: Tailwind CSS 4
- **UI Components**: shadcn/ui (Radix UI primitives)
- **Icons**: Lucide React
- **Package Manager**: pnpm 10.15.0
- **TypeScript**: 5.x

## Scripts

```bash
# Development
pnpm dev          # Start dev server (port 3000)

# Build
pnpm build        # Build for production
pnpm start        # Start production server

# Linting
pnpm lint         # Run ESLint

# Deployment verification
./scripts/verify-deployment.sh <BACKEND_URL> <FRONTEND_URL>
```

## Troubleshooting

### CORS Errors

Add your frontend URL to FastAPI CORS origins:

```python
# apps/api/dj_ai_api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-frontend.vercel.app",
    ],
)
```

### Build Errors

- Check `tsconfig.json` paths configuration
- Ensure imports use `@/` alias
- Verify `package.json` has `packageManager` field

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Vercel Deployment Guide](../../VERCEL_DEPLOYMENT.md)
- [Project Contributing Guide](../../CONTRIBUTING.md)
