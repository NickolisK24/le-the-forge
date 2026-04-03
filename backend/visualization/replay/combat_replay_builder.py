from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ReplayEntity:
    entity_id: str
    position: tuple[float, float]
    health: float
    is_alive: bool
    metadata: dict = field(default_factory=dict)


@dataclass
class ReplayProjectile:
    projectile_id: str
    position: tuple[float, float]
    direction: tuple[float, float]
    speed: float


@dataclass
class ReplayFrame:
    frame_index: int
    time: float
    entities: list[ReplayEntity]
    projectiles: list[ReplayProjectile]
    events: list[dict]  # damage, kills, etc. this frame


@dataclass
class ReplayData:
    frames: list[ReplayFrame]
    duration: float
    tick_size: float
    entity_ids: list[str]
    total_frames: int


class CombatReplayBuilder:
    def __init__(self, tick_size: float = 0.1) -> None:
        self.tick_size = tick_size
        self._frames: list[ReplayFrame] = []

    def add_frame(
        self,
        time: float,
        entities: list[ReplayEntity],
        projectiles: list[ReplayProjectile] | None = None,
        events: list[dict] | None = None,
    ) -> ReplayFrame:
        frame = ReplayFrame(
            frame_index=len(self._frames),
            time=time,
            entities=entities,
            projectiles=projectiles if projectiles is not None else [],
            events=events if events is not None else [],
        )
        self._frames.append(frame)
        return frame

    def build(self) -> ReplayData:
        sorted_frames = sorted(self._frames, key=lambda f: f.time)
        duration = sorted_frames[-1].time if sorted_frames else 0.0

        entity_ids: list[str] = []
        seen: set[str] = set()
        for frame in sorted_frames:
            for entity in frame.entities:
                if entity.entity_id not in seen:
                    seen.add(entity.entity_id)
                    entity_ids.append(entity.entity_id)

        return ReplayData(
            frames=sorted_frames,
            duration=duration,
            tick_size=self.tick_size,
            entity_ids=entity_ids,
            total_frames=len(sorted_frames),
        )

    def reset(self) -> None:
        self._frames = []

    def get_frame(self, frame_index: int) -> ReplayFrame | None:
        for frame in self._frames:
            if frame.frame_index == frame_index:
                return frame
        return None

    def get_frame_at_time(self, time: float) -> ReplayFrame | None:
        if not self._frames:
            return None
        return min(self._frames, key=lambda f: abs(f.time - time))

    def to_dict(self, replay: ReplayData) -> dict:
        return {
            "duration": replay.duration,
            "tick_size": replay.tick_size,
            "entity_ids": replay.entity_ids,
            "total_frames": replay.total_frames,
            "frames": [
                {
                    "frame_index": frame.frame_index,
                    "time": frame.time,
                    "entities": [
                        {
                            "entity_id": e.entity_id,
                            "position": list(e.position),
                            "health": e.health,
                            "is_alive": e.is_alive,
                            "metadata": e.metadata,
                        }
                        for e in frame.entities
                    ],
                    "projectiles": [
                        {
                            "projectile_id": p.projectile_id,
                            "position": list(p.position),
                            "direction": list(p.direction),
                            "speed": p.speed,
                        }
                        for p in frame.projectiles
                    ],
                    "events": frame.events,
                }
                for frame in replay.frames
            ],
        }
