This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

### Automatic Deployment Setup

1. Go to [Vercel](https://vercel.com) and import the repository
2. Configure the project settings:
   - **Framework Preset**: Next.js
   - **Root Directory**: `apps/web`
3. Click **Deploy**

Vercel will automatically deploy on every push to main and create preview deployments for pull requests.

### Configuration

The `vercel.json` file is pre-configured with:
- Framework detection for Next.js
- pnpm package manager
- Ignore command to skip builds when `apps/web` hasn't changed

### Environment Variables

If your app needs environment variables (e.g., API URL), add them in Vercel Dashboard under Project Settings > Environment Variables.
