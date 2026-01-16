# Deploying DJ AI Studio to Vercel

## Prerequisites

- [Vercel account](https://vercel.com/signup)
- [Vercel CLI](https://vercel.com/cli) (optional but recommended)
- Deployed FastAPI backend (see backend deployment guide below)

## Quick Deploy

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "feat: prepare for Vercel deployment"
   git push origin main
   ```

2. **Import to Vercel**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Click "Import Project"
   - Select your GitHub repository
   - Vercel will auto-detect Next.js

3. **Configure the project**
   - **Root Directory**: Set to `apps/web`
   - **Framework Preset**: Next.js (auto-detected)
   - **Build Command**: `pnpm build`
   - **Output Directory**: `.next` (auto-detected)
   - **Install Command**: `pnpm install`

4. **Add Environment Variables**
   - Add `NEXT_PUBLIC_API_URL` with your FastAPI backend URL
   - Example: `https://your-fastapi-backend.railway.app`

5. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes for build to complete

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy from the web directory**
   ```bash
   cd apps/web
   vercel
   ```

4. **Follow the prompts**
   - Set up and deploy? **Y**
   - Which scope? Select your account
   - Link to existing project? **N**
   - What's your project's name? `dj-ai-studio-web`
   - In which directory is your code located? `./`
   - Auto-detected settings correct? **Y**

5. **Set environment variables**
   ```bash
   vercel env add NEXT_PUBLIC_API_URL
   # Enter your FastAPI backend URL when prompted
   ```

6. **Deploy to production**
   ```bash
   vercel --prod
   ```

## Environment Variables

Configure these in Vercel Dashboard → Settings → Environment Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | FastAPI backend URL | `https://api.yourdomain.com` |

## Backend Deployment Options

The Next.js app needs a FastAPI backend. Deploy it to one of these platforms:

### Option A: Railway (Recommended)

1. **Install Railway CLI**
   ```bash
   npm i -g @railway/cli
   ```

2. **Login and deploy**
   ```bash
   cd ../../apps/api
   railway login
   railway init
   railway up
   ```

3. **Set environment variables in Railway**
   - `PORT=8000`
   - `DATABASE_URL=sqlite:///data/dj_ai_studio.db`
   - Add any other required variables

4. **Get the public URL**
   - Railway will provide a URL like `https://your-app.railway.app`
   - Use this as `NEXT_PUBLIC_API_URL` in Vercel

### Option B: Render

1. **Create `render.yaml` in project root**
   ```yaml
   services:
     - type: web
       name: dj-ai-api
       env: python
       buildCommand: "cd apps/api && pip install -e ../../packages/core && pip install -r requirements.txt"
       startCommand: "cd apps/api && uvicorn dj_ai_api.main:app --host 0.0.0.0 --port $PORT"
       envVars:
         - key: PYTHON_VERSION
           value: "3.12"
   ```

2. **Connect to Render**
   - Go to [render.com](https://render.com)
   - Create new Web Service from GitHub
   - Use the `render.yaml` config

### Option C: Fly.io

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Create `Dockerfile` for API**
   ```dockerfile
   FROM python:3.12-slim
   
   WORKDIR /app
   
   # Install uv
   RUN pip install uv
   
   # Copy project files
   COPY packages/core packages/core
   COPY apps/api apps/api
   COPY pyproject.toml .
   
   # Install dependencies
   RUN uv pip install --system -e packages/core
   RUN uv pip install --system -r apps/api/requirements.txt
   
   # Expose port
   EXPOSE 8000
   
   # Run API
   CMD ["uvicorn", "dj_ai_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

3. **Deploy**
   ```bash
   fly launch
   fly deploy
   ```

## Custom Domain (Optional)

1. **In Vercel Dashboard**
   - Go to Settings → Domains
   - Add your custom domain
   - Configure DNS as instructed

2. **Update CORS in FastAPI**
   ```python
   # apps/api/dj_ai_api/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "https://yourdomain.com",
           "https://www.yourdomain.com",
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

## Troubleshooting

### Build Fails

**Error: Cannot find module 'pnpm'**
- Vercel should auto-detect pnpm from `package.json`
- If not, add `"packageManager": "pnpm@10.15.0"` to `package.json`

**Error: Build exceeds time limit**
- Check build logs in Vercel dashboard
- Ensure `node_modules` are not committed to git

### Runtime Errors

**Error: API requests fail (CORS)**
- Add your Vercel domain to FastAPI CORS origins
- Ensure `NEXT_PUBLIC_API_URL` is set correctly

**Error: 404 on routes**
- Next.js App Router uses file-based routing
- Check that `src/app/` structure is correct

### Performance Issues

**Slow initial load**
- Enable Edge Runtime for API routes (if applicable)
- Use `output: "standalone"` in `next.config.ts` (already configured)

**Images not loading**
- Check `remotePatterns` in `next.config.ts`
- Ensure image URLs are HTTPS

## Monitoring

1. **Vercel Analytics**
   - Enable in Vercel Dashboard → Analytics
   - View real-time performance metrics

2. **Error Tracking**
   - Integrate Sentry for error monitoring
   - Add `@sentry/nextjs` package

3. **Logs**
   - View build logs: Vercel Dashboard → Deployments → [Deployment] → Build Logs
   - View runtime logs: Vercel Dashboard → Deployments → [Deployment] → Function Logs

## Continuous Deployment

Vercel automatically deploys on git push:

- **Production**: Deployments from `main` branch → `dj-ai-studio.vercel.app`
- **Preview**: Deployments from PRs → `dj-ai-studio-<hash>.vercel.app`

### Disable Auto-Deploy

If you want manual control:
1. Settings → Git → Deploy Hooks → Disable automatic deployments
2. Use `vercel --prod` from CLI to deploy manually

## Security Checklist

- [ ] Environment variables configured (not hardcoded)
- [ ] CORS properly configured in FastAPI
- [ ] API uses HTTPS in production
- [ ] No sensitive data in client-side code
- [ ] Rate limiting enabled on API endpoints

## Next Steps

1. Deploy the FastAPI backend first
2. Get the backend URL
3. Deploy the Next.js frontend with `NEXT_PUBLIC_API_URL` set
4. Test the integration
5. Set up custom domain (optional)
6. Enable monitoring and analytics

---

**Need help?**
- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Railway Documentation](https://docs.railway.app)
