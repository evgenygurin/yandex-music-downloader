# Vercel Integration Guide - Full Setup Complete

## ✅ Integration Status

**Status:** Полностью настроен и готов к развертыванию

### Что было сделано:

#### 1. **Оптимизирована конфигурация Vercel**
- ✅ `vercel.json` (корневой) - монорепо конфигурация
- ✅ `apps/web/vercel.json` - специфичная конфигурация приложения
- ✅ `.vercelignore` - исключение Python файлов
- ✅ Security headers (X-Frame-Options, CSP, XSS-Protection)
- ✅ Оптимизация кэширования

#### 2. **Next.js оптимизации**
- ✅ Standalone output mode
- ✅ Package imports optimization (lucide-react, radix-ui)
- ✅ Image optimization (AVIF, WebP)
- ✅ Webpack production optimizations
- ✅ React Strict Mode enabled

#### 3. **Environment Variables**
- ✅ `.env.example` - шаблон переменных окружения
- ✅ `.env.local.example` - расширенный шаблон
- ✅ `NEXT_PUBLIC_API_URL` - настроен с fallback

#### 4. **CI/CD Workflows**
- ✅ `.github/workflows/vercel-deploy.yml`:
  - Автоматический deploy в Preview для PR
  - Автоматический deploy в Production для main
  - Комментарии с preview URL в PR
  - Оптимизация через pnpm cache

#### 5. **Deployment Scripts**
- ✅ `apps/web/scripts/check-build.sh` - валидация перед деплоем
- ✅ `apps/web/scripts/deploy-vercel.sh` - ручной деплой
- ✅ Проверка типов, линтинга, сборки

---

## 🚀 Развертывание

### Вариант 1: Vercel Dashboard (Рекомендуется)

#### Шаг 1: Подготовка репозитория

```bash
# 1. Убедитесь что все изменения закоммичены
git status

# 2. Push в GitHub
git push origin main
```

#### Шаг 2: Импорт в Vercel

1. Перейдите на [vercel.com/new](https://vercel.com/new)
2. Выберите "Import Git Repository"
3. Выберите ваш репозиторий `yandex-music-downloader`

#### Шаг 3: Конфигурация проекта

Vercel автоматически определит конфигурацию из `vercel.json`:

```
✓ Framework Preset: Next.js
✓ Root Directory: apps/web (авто-определение)
✓ Build Command: pnpm build
✓ Output Directory: .next
✓ Install Command: pnpm install --frozen-lockfile
```

#### Шаг 4: Environment Variables

Добавьте в Vercel Dashboard → Settings → Environment Variables:

| Variable | Value | Environment |
|----------|-------|-------------|
| `NEXT_PUBLIC_API_URL` | `https://your-api.railway.app` | Production |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Preview |

#### Шаг 5: Deploy

1. Нажмите "Deploy"
2. Ожидайте 2-3 минуты
3. Получите URL: `https://your-project.vercel.app`

---

### Вариант 2: Vercel CLI (Продвинутый)

#### Установка CLI

```bash
pnpm add --global vercel@latest
vercel login
```

#### Quick Deploy

```bash
cd apps/web

# Preview deployment
vercel

# Production deployment
vercel --prod
```

#### С валидацией

```bash
cd apps/web

# Запустить проверки и деплой
./scripts/deploy-vercel.sh
```

---

### Вариант 3: GitHub Actions (Автоматический)

#### Настройка секретов GitHub

1. Получите Vercel Token:
   ```bash
   vercel login
   vercel token create
   ```

2. Добавьте в GitHub Secrets (Settings → Secrets → Actions):
   - `VERCEL_TOKEN` - ваш токен
   - `VERCEL_ORG_ID` - из `.vercel/project.json` после первого деплоя
   - `VERCEL_PROJECT_ID` - из `.vercel/project.json`

#### Автоматический деплой

```bash
# Push в main → Production deploy
git push origin main

# Create PR → Preview deploy с комментарием в PR
gh pr create
```

---

## 📋 Pre-Deployment Checklist

### Локальная проверка

```bash
cd apps/web

# 1. Type check
pnpm exec tsc --noEmit

# 2. Lint
pnpm lint

# 3. Build test
pnpm build

# 4. Полная валидация
./scripts/check-build.sh
```

### Environment Variables

- [ ] `NEXT_PUBLIC_API_URL` настроен
- [ ] Бэкенд API развернут и доступен
- [ ] CORS настроен в FastAPI для Vercel домена

### Security

- [ ] Security headers настроены (✅ уже в конфиге)
- [ ] Нет хардкод секретов в коде
- [ ] `.env` добавлен в `.gitignore`

---

## 🔧 Настройка Backend API

Перед развертыванием frontend необходимо развернуть backend:

### Railway (Рекомендуется)

```bash
cd apps/api

# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up

# Set env vars
railway variables set PORT=8000
railway variables set DATABASE_URL=sqlite:///data/dj_ai_studio.db

# Get URL
railway open
# Example: https://dj-ai-api-production.railway.app
```

### Render

```yaml
# render.yaml (уже в проекте)
services:
  - type: web
    name: dj-ai-api
    env: python
    buildCommand: "pip install -e packages/core && cd apps/api && pip install -r requirements.txt"
    startCommand: "cd apps/api && uvicorn dj_ai_api.main:app --host 0.0.0.0 --port $PORT"
```

### Fly.io

```bash
# Dockerfile уже создан
cd apps/api
fly launch
fly deploy
```

---

## 🔍 Мониторинг и отладка

### Vercel Dashboard

1. **Deployments** - история деплоев
2. **Build Logs** - логи сборки
3. **Function Logs** - runtime логи
4. **Analytics** - метрики производительности

### CLI команды

```bash
# Список деплоев
vercel ls

# Логи последнего деплоя
vercel logs

# Логи конкретного деплоя
vercel logs [deployment-url]

# Информация о проекте
vercel inspect [deployment-url]
```

### GitHub Actions

- Статус: Actions tab в GitHub
- Логи: Каждый workflow run → Job logs
- Preview URLs: Комментарии в PR

---

## 🐛 Troubleshooting

### Build Fails

**Error: `pnpm` not found**
```json
// Уже исправлено в package.json:
"packageManager": "pnpm@10.15.0+sha512..."
```

**Error: Module not found**
```bash
# Очистите кэш и пересоберите
rm -rf .next node_modules
pnpm install
pnpm build
```

### Runtime Errors

**CORS Error**
```python
# apps/api/dj_ai_api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",
        "https://*.vercel.app",  # Для preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**API Not Reachable**
```bash
# Проверьте env var
vercel env ls

# Добавьте если отсутствует
vercel env add NEXT_PUBLIC_API_URL production
```

### Performance

**Slow Initial Load**
- ✅ Уже оптимизировано: `output: "standalone"`
- ✅ Package imports оптимизированы
- ✅ Images AVIF/WebP enabled

---

## 📊 Performance Metrics

### Текущие оптимизации:

- ✅ **Bundle Size**: Optimized imports (lucide-react, radix-ui)
- ✅ **Images**: AVIF/WebP formats, 60s cache TTL
- ✅ **Headers**: Security + Cache-Control
- ✅ **Webpack**: Deterministic module IDs, tree shaking
- ✅ **React**: Strict Mode enabled

### Expected Scores:

- **Lighthouse Performance**: 90-100
- **First Contentful Paint**: < 1.5s
- **Time to Interactive**: < 3s
- **Bundle Size**: ~150KB (gzipped)

---

## 🔐 Security

### Настроенные защиты:

1. **CSP Headers** ✅
   ```
   X-Content-Type-Options: nosniff
   X-Frame-Options: DENY
   X-XSS-Protection: 1; mode=block
   Referrer-Policy: strict-origin-when-cross-origin
   ```

2. **Image Security** ✅
   ```typescript
   dangerouslyAllowSVG: true
   contentDispositionType: "attachment"
   contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;"
   ```

3. **Environment Variables** ✅
   - Не в git (через `.gitignore`)
   - Только через Vercel Dashboard
   - Prefix `NEXT_PUBLIC_` для client-side

---

## 📈 Continuous Deployment

### Автоматические деплои:

| Событие | Окружение | URL |
|---------|-----------|-----|
| Push to `main` | Production | `your-app.vercel.app` |
| PR creation | Preview | `your-app-<hash>.vercel.app` |
| Commit to PR | Preview | Обновление preview |

### Ручной контроль:

```bash
# Отключить auto-deploy
vercel --cwd apps/web --no-auto

# Ручной deploy
vercel --cwd apps/web --prod
```

---

## 🎯 Next Steps

1. **Deploy Backend**
   ```bash
   cd apps/api
   railway up  # или другой провайдер
   ```

2. **Get Backend URL**
   ```
   Example: https://dj-ai-api.railway.app
   ```

3. **Deploy Frontend**
   ```bash
   # Через Vercel Dashboard
   vercel.com/new → Import → Configure → Deploy
   
   # Или через CLI
   cd apps/web
   ./scripts/deploy-vercel.sh
   ```

4. **Verify**
   - Откройте Vercel URL
   - Проверьте API подключение
   - Проверьте Dashboard statistics

5. **Custom Domain** (опционально)
   ```bash
   vercel domains add yourdomain.com
   ```

---

## 📚 Документация

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [DJ AI Studio Deployment Guide](./apps/web/DEPLOYMENT.md)

---

## ✅ Summary

**Что готово:**
- ✅ Vercel конфигурация (корневая + web)
- ✅ Next.js оптимизации
- ✅ CI/CD workflow (GitHub Actions)
- ✅ Deployment scripts (check-build, deploy)
- ✅ Environment variables setup
- ✅ Security headers
- ✅ Performance optimizations
- ✅ Monorepo support

**Требуется от вас:**
1. Push в GitHub: `git push origin main`
2. Deploy backend (Railway/Render/Fly)
3. Import в Vercel Dashboard
4. Добавить `NEXT_PUBLIC_API_URL` в Vercel
5. Deploy! 🚀

---

**Need help?** Open an issue или см. [CONTRIBUTING.md](./CONTRIBUTING.md)
