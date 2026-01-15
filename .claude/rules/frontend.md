---
paths:
  - "apps/web/**/*.tsx"
  - "apps/web/**/*.ts"
  - "apps/web/**/*.css"
---

# Next.js Frontend Rules

## Project Structure

```
apps/web/
├── src/
│   ├── app/                    # App Router pages
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Dashboard
│   │   ├── tracks/page.tsx     # Track library
│   │   ├── sets/page.tsx       # DJ sets
│   │   └── analyze/page.tsx    # Audio analysis
│   ├── components/
│   │   └── ui/                 # shadcn/ui components
│   └── lib/
│       ├── utils.ts            # Helper functions
│       └── api.ts              # API client
├── public/
└── package.json
```

## Technologies

- **Framework:** Next.js 15 (App Router)
- **React:** 19.x
- **Styling:** Tailwind CSS 4 + shadcn/ui
- **State:** React hooks (useState, useEffect)
- **API:** fetch with custom wrapper

## Component Patterns

### Client Components
```tsx
"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

interface TrackListProps {
  initialTracks?: Track[]
}

export function TrackList({ initialTracks = [] }: TrackListProps) {
  const [tracks, setTracks] = useState<Track[]>(initialTracks)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchTracks()
  }, [])

  const fetchTracks = async () => {
    setLoading(true)
    try {
      const response = await fetch("/api/tracks")
      const data = await response.json()
      setTracks(data)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      {tracks.map(track => (
        <TrackCard key={track.id} track={track} />
      ))}
    </div>
  )
}
```

### Server Components (Default)
```tsx
// No "use client" directive - runs on server
import { Suspense } from "react"
import { TrackList } from "@/components/track-list"

export default async function TracksPage() {
  const tracks = await fetchTracks()

  return (
    <main className="container py-8">
      <h1 className="text-3xl font-bold mb-6">Track Library</h1>
      <Suspense fallback={<TrackListSkeleton />}>
        <TrackList initialTracks={tracks} />
      </Suspense>
    </main>
  )
}
```

## Styling with Tailwind

### Layout Classes
```tsx
// Container
<div className="container mx-auto px-4 py-8">

// Flex layouts
<div className="flex items-center justify-between gap-4">
<div className="flex flex-col gap-2">

// Grid layouts
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
```

### Component Styling
```tsx
// Cards
<Card className="p-4 hover:shadow-lg transition-shadow">

// Buttons
<Button variant="default" size="sm">
<Button variant="outline" className="w-full">
<Button variant="destructive">

// Text
<h1 className="text-2xl font-bold tracking-tight">
<p className="text-muted-foreground text-sm">
```

### Conditional Classes
```tsx
import { cn } from "@/lib/utils"

<div className={cn(
  "p-4 rounded-lg border",
  isActive && "border-primary bg-primary/10",
  isDisabled && "opacity-50 cursor-not-allowed"
)}>
```

## shadcn/ui Components

### Available Components
Located in `src/components/ui/`:
- `button.tsx` - Button variants
- `card.tsx` - Card container
- `table.tsx` - Data tables
- `input.tsx` - Form inputs
- `badge.tsx` - Status badges
- `skeleton.tsx` - Loading states

### Usage Pattern
```tsx
import { Button } from "@/components/ui/button"
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export function TrackCard({ track }: { track: Track }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{track.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex gap-2">
          <Badge>{track.bpm} BPM</Badge>
          <Badge variant="outline">{track.key}</Badge>
        </div>
      </CardContent>
    </Card>
  )
}
```

## API Client Pattern

```tsx
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export const libraryApi = {
  async getTracks(filters?: TrackFilters): Promise<Track[]> {
    const params = new URLSearchParams()
    if (filters?.bpm_min) params.set("bpm_min", String(filters.bpm_min))
    if (filters?.bpm_max) params.set("bpm_max", String(filters.bpm_max))
    if (filters?.key) params.set("key", filters.key)

    const response = await fetch(`${API_BASE}/api/v1/tracks?${params}`)
    if (!response.ok) throw new Error("Failed to fetch tracks")
    return response.json()
  },

  async createTrack(data: TrackCreate): Promise<Track> {
    const response = await fetch(`${API_BASE}/api/v1/tracks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    if (!response.ok) throw new Error("Failed to create track")
    return response.json()
  },
}
```

## TypeScript Types

```tsx
// types/track.ts
export interface Track {
  id: string
  title: string
  artists: string[]
  bpm: number | null
  key: string | null
  camelot: string | null
  energy: number | null
  created_at: string
}

export interface TrackFilters {
  bpm_min?: number
  bpm_max?: number
  key?: string
  energy_min?: number
  energy_max?: number
}

export interface TrackCreate {
  title: string
  artists?: string[]
  bpm?: number
  key?: string
}
```

## File Naming

| Type | Convention | Example |
|------|------------|---------|
| Pages | `page.tsx` | `app/tracks/page.tsx` |
| Layouts | `layout.tsx` | `app/layout.tsx` |
| Components | kebab-case | `track-card.tsx` |
| UI Components | kebab-case | `button.tsx` |
| Utilities | kebab-case | `cn.ts`, `api.ts` |
| Types | kebab-case | `track.ts` |
