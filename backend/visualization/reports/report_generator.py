from __future__ import annotations

import csv
import dataclasses
import io
import json
import time
from dataclasses import dataclass, field

from visualization.metrics.metric_summary import MetricSummary, MetricSummaryEngine


@dataclass
class ReportSection:
    title: str
    data: list[dict]
    summary: dict = field(default_factory=dict)


@dataclass
class Report:
    title: str
    generated_at: float   # unix timestamp
    sections: list[ReportSection]
    metadata: dict = field(default_factory=dict)


class ReportGenerator:
    def create_report(self, title: str, metadata: dict | None = None) -> Report:
        """Create a new empty Report with the given title."""
        return Report(title=title, generated_at=time.time(), sections=[], metadata=metadata or {})

    def add_section(
        self,
        report: Report,
        title: str,
        data: list[dict],
        summary: dict | None = None,
    ) -> None:
        """Append a section to the report."""
        report.sections.append(ReportSection(title=title, data=data, summary=summary or {}))

    def to_json(self, report: Report) -> str:
        """Serialize the entire report to a JSON string."""
        return json.dumps(dataclasses.asdict(report))

    def to_csv(self, report: Report, section_index: int = 0) -> str:
        """
        Serialize one section to a CSV string.
        Returns an empty string if the report has no sections or the section has no rows.
        """
        if not report.sections:
            return ""

        section = report.sections[section_index]
        if not section.data:
            return ""

        buf = io.StringIO()
        fieldnames = list(section.data[0].keys())
        writer = csv.DictWriter(buf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(section.data)
        return buf.getvalue()

    def to_pdf_data(self, report: Report) -> dict:
        """
        Return a PDF-ready structure (structured dict for future rendering;
        no actual PDF library is used).
        """
        return {
            "title": report.title,
            "generated_at": report.generated_at,
            "sections": [
                {
                    "title": section.title,
                    "data": section.data,
                    "summary": section.summary,
                }
                for section in report.sections
            ],
        }

    def from_metric_summary(
        self,
        summary: MetricSummary,
        build_label: str = "Build",
    ) -> Report:
        """
        Create a Report from a MetricSummary with three sections:
        - "DPS Breakdown"
        - "Buff Uptimes"
        - "Kill Times"
        """
        report = self.create_report(title=f"{build_label} Report")

        # --- DPS Breakdown ---
        dps_rows: list[dict] = []
        for entry in getattr(summary, "dps_breakdown", []):
            dps_rows.append(
                {
                    "source": getattr(entry, "source", ""),
                    "total_damage": getattr(entry, "total_damage", 0.0),
                    "dps": getattr(entry, "dps", 0.0),
                    "hit_count": getattr(entry, "hit_count", 0),
                    "crit_count": getattr(entry, "crit_count", 0),
                    "crit_rate": getattr(entry, "crit_rate", 0.0),
                }
            )
        self.add_section(report, "DPS Breakdown", dps_rows)

        # --- Buff Uptimes ---
        buff_rows: list[dict] = []
        for entry in getattr(summary, "buff_uptimes", []):
            buff_rows.append(
                {
                    "buff_name": getattr(entry, "buff_name", ""),
                    "total_uptime": getattr(entry, "total_uptime", 0.0),
                    "uptime_pct": getattr(entry, "uptime_pct", 0.0),
                    "application_count": getattr(entry, "application_count", 0),
                }
            )
        self.add_section(report, "Buff Uptimes", buff_rows)

        # --- Kill Times ---
        kill_rows: list[dict] = [
            {"index": idx, "kill_time": kt}
            for idx, kt in enumerate(getattr(summary, "kill_times", []))
        ]
        self.add_section(report, "Kill Times", kill_rows)

        return report
