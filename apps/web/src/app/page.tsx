"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { libraryApi, type LibraryStats } from "@/lib/api";

export default function Home() {
  const [stats, setStats] = useState<LibraryStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    libraryApi
      .stats()
      .then(setStats)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Welcome to DJ AI Studio</h1>
        <Card className="border-yellow-500/50 bg-yellow-500/10">
          <CardContent className="pt-6">
            <p className="text-yellow-500">
              Backend not available. Start the API server to see library stats.
            </p>
            <code className="block mt-2 text-sm text-muted-foreground">
              uv run uvicorn dj_ai_studio.api:app --reload
            </code>
          </CardContent>
        </Card>
        <div className="grid gap-4 md:grid-cols-3">
          <Link href="/tracks">
            <Card className="hover:bg-accent transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>Tracks</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Browse and search your music library
                </p>
              </CardContent>
            </Card>
          </Link>
          <Link href="/sets">
            <Card className="hover:bg-accent transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>Sets</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Create and manage DJ sets
                </p>
              </CardContent>
            </Card>
          </Link>
          <Link href="/analyze">
            <Card className="hover:bg-accent transition-colors cursor-pointer">
              <CardHeader>
                <CardTitle>Analyze</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Analyze tracks for BPM, key, and energy
                </p>
              </CardContent>
            </Card>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <Button asChild>
          <Link href="/analyze">Analyze Track</Link>
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Tracks
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats?.total_tracks ?? 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Analyzed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {stats?.analyzed_tracks ?? 0}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              DJ Sets
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats?.total_sets ?? 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              BPM Range
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {stats?.bpm_range
                ? `${stats.bpm_range[0]}-${stats.bpm_range[1]}`
                : "-"}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Link href="/tracks">
          <Card className="hover:bg-accent transition-colors cursor-pointer h-full">
            <CardHeader>
              <CardTitle>Browse Tracks</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Search and filter your music library by BPM, key, energy, and
                more.
              </p>
            </CardContent>
          </Card>
        </Link>

        <Link href="/sets">
          <Card className="hover:bg-accent transition-colors cursor-pointer h-full">
            <CardHeader>
              <CardTitle>Manage Sets</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Create DJ sets with harmonic mixing suggestions and energy flow.
              </p>
            </CardContent>
          </Card>
        </Link>

        <Link href="/analyze">
          <Card className="hover:bg-accent transition-colors cursor-pointer h-full">
            <CardHeader>
              <CardTitle>Analyze Audio</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Upload tracks to detect BPM, musical key, and energy level.
              </p>
            </CardContent>
          </Card>
        </Link>
      </div>
    </div>
  );
}
