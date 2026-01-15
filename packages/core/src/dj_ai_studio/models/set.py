"""DJ Set data model for DJ AI Studio.

Represents a planned DJ set with ordered tracks, transitions,
and target parameters like duration and energy curve.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


class SetTrack(BaseModel):
    """A track within a DJ set with transition information.

    Attributes:
        position: Order position in the set (1-indexed).
        track_id: Reference to the Track.
        transition_type: How to transition from the previous track.
        mix_in_point_ms: Where to start mixing in (cue point).
        mix_out_point_ms: Where to start mixing out.
        notes: DJ notes for this transition.
    """

    position: int = Field(..., ge=1, description="Position in set (1-indexed)")
    track_id: UUID = Field(..., description="Reference to Track")
    transition_type: Literal["mix", "cut", "fade", "slam", "echo"] = Field(
        default="mix", description="Transition type from previous track"
    )
    mix_in_point_ms: int | None = Field(default=None, ge=0, description="Mix-in cue point in ms")
    mix_out_point_ms: int | None = Field(default=None, ge=0, description="Mix-out point in ms")
    notes: str | None = Field(default=None, description="DJ notes for this transition")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "position": 1,
                    "track_id": "123e4567-e89b-12d3-a456-426614174000",
                    "transition_type": "mix",
                    "mix_in_point_ms": 0,
                    "mix_out_point_ms": 600000,
                    "notes": "Start with intro, build slowly",
                }
            ]
        }
    }


class Set(BaseModel):
    """A DJ set with planned tracks and transitions.

    Attributes:
        id: Unique identifier for the set.
        name: Set name.
        description: Optional description of the set.
        target_duration_min: Target duration in minutes.
        style: DJ style/vibe for the set.
        energy_curve: Target energy levels per segment of the set.
        tracks: Ordered list of tracks with transition info.
        created_at: When the set was created.
        updated_at: When the set was last modified.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique set identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Set name")
    description: str | None = Field(default=None, description="Set description")
    target_duration_min: int = Field(
        default=60, ge=5, le=480, description="Target duration in minutes"
    )
    style: (
        Literal[
            "warm-up",
            "progressive",
            "peak-time",
            "closing",
            "journey",
            "mixed",
        ]
        | None
    ) = Field(default=None, description="Set style/vibe")
    energy_curve: list[int] = Field(
        default_factory=list,
        description="Target energy levels per segment (1-10)",
    )
    tracks: list[SetTrack] = Field(
        default_factory=list, description="Ordered tracks with transitions"
    )
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

    @field_validator("energy_curve")
    @classmethod
    def validate_energy_curve(cls, v: list[int]) -> list[int]:
        """Validate energy curve values are between 1-10."""
        for energy in v:
            if not 1 <= energy <= 10:
                msg = f"Energy curve values must be between 1-10, got {energy}"
                raise ValueError(msg)
        return v

    @model_validator(mode="after")
    def validate_track_positions(self) -> Set:
        """Ensure track positions are sequential starting from 1."""
        if not self.tracks:
            return self

        positions = sorted(t.position for t in self.tracks)
        expected = list(range(1, len(self.tracks) + 1))

        if positions != expected:
            msg = f"Track positions must be sequential from 1. Got: {positions}"
            raise ValueError(msg)

        return self

    def add_track(
        self,
        track_id: UUID,
        transition_type: Literal["mix", "cut", "fade", "slam", "echo"] = "mix",
        mix_in_point_ms: int | None = None,
        mix_out_point_ms: int | None = None,
        notes: str | None = None,
    ) -> SetTrack:
        """Add a track to the end of the set.

        Args:
            track_id: UUID of the track to add.
            transition_type: How to transition from previous track.
            mix_in_point_ms: Where to start mixing in.
            mix_out_point_ms: Where to start mixing out.
            notes: DJ notes for this transition.

        Returns:
            The created SetTrack instance.
        """
        position = len(self.tracks) + 1
        set_track = SetTrack(
            position=position,
            track_id=track_id,
            transition_type=transition_type,
            mix_in_point_ms=mix_in_point_ms,
            mix_out_point_ms=mix_out_point_ms,
            notes=notes,
        )
        self.tracks.append(set_track)
        self.updated_at = datetime.now()
        return set_track

    def remove_track(self, position: int) -> SetTrack | None:
        """Remove a track from the set and reorder remaining tracks.

        Args:
            position: Position of the track to remove (1-indexed).

        Returns:
            The removed SetTrack or None if not found.
        """
        for i, track in enumerate(self.tracks):
            if track.position == position:
                removed = self.tracks.pop(i)
                # Reorder remaining tracks
                for j, t in enumerate(self.tracks):
                    # Create new SetTrack with updated position
                    self.tracks[j] = t.model_copy(update={"position": j + 1})
                self.updated_at = datetime.now()
                return removed
        return None

    def reorder_track(self, from_position: int, to_position: int) -> bool:
        """Move a track from one position to another.

        Args:
            from_position: Current position (1-indexed).
            to_position: Target position (1-indexed).

        Returns:
            True if reorder was successful, False otherwise.
        """
        if from_position == to_position:
            return True

        if not 1 <= from_position <= len(self.tracks):
            return False
        if not 1 <= to_position <= len(self.tracks):
            return False

        # Find and remove the track
        track_to_move = None
        for i, track in enumerate(self.tracks):
            if track.position == from_position:
                track_to_move = self.tracks.pop(i)
                break

        if track_to_move is None:
            return False

        # Insert at new position (convert to 0-indexed)
        self.tracks.insert(to_position - 1, track_to_move)

        # Reorder all positions
        for i, track in enumerate(self.tracks):
            self.tracks[i] = track.model_copy(update={"position": i + 1})

        self.updated_at = datetime.now()
        return True

    @property
    def track_count(self) -> int:
        """Get the number of tracks in the set."""
        return len(self.tracks)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Saturday Night Progressive",
                    "description": "Progressive house journey",
                    "target_duration_min": 90,
                    "style": "progressive",
                    "energy_curve": [3, 4, 5, 6, 7, 8, 9, 8, 6],
                    "tracks": [],
                }
            ]
        }
    }
