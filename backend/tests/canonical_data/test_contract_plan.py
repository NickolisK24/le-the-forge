"""R2_CONTRACT_TEST_PLAN.md T-tests: where each one lives, and which wait on unbuilt packages.

Built in the foundation (see the named modules):
    T3  identity stability            test_ids.py, test_contracts.py (IDENTITY_*)
    T6  patch consistency             test_importer.py, test_store.py (manifest rejections)
    T7  trust propagation (store)     test_store.py, test_importer.py (API half: unbuilt reference API)
    T10 no fallback masking (gate)    tests/fallback_gate (per-path tests belong to each family package)
    T11 no legacy source              test_store.py / test_importer.py static scans, FOREIGN_SOURCE
    T12 migrations on PostgreSQL      tests/postgres (served-dataset half: R2-P14)

The rest are reported as xfail, naming the owning package, until that
package is authorised and replaces its entry here with the real test.
"""
from __future__ import annotations

import pytest

PENDING = {
    "T1_no_field_loss_in_adapters": "R2-P05/P07/P08/P11 family adapters (DECLARED_DROPS)",
    "T2_no_undeclared_value_transformation": "R2-P05/P07/P08/P11 family adapters",
    "T4_family_relationship_integrity": "R2-P07/P08/P11 (primitives are built: test_relationships.py)",
    "T5_mastery_migration": "R2-P06",
    "T8_frontend_backend_parity": "R2-P10",
    "T9_db_provenance": "R2-P13",
    "T13_fail_closed_at_deploy": "R2-P14",
    "T14_import_mapping_honesty": "R2-P11 / R4",
}


@pytest.mark.parametrize("test_id", sorted(PENDING))
def test_pending_contract(test_id):
    pytest.xfail(f"{test_id}: waits on {PENDING[test_id]}, not authorised in the R2 foundation")
