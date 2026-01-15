/**
 * DJ AI Studio API Client
 *
 * Type-safe client for the FastAPI backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Base fetch wrapper with error handling
 */
async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}/api/v1${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

// ============================================================================
// Types
// ============================================================================

export interface Track {
  id: string;
  title: string;
  artists: string[];
  album: string | null;
  duration_ms: number;
  bpm: number;
  key: string;
  camelot: string;
  energy: number;
  mood: string[];
  genre: string[];
  vocals: string | null;
  structure: TrackStructure | null;
  rating: number | null;
  tags: string[];
  notes: string | null;
  source: string;
  source_id: string;
  cover_url: string | null;
  created_at: string;
  analyzed_at: string | null;
}

export interface TrackStructure {
  intro_ms: number | null;
  outro_ms: number | null;
  drop_ms: number | null;
  breakdown_ms: number | null;
}

export interface SetTrack {
  position: number;
  track_id: string;
  transition_type: string;
  mix_in_point_ms: number | null;
  mix_out_point_ms: number | null;
  notes: string | null;
}

export interface DJSet {
  id: string;
  name: string;
  description: string | null;
  target_duration_min: number;
  style: string | null;
  energy_curve: number[];
  tracks: SetTrack[];
  created_at: string;
  updated_at: string;
}

export interface LibraryStats {
  total_tracks: number;
  analyzed_tracks: number;
  total_sets: number;
  bpm_range: [number, number] | null;
  avg_energy: number | null;
}

export interface TrackFilters {
  query?: string;
  bpm_min?: number;
  bpm_max?: number;
  key?: string;
  camelot?: string;
  energy_min?: number;
  energy_max?: number;
  source?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
}

export interface AnalysisResult {
  bpm: number;
  bpm_confidence: number;
  key: string;
  camelot: string;
  is_minor: boolean;
  key_confidence: number;
  energy: number;
  duration_seconds: number;
}

export interface CreateSetRequest {
  name: string;
  description?: string;
  target_duration_min?: number;
  style?: string;
}

// ============================================================================
// Library API
// ============================================================================

export const libraryApi = {
  /**
   * Get library statistics
   */
  async stats(): Promise<LibraryStats> {
    return fetchApi<LibraryStats>("/library/stats");
  },
};

// ============================================================================
// Tracks API
// ============================================================================

export const tracksApi = {
  /**
   * List tracks with optional filters and pagination
   */
  async list(
    filters: TrackFilters = {},
    page: number = 1,
    limit: number = 20
  ): Promise<PaginatedResponse<Track>> {
    const params = new URLSearchParams();

    // Pagination
    params.set("skip", String((page - 1) * limit));
    params.set("limit", String(limit));

    // Filters
    if (filters.bpm_min !== undefined) {
      params.set("bpm_min", String(filters.bpm_min));
    }
    if (filters.bpm_max !== undefined) {
      params.set("bpm_max", String(filters.bpm_max));
    }
    if (filters.key) {
      params.set("key", filters.key);
    }
    if (filters.camelot) {
      params.set("camelot", filters.camelot);
    }
    if (filters.energy_min !== undefined) {
      params.set("energy_min", String(filters.energy_min));
    }
    if (filters.energy_max !== undefined) {
      params.set("energy_max", String(filters.energy_max));
    }
    if (filters.source) {
      params.set("source", filters.source);
    }

    const tracks = await fetchApi<Track[]>(`/tracks?${params.toString()}`);

    // The API returns a list, but we need total count
    // For now, estimate based on whether we got a full page
    return {
      items: tracks,
      total: tracks.length === limit ? (page + 1) * limit : (page - 1) * limit + tracks.length,
    };
  },

  /**
   * Get a single track by ID
   */
  async get(id: string): Promise<Track> {
    return fetchApi<Track>(`/tracks/${id}`);
  },

  /**
   * Create a new track
   */
  async create(track: Partial<Track>): Promise<Track> {
    return fetchApi<Track>("/tracks", {
      method: "POST",
      body: JSON.stringify(track),
    });
  },

  /**
   * Update a track
   */
  async update(id: string, update: Partial<Track>): Promise<Track> {
    return fetchApi<Track>(`/tracks/${id}`, {
      method: "PATCH",
      body: JSON.stringify(update),
    });
  },

  /**
   * Delete a track
   */
  async delete(id: string): Promise<void> {
    return fetchApi<void>(`/tracks/${id}`, {
      method: "DELETE",
    });
  },

  /**
   * Analyze an uploaded audio file
   */
  async analyze(file: File): Promise<AnalysisResult> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/api/v1/analysis/file`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Analysis failed: ${response.status}`);
    }

    return response.json();
  },
};

// ============================================================================
// Sets API
// ============================================================================

export const setsApi = {
  /**
   * List all DJ sets
   */
  async list(): Promise<DJSet[]> {
    return fetchApi<DJSet[]>("/sets");
  },

  /**
   * Get a single set by ID
   */
  async get(id: string): Promise<DJSet> {
    return fetchApi<DJSet>(`/sets/${id}`);
  },

  /**
   * Create a new DJ set
   */
  async create(name: string, description?: string): Promise<DJSet> {
    const now = new Date().toISOString();
    const setData: CreateSetRequest & {
      id: string;
      tracks: SetTrack[];
      energy_curve: number[];
      created_at: string;
      updated_at: string;
    } = {
      id: crypto.randomUUID(),
      name,
      description,
      target_duration_min: 60,
      tracks: [],
      energy_curve: [],
      created_at: now,
      updated_at: now,
    };

    return fetchApi<DJSet>("/sets", {
      method: "POST",
      body: JSON.stringify(setData),
    });
  },

  /**
   * Update a set
   */
  async update(id: string, update: Partial<DJSet>): Promise<DJSet> {
    return fetchApi<DJSet>(`/sets/${id}`, {
      method: "PATCH",
      body: JSON.stringify(update),
    });
  },

  /**
   * Delete a set
   */
  async delete(id: string): Promise<void> {
    return fetchApi<void>(`/sets/${id}`, {
      method: "DELETE",
    });
  },

  /**
   * Add a track to a set
   */
  async addTrack(
    setId: string,
    trackId: string,
    position: number,
    options: Partial<SetTrack> = {}
  ): Promise<DJSet> {
    const trackData: SetTrack = {
      position,
      track_id: trackId,
      transition_type: options.transition_type || "mix",
      mix_in_point_ms: options.mix_in_point_ms || null,
      mix_out_point_ms: options.mix_out_point_ms || null,
      notes: options.notes || null,
    };

    return fetchApi<DJSet>(`/sets/${setId}/tracks`, {
      method: "POST",
      body: JSON.stringify(trackData),
    });
  },

  /**
   * Remove a track from a set
   */
  async removeTrack(setId: string, position: number): Promise<void> {
    return fetchApi<void>(`/sets/${setId}/tracks/${position}`, {
      method: "DELETE",
    });
  },
};
