"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { setsApi, type DJSet } from "@/lib/api";

export default function SetsPage() {
  const [sets, setSets] = useState<DJSet[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newSetName, setNewSetName] = useState("");
  const [newSetDescription, setNewSetDescription] = useState("");
  const [creating, setCreating] = useState(false);

  const loadSets = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await setsApi.list();
      setSets(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load sets");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSets();
  }, []);

  const handleCreateSet = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSetName.trim()) return;

    setCreating(true);
    try {
      await setsApi.create(newSetName, newSetDescription || undefined);
      setNewSetName("");
      setNewSetDescription("");
      setDialogOpen(false);
      loadSets();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create set");
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteSet = async (id: string) => {
    if (!confirm("Are you sure you want to delete this set?")) return;

    try {
      await setsApi.delete(id);
      loadSets();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to delete set");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">DJ Sets</h1>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>Create New Set</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New DJ Set</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreateSet} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Name</label>
                <Input
                  value={newSetName}
                  onChange={(e) => setNewSetName(e.target.value)}
                  placeholder="Friday Night Mix"
                  required
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">
                  Description (optional)
                </label>
                <Input
                  value={newSetDescription}
                  onChange={(e) => setNewSetDescription(e.target.value)}
                  placeholder="Opening set for club night"
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={creating}>
                  {creating ? "Creating..." : "Create Set"}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">{error}</p>
          </CardContent>
        </Card>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Loading sets...</div>
        </div>
      ) : sets.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <p className="text-muted-foreground text-center">
              No DJ sets yet. Create your first set to start building your
              perfect mix!
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {sets.map((set) => (
            <Card key={set.id} className="hover:bg-accent/50 transition-colors">
              <CardHeader className="pb-2">
                <div className="flex justify-between items-start">
                  <CardTitle className="text-lg">{set.name}</CardTitle>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-muted-foreground hover:text-destructive"
                    onClick={() => handleDeleteSet(set.id)}
                  >
                    Delete
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {set.description && (
                  <p className="text-muted-foreground text-sm mb-2">
                    {set.description}
                  </p>
                )}
                <div className="flex justify-between items-center text-sm">
                  <span className="text-muted-foreground">
                    {set.tracks.length} track
                    {set.tracks.length !== 1 ? "s" : ""}
                  </span>
                  <span className="text-muted-foreground">
                    {new Date(set.created_at).toLocaleDateString()}
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
