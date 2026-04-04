"""
Domain Calculators — pure computation functions.

Each calculator module:
  - Accepts typed domain objects as inputs
  - Performs math or stat computation
  - Has no side effects
  - Does not access registries or Flask context
  - Returns computed values

Engines import from here; calculators never import from engines.
"""
