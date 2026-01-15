"use client";

import { useCallback, useEffect, useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { tracksApi, type Track, type TrackFilters } from "@/lib/api";

const CAMELOT_KEYS = [
  "1A", "1B", "2A", "2B", "3A", "3B", "4A", "4B",
  "5A", "5B", "6A", "6B", "7A", "7B", "8A", "8B",
  "9A", "9B", "10A", "10B", "11A", "11B", "12A", "12B",
];

function formatDuration(ms: number): string {
  const minutes = Math.floor(ms / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

function EnergyBadge({ energy }: { energy: number }) {
  const colors: Record<number, string> = {
    1: "bg-blue-900",
    2: "bg-blue-800",
    3: "bg-blue-700",
    4: "bg-green-700",
    5: "bg-green-600",
    6: "bg-yellow-600",
    7: "bg-orange-600",
    8: "bg-orange-700",
    9: "bg-red-600",
    10: "bg-red-700",
  };
  return (
    <Badge className={`${colors[energy] || "bg-gray-600"} text-white`}>
      {energy}
    </Badge>
  );
}

function CamelotBadge({ camelot }: { camelot: string }) {
  const isMinor = camelot.endsWith("A");
  return (
    <Badge variant={isMinor ? "secondary" : "default"}>
      {camelot}
    </Badge>
  );
}

export default function TracksPage() {
  const [tracks, setTracks] = useState<Track[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);

  // Filters
  const [query, setQuery] = useState("");
  const [bpmMin, setBpmMin] = useState("");
  const [bpmMax, setBpmMax] = useState("");
  const [camelot, setCamelot] = useState("");
  const [energyMin, setEnergyMin] = useState("");
  const [energyMax, setEnergyMax] = useState("");

  const loadTracks = useCallback(async () => {
    setLoading(true);
    setError(null);

    const filters: TrackFilters = {};
    if (query) filters.query = query;
    if (bpmMin) filters.bpm_min = parseFloat(bpmMin);
    if (bpmMax) filters.bpm_max = parseFloat(bpmMax);
    if (camelot) filters.camelot = camelot;
    if (energyMin) filters.energy_min = parseInt(energyMin);
    if (energyMax) filters.energy_max = parseInt(energyMax);

    try {
      const response = await tracksApi.list(filters, page, 20);
      setTracks(response.items);
      setTotal(response.total);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load tracks");
    } finally {
      setLoading(false);
    }
  }, [query, bpmMin, bpmMax, camelot, energyMin, energyMax, page]);

  useEffect(() => {
    loadTracks();
  }, [loadTracks]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadTracks();
  };

  const clearFilters = () => {
    setQuery("");
    setBpmMin("");
    setBpmMax("");
    setCamelot("");
    setEnergyMin("");
    setEnergyMax("");
    setPage(1);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Tracks</h1>
        <div className="text-muted-foreground">
          {total} track{total !== 1 ? "s" : ""}
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="grid gap-4 md:grid-cols-6">
              <div className="md:col-span-2">
                <Input
                  placeholder="Search by title or artist..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
              </div>

              <div className="flex gap-2">
                <Input
                  type="number"
                  placeholder="BPM min"
                  value={bpmMin}
                  onChange={(e) => setBpmMin(e.target.value)}
                  className="w-24"
                />
                <Input
                  type="number"
                  placeholder="BPM max"
                  value={bpmMax}
                  onChange={(e) => setBpmMax(e.target.value)}
                  className="w-24"
                />
              </div>

              <Select value={camelot} onValueChange={setCamelot}>
                <SelectTrigger>
                  <SelectValue placeholder="Camelot" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Any key</SelectItem>
                  {CAMELOT_KEYS.map((key) => (
                    <SelectItem key={key} value={key}>
                      {key}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <div className="flex gap-2">
                <Input
                  type="number"
                  placeholder="Energy min"
                  value={energyMin}
                  onChange={(e) => setEnergyMin(e.target.value)}
                  min="1"
                  max="10"
                  className="w-24"
                />
                <Input
                  type="number"
                  placeholder="Energy max"
                  value={energyMax}
                  onChange={(e) => setEnergyMax(e.target.value)}
                  min="1"
                  max="10"
                  className="w-24"
                />
              </div>

              <div className="flex gap-2">
                <Button type="submit">Search</Button>
                <Button type="button" variant="outline" onClick={clearFilters}>
                  Clear
                </Button>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Results */}
      {error ? (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">{error}</p>
          </CardContent>
        </Card>
      ) : loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Loading tracks...</div>
        </div>
      ) : tracks.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <p className="text-muted-foreground text-center">
              No tracks found. Try adjusting your filters or add some tracks to
              your library.
            </p>
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="border rounded-lg">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Title</TableHead>
                  <TableHead>Artist</TableHead>
                  <TableHead className="text-right">BPM</TableHead>
                  <TableHead className="text-center">Key</TableHead>
                  <TableHead className="text-center">Energy</TableHead>
                  <TableHead className="text-right">Duration</TableHead>
                  <TableHead>Source</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {tracks.map((track) => (
                  <TableRow key={track.id}>
                    <TableCell className="font-medium">{track.title}</TableCell>
                    <TableCell className="text-muted-foreground">
                      {track.artists.join(", ")}
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {track.bpm.toFixed(1)}
                    </TableCell>
                    <TableCell className="text-center">
                      <CamelotBadge camelot={track.camelot} />
                    </TableCell>
                    <TableCell className="text-center">
                      <EnergyBadge energy={track.energy} />
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {formatDuration(track.duration_ms)}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{track.source}</Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {/* Pagination */}
          {total > 20 && (
            <div className="flex justify-center gap-2">
              <Button
                variant="outline"
                disabled={page === 1}
                onClick={() => setPage((p) => p - 1)}
              >
                Previous
              </Button>
              <span className="flex items-center px-4 text-muted-foreground">
                Page {page} of {Math.ceil(total / 20)}
              </span>
              <Button
                variant="outline"
                disabled={page * 20 >= total}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
