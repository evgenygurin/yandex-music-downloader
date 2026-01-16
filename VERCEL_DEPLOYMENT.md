# 🚀 Complete Vercel Deployment Guide

This guide covers deploying the entire DJ AI Studio stack:
- **Frontend**: Next.js web app → Vercel
- **Backend**: FastAPI → Railway/Render/Fly.io

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Deploy Backend (FastAPI)](#step-1-deploy-backend-fastapi)
3. [Step 2: Deploy Frontend (Next.js)](#step-2-deploy-frontend-nextjs)
4. [Step 3: Connect Frontend to Backend](#step-3-connect-frontend-to-backend)
5. [Step 4: Verify Deployment](#step-4-verify-deployment)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- [x] GitHub account
- [x] Vercel account (sign up at [vercel.com](https://vercel.com))
- [x] Railway/Render account (choose one for backend)
- [x] Code pushed to GitHub repository

---

## Step 1: Deploy Backend (FastAPI)

Choose one of these platforms for the backend:

### Option A: Railway (Recommended - Easiest)

**Why Railway?**
- Free tier with $5/month credit
- Automatic HTTPS
- Built-in PostgreSQL/Redis if needed
- Simple deployment

**Deploy Steps:**

1. **Go to [railway.app](https://railway.app)**
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `yandex-music-downloader` repository
4. Configure the service:
   - **Root Directory**: Leave empty (Railway will detect)
   - **Start Command**: 
     ```bash
     cd apps/api && pip install -e ../../packages/core && pip install -r requirements.txt && uvicorn dj_ai_api.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Environment Variables**:
     ```
     PORT=8000
     PYTHONPATH=/app
     DATABASE_URL=sqlite:////data/dj_ai_studio.db
     ```

5. **Generate Domain**
   - Settings → Generate Domain
   - You'll get: `https://your-app.up.railway.app`
   - **Save this URL** - you'll need it for Vercel

6. **Add persistent storage (optional)**
   - Volumes → New Volume → `/data`
   - Ensures database persists across deployments

### Option B: Render

**Why Render?**
- Generous free tier
- Automatic SSL
- Native Python support

**Deploy Steps:**

1. **Go to [render.com](https://render.com)**
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `dj-ai-api`
   - **Root Directory**: Leave empty
   - **Environment**: Python 3
   - **Build Command**:
     ```bash
     cd apps/api && pip install -e ../../packages/core && pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     cd apps/api && uvicorn dj_ai_api.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Environment Variables**:
     ```
     PYTHON_VERSION=3.12
     DATABASE_URL=sqlite:////opt/render/project/src/dj_ai_studio.db
     ```

5. **Create the service**
   - Click "Create Web Service"
   - You'll get: `https://dj-ai-api.onrender.com`
   - **Save this URL**

### Option C: Fly.io

**Why Fly.io?**
- Excellent global performance
- True edge deployment
- Free tier available

**Deploy Steps:**

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Create `Dockerfile` in project root**
   ```dockerfile
   FROM python:3.12-slim

   WORKDIR /app

   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       gcc \
       && rm -rf /var/lib/apt/lists/*

   # Copy project files
   COPY packages/core packages/core
   COPY apps/api apps/api
   COPY pyproject.toml .
   COPY uv.lock .

   # Install uv
   RUN pip install uv

   # Install dependencies
   RUN uv pip install --system -e packages/core
   RUN cd apps/api && uv pip install --system -r requirements.txt

   # Expose port
   EXPOSE 8000

   # Run API
   CMD ["uvicorn", "dj_ai_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

3. **Login and launch**
   ```bash
   fly auth login
   fly launch --name dj-ai-api
   ```

4. **Follow prompts**
   - Choose region closest to your users
   - No PostgreSQL needed (using SQLite)
   - Yes to deploy now

5. **Get the URL**
   ```bash
   fly status
   # URL will be: https://dj-ai-api.fly.dev
   ```

---

## Step 2: Deploy Frontend (Next.js)

### Via Vercel Dashboard (Recommended)

1. **Go to [vercel.com/new](https://vercel.com/new)**

2. **Import Git Repository**
   - Click "Import Project"
   - Select your GitHub repository
   - Authorize Vercel to access the repo

3. **Configure Build Settings**
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `apps/web`
   - **Build Command**: `pnpm build`
   - **Output Directory**: `.next` (default)
   - **Install Command**: `pnpm install`

4. **Add Environment Variable**
   - Click "Environment Variables"
   - Add:
     ```
     NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
     ```
   - Replace with your actual backend URL from Step 1

5. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes
   - You'll get: `https://dj-ai-studio.vercel.app`

### Via Vercel CLI (Alternative)

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy from web directory
cd apps/web
vercel

# Set environment variable
vercel env add NEXT_PUBLIC_API_URL production
# Paste your backend URL when prompted

# Deploy to production
vercel --prod
```

---

## Step 3: Connect Frontend to Backend

### Update CORS in FastAPI

1. **Edit `apps/api/dj_ai_api/main.py`**

2. **Add your Vercel domain to CORS origins**
   ```python
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "http://localhost:3000",  # Local development
           "https://dj-ai-studio.vercel.app",  # Your Vercel domain
           "https://dj-ai-studio-*.vercel.app",  # Preview deployments
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Commit and push**
   ```bash
   git add apps/api/dj_ai_api/main.py
   git commit -m "feat: add Vercel domain to CORS"
   git push origin main
   ```

4. **Backend will auto-redeploy** (Railway/Render/Fly.io watch your repo)

---

## Step 4: Verify Deployment

### Test Backend

```bash
# Health check
curl https://your-backend-url.railway.app/health

# API docs
open https://your-backend-url.railway.app/docs
```

### Test Frontend

1. **Open your Vercel URL**: `https://dj-ai-studio.vercel.app`
2. **Check browser console** (F12) - no CORS errors
3. **Test a feature**:
   - Go to "Tracks" page
   - Should load (may be empty if no data)
   - Upload a file to "Analyze" page

### Test Integration

1. **Analyze a track**:
   - Go to `/analyze`
   - Upload an audio file
   - Should return BPM, key, energy

2. **Check network tab**:
   - F12 → Network
   - API calls should go to your backend URL
   - Status: 200 OK

---

## Troubleshooting

### Issue: CORS Error

**Symptom:**
```
Access to fetch at 'https://your-api.railway.app' from origin 'https://dj-ai-studio.vercel.app' 
has been blocked by CORS policy
```

**Solution:**
1. Add Vercel domain to `allow_origins` in `main.py`
2. Redeploy backend
3. Clear browser cache

### Issue: API Requests Fail (Network Error)

**Check:**
1. **Backend is running**:
   ```bash
   curl https://your-backend-url.railway.app/health
   ```
2. **Environment variable set correctly**:
   - Vercel Dashboard → Settings → Environment Variables
   - `NEXT_PUBLIC_API_URL` matches backend URL

3. **Backend URL uses HTTPS** (not HTTP)

### Issue: Build Fails on Vercel

**Error: Cannot find module 'pnpm'**

**Solution:**
- Ensure `packageManager` field exists in `apps/web/package.json`:
  ```json
  "packageManager": "pnpm@10.15.0"
  ```

**Error: Module not found '@/lib/utils'**

**Solution:**
- File already created: `src/lib/utils.ts`
- If still fails, check `tsconfig.json`:
  ```json
  {
    "compilerOptions": {
      "paths": {
        "@/*": ["./src/*"]
      }
    }
  }
  ```

### Issue: Database Not Persisting (Railway)

**Solution:**
1. Railway → Volumes → Create Volume
2. Mount to `/data`
3. Update `DATABASE_URL` to use volume path:
   ```
   sqlite:////data/dj_ai_studio.db
   ```

### Issue: 404 on Routes

**Check:**
1. Next.js file structure correct (`src/app/tracks/page.tsx`)
2. No trailing slashes in URLs
3. Vercel deployment logs show all routes built

---

## Performance Optimization

### Frontend (Vercel)

1. **Enable Edge Runtime** (for API routes if you add them):
   ```typescript
   // src/app/api/example/route.ts
   export const runtime = 'edge'
   ```

2. **Add caching headers**:
   ```typescript
   // next.config.ts
   async headers() {
     return [
       {
         source: '/api/:path*',
         headers: [
           { key: 'Cache-Control', value: 'no-store' },
         ],
       },
     ]
   }
   ```

3. **Enable Vercel Analytics**:
   - Dashboard → Analytics → Enable
   - Track Core Web Vitals

### Backend (Railway/Render)

1. **Add health check**:
   ```python
   @app.get("/health")
   async def health_check():
       return {"status": "healthy"}
   ```

2. **Enable compression**:
   ```python
   from fastapi.middleware.gzip import GZipMiddleware
   app.add_middleware(GZipMiddleware, minimum_size=1000)
   ```

3. **Add Redis cache** (Railway):
   - Add Redis plugin
   - Cache expensive queries

---

## Custom Domain (Optional)

### Frontend Domain (Vercel)

1. **Vercel Dashboard → Settings → Domains**
2. Add `yourdomain.com`
3. Configure DNS:
   - Type: `CNAME`
   - Name: `@` or `www`
   - Value: `cname.vercel-dns.com`

### Backend Domain (Railway)

1. **Railway → Settings → Custom Domain**
2. Add `api.yourdomain.com`
3. Configure DNS:
   - Type: `CNAME`
   - Name: `api`
   - Value: (Railway provides)

### Update Environment Variables

After adding custom domains:

**Vercel:**
```
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

**FastAPI CORS:**
```python
allow_origins=[
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
```

---

## Continuous Deployment

### Automatic Deployments

Both Vercel and Railway/Render watch your GitHub repo:

- **Push to `main`** → Production deployment
- **Pull Request** → Preview deployment (Vercel)

### Manual Control

**Disable auto-deploy (Vercel):**
```bash
vercel git disconnect
```

**Deploy manually:**
```bash
vercel --prod
```

---

## Monitoring & Logs

### Vercel

- **Build logs**: Deployments → [deployment] → Build Logs
- **Runtime logs**: Deployments → [deployment] → Function Logs
- **Analytics**: Dashboard → Analytics

### Railway

- **Logs**: Service → Logs (live tail)
- **Metrics**: Service → Metrics (CPU, memory, requests)

### Render

- **Logs**: Service → Logs
- **Metrics**: Dashboard (requests, errors)

---

## Security Checklist

- [ ] Environment variables configured (not hardcoded)
- [ ] CORS properly configured
- [ ] API uses HTTPS in production
- [ ] No sensitive data in frontend code
- [ ] Rate limiting enabled (if needed)
- [ ] Database backed up (if using persistent data)

---

## Cost Estimates

### Free Tier Limits

| Service | Free Tier | Paid Plans Start At |
|---------|-----------|---------------------|
| **Vercel** | 100 GB bandwidth, unlimited sites | $20/month (Pro) |
| **Railway** | $5 credit/month | $5/month (usage-based) |
| **Render** | 750 hours/month | $7/month (Starter) |
| **Fly.io** | 3 shared VMs, 3GB storage | Pay as you go |

**Recommendation for hobby projects:**
- Vercel Free (frontend) + Railway Free (backend) = $0/month
- Should handle low-medium traffic

---

## Next Steps

1. ✅ Deploy backend → Get URL
2. ✅ Deploy frontend → Set `NEXT_PUBLIC_API_URL`
3. ✅ Update CORS → Test integration
4. 📊 Add monitoring (Sentry, LogRocket)
5. 🎨 Set up custom domain (optional)
6. 📈 Optimize performance (caching, compression)

---

## Resources

- [Vercel Docs](https://vercel.com/docs)
- [Railway Docs](https://docs.railway.app)
- [Render Docs](https://render.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)

---

**Need help?** Open an issue on GitHub or check the troubleshooting section above.

**Happy deploying! 🚀**
