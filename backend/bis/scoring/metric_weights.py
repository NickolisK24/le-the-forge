from dataclasses import dataclass, field


@dataclass
class MetricWeights:
    tier_weight: float = 0.50
    coverage_weight: float = 0.30
    fp_efficiency_weight: float = 0.10
    feasibility_weight: float = 0.10

    def validate(self) -> bool:
        return abs(self.tier_weight + self.coverage_weight + self.fp_efficiency_weight + self.feasibility_weight - 1.0) < 1e-6

    def normalize(self) -> "MetricWeights":
        total = self.tier_weight + self.coverage_weight + self.fp_efficiency_weight + self.feasibility_weight
        if total == 0:
            return MetricWeights()
        return MetricWeights(
            self.tier_weight / total,
            self.coverage_weight / total,
            self.fp_efficiency_weight / total,
            self.feasibility_weight / total,
        )

    def to_dict(self) -> dict[str, float]:
        return {
            "tier": self.tier_weight,
            "coverage": self.coverage_weight,
            "fp": self.fp_efficiency_weight,
            "feasibility": self.feasibility_weight,
        }


BALANCED = MetricWeights(0.4, 0.3, 0.15, 0.15)
TIER_FOCUSED = MetricWeights(0.7, 0.2, 0.05, 0.05)
COVERAGE_FOCUSED = MetricWeights(0.2, 0.65, 0.10, 0.05)
