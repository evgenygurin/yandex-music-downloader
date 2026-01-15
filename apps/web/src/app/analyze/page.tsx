"use client";

import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { tracksApi, type AnalysisResult } from "@/lib/api";

function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${minutes}:${secs.toString().padStart(2, "0")}`;
}

export default function AnalyzePage() {
  const [file, setFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFile = (selectedFile: File) => {
    if (!selectedFile.type.startsWith("audio/")) {
      setError("Please select an audio file");
      return;
    }
    setFile(selectedFile);
    setResult(null);
    setError(null);
  };

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleAnalyze = async () => {
    if (!file) return;

    setAnalyzing(true);
    setError(null);
    setResult(null);

    try {
      const analysisResult = await tracksApi.analyze(file);
      setResult(analysisResult);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Analyze Track</h1>

      {/* Upload Area */}
      <Card>
        <CardContent className="pt-6">
          <div
            className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
              dragActive
                ? "border-primary bg-primary/10"
                : "border-muted-foreground/25 hover:border-muted-foreground/50"
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              type="file"
              id="audio-file"
              className="hidden"
              accept="audio/*"
              onChange={(e) => {
                if (e.target.files?.[0]) {
                  handleFile(e.target.files[0]);
                }
              }}
            />
            <label
              htmlFor="audio-file"
              className="cursor-pointer space-y-4 block"
            >
              <div className="text-4xl">🎵</div>
              <div className="text-lg font-medium">
                {file ? file.name : "Drop audio file here or click to browse"}
              </div>
              <div className="text-sm text-muted-foreground">
                Supports MP3, WAV, FLAC, and other audio formats
              </div>
            </label>
          </div>

          {file && (
            <div className="mt-4 flex justify-center">
              <Button onClick={handleAnalyze} disabled={analyzing} size="lg">
                {analyzing ? "Analyzing..." : "Analyze Track"}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Error */}
      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {result && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                BPM
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold">{result.bpm.toFixed(1)}</div>
              <div className="text-sm text-muted-foreground mt-1">
                Confidence: {(result.bpm_confidence * 100).toFixed(0)}%
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Musical Key
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                <div className="text-4xl font-bold">{result.key}</div>
                <Badge
                  variant={result.is_minor ? "secondary" : "default"}
                  className="text-lg px-3 py-1"
                >
                  {result.camelot}
                </Badge>
              </div>
              <div className="text-sm text-muted-foreground mt-1">
                Confidence: {(result.key_confidence * 100).toFixed(0)}%
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Energy Level
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold">{result.energy}</div>
              <div className="text-sm text-muted-foreground mt-1">
                Scale: 1 (low) - 10 (high)
              </div>
              <div className="mt-2 h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary transition-all"
                  style={{ width: `${result.energy * 10}%` }}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Duration
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold font-mono">
                {formatDuration(result.duration_seconds)}
              </div>
              <div className="text-sm text-muted-foreground mt-1">
                {result.duration_seconds.toFixed(1)} seconds
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Compatible Keys Info */}
      {result && (
        <Card>
          <CardHeader>
            <CardTitle>Harmonic Mixing Guide</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground mb-4">
              This track is in <strong>{result.key}</strong> ({result.camelot}
              ). For smooth harmonic transitions, mix with tracks in these
              compatible keys:
            </p>
            <div className="flex flex-wrap gap-2">
              <CompatibleKeyBadge camelot={result.camelot} label="Same key" />
              <CompatibleKeyBadge
                camelot={getAdjacentCamelot(result.camelot, 1)}
                label="+1"
              />
              <CompatibleKeyBadge
                camelot={getAdjacentCamelot(result.camelot, -1)}
                label="-1"
              />
              <CompatibleKeyBadge
                camelot={getRelativeCamelot(result.camelot)}
                label="Relative"
              />
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function CompatibleKeyBadge({
  camelot,
  label,
}: {
  camelot: string;
  label: string;
}) {
  return (
    <div className="flex items-center gap-2 bg-muted px-3 py-2 rounded-lg">
      <Badge variant={camelot.endsWith("A") ? "secondary" : "default"}>
        {camelot}
      </Badge>
      <span className="text-sm text-muted-foreground">{label}</span>
    </div>
  );
}

function getAdjacentCamelot(camelot: string, delta: number): string {
  const num = parseInt(camelot.slice(0, -1));
  const letter = camelot.slice(-1);
  let newNum = num + delta;
  if (newNum < 1) newNum = 12;
  if (newNum > 12) newNum = 1;
  return `${newNum}${letter}`;
}

function getRelativeCamelot(camelot: string): string {
  const num = camelot.slice(0, -1);
  const letter = camelot.slice(-1);
  return `${num}${letter === "A" ? "B" : "A"}`;
}
