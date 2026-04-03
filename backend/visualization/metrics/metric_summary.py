from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DpsBreakdown:
    source: str
    total_damage: float
    dps: float        # total_damage / duration
    hit_count: int
    crit_count: int
    crit_rate: float  # crit_count / hit_count


@dataclass
class BuffUptimeSummary:
    buff_name: str
    total_uptime: float    # seconds active
    uptime_pct: float      # out of duration
    application_count: int


@dataclass
class MetricSummary:
    duration: float
    total_damage: float
    overall_dps: float
    dps_breakdown: list[DpsBreakdown]
    buff_uptimes: list[BuffUptimeSummary]
    kill_times: list[float]
    peak_dps: float   # highest single-tick DPS
    mean_dps: float   # mean over all ticks with damage


class MetricSummaryEngine:
    def compute_dps_breakdown(
        self,
        damage_events: list[dict],
        duration: float,
    ) -> list[DpsBreakdown]:
        source_data: dict[str, dict] = {}
        for ev in damage_events:
            src = str(ev["source"])
            if src not in source_data:
                source_data[src] = {"total": 0.0, "hits": 0, "crits": 0}
            source_data[src]["total"] += float(ev["amount"])
            source_data[src]["hits"] += 1
            if ev.get("is_crit", False):
                source_data[src]["crits"] += 1

        result: list[DpsBreakdown] = []
        for src, data in source_data.items():
            hit_count = data["hits"]
            crit_count = data["crits"]
            crit_rate = crit_count / hit_count if hit_count > 0 else 0.0
            dps = data["total"] / duration if duration > 0 else 0.0
            result.append(
                DpsBreakdown(
                    source=src,
                    total_damage=data["total"],
                    dps=dps,
                    hit_count=hit_count,
                    crit_count=crit_count,
                    crit_rate=crit_rate,
                )
            )
        return result

    def compute_buff_uptimes(
        self,
        buff_events: list[dict],
        duration: float,
    ) -> list[BuffUptimeSummary]:
        # group events by buff_name
        by_buff: dict[str, list[dict]] = {}
        for ev in buff_events:
            name = str(ev["buff_name"])
            by_buff.setdefault(name, []).append(ev)

        result: list[BuffUptimeSummary] = []
        for buff_name, events in by_buff.items():
            sorted_events = sorted(events, key=lambda e: float(e["time"]))
            total_uptime = 0.0
            application_count = 0
            apply_time: float | None = None

            for ev in sorted_events:
                t = float(ev["time"])
                if ev["event"] == "applied":
                    apply_time = t
                    application_count += 1
                elif ev["event"] == "expired" and apply_time is not None:
                    total_uptime += t - apply_time
                    apply_time = None

            # If still active at end of duration
            if apply_time is not None:
                total_uptime += duration - apply_time

            uptime_pct = total_uptime / duration if duration > 0 else 0.0
            result.append(
                BuffUptimeSummary(
                    buff_name=buff_name,
                    total_uptime=total_uptime,
                    uptime_pct=uptime_pct,
                    application_count=application_count,
                )
            )
        return result

    def compute_kill_times(self, kill_events: list[dict]) -> list[float]:
        return sorted(float(ev["time"]) for ev in kill_events)

    def summarize(
        self,
        damage_events: list[dict],
        buff_events: list[dict],
        kill_events: list[dict],
        duration: float,
        tick_size: float = 0.1,
    ) -> MetricSummary:
        dps_breakdown = self.compute_dps_breakdown(damage_events, duration)
        buff_uptimes = self.compute_buff_uptimes(buff_events, duration)
        kill_times = self.compute_kill_times(kill_events)

        total_damage = sum(b.total_damage for b in dps_breakdown)
        overall_dps = total_damage / duration if duration > 0 else 0.0

        # Per-tick damage aggregation (events without a "time" key are skipped)
        tick_totals: dict[int, float] = {}
        for ev in damage_events:
            if "time" not in ev:
                continue
            t = float(ev["time"])
            tick_key = int(t / tick_size)
            tick_totals[tick_key] = tick_totals.get(tick_key, 0.0) + float(ev["amount"])

        if tick_totals:
            tick_damage_values = list(tick_totals.values())
            peak_dps = max(tick_damage_values) / tick_size
            mean_dps = (sum(tick_damage_values) / len(tick_damage_values)) / tick_size
        else:
            peak_dps = 0.0
            mean_dps = 0.0

        return MetricSummary(
            duration=duration,
            total_damage=total_damage,
            overall_dps=overall_dps,
            dps_breakdown=dps_breakdown,
            buff_uptimes=buff_uptimes,
            kill_times=kill_times,
            peak_dps=peak_dps,
            mean_dps=mean_dps,
        )
