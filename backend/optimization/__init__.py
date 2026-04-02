"""
optimization — Build Optimization Engine (Phase F).

Pipeline:
    OptimizationConfig
    → VariantGenerator  (produces mutated BuildDefinition objects)
    → ConstraintEngine  (filters invalid variants)
    → BatchRunner       (runs encounter simulation on each variant)
    → ScoringEngine     (assigns a numeric score to each result)
    → RankingEngine     (sorts and returns top N)
    → OptimizationResult list
"""
