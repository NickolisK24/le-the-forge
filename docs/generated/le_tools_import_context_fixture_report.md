# LE Tools Import Context Dry-Run Report

- production_safe: false
- source: fixture
- total items: 16

## Resolver Status Counts

- resolved: 10
- needs_context: 3
- needs_review: 1
- deferred: 0
- unresolved: 2

## Items

- slot=helmet forge=helm base_type_id=0 status=resolved bundle=helmet
- slot=body_armour forge=chest base_type_id=1 status=resolved bundle=body_armor
- slot=weapon forge=axe base_type_id=5 status=resolved bundle=one_handed_axe
- slot=weapon forge=axe base_type_id=12 status=resolved bundle=two_handed_axe
- slot=weapon forge=mace base_type_id=7 status=resolved bundle=one_handed_maces
- slot=weapon forge=mace base_type_id=13 status=resolved bundle=two_handed_mace
- slot=weapon forge=sword base_type_id=9 status=resolved bundle=one_handed_sword
- slot=weapon forge=sword base_type_id=16 status=resolved bundle=two_handed_sword
- slot=idol forge=idol_1x1 base_type_id=25 status=resolved bundle=idol_1x1_eterra
- slot=idol forge=idol_1x1 base_type_id=26 status=resolved bundle=idol_1x1_lagon
- slot=weapon forge=axe base_type_id=null status=needs_context bundle=null
  - warning: base_type_id is required; resolver will not guess from slug alone.
- slot=idol forge=idol_1x1 base_type_id=null status=needs_context bundle=null
  - warning: base_type_id is required; resolver will not guess from slug alone.
- slot=weapon forge=spear base_type_id=14 status=needs_review bundle=null
  - warning: Forge item type requires manual review before resolution.
- slot=unknown forge=unknown_type base_type_id=null status=unresolved bundle=null
  - warning: No reviewed mapping exists for this Forge item type.
- slot=belt forge=belt base_type_id=null status=needs_context bundle=null
  - warning: subtype_id was provided but ignored; subtype_id alone is not a valid identity.
  - warning: base_type_id is required; resolver will not guess from slug alone.
  - warning: subtype_id is present without base_type_id; this is not sufficient context.
- slot=helmet forge=null base_type_id=null status=unresolved bundle=null
  - warning: Missing forge_item_type.
  - warning: No item_type-like field was found; name-only matching is not attempted.

## Context Gaps

- index=10 slot=weapon forge=axe status=needs_context
- index=11 slot=idol forge=idol_1x1 status=needs_context
- index=12 slot=weapon forge=spear status=needs_review
- index=13 slot=unknown forge=unknown_type status=unresolved
- index=14 slot=belt forge=belt status=needs_context
- index=15 slot=helmet forge=null status=unresolved

## Recommendations

- Keep this report developer-only; it does not change LE Tools importer output.
- Keep production_safe=false until a separate migration defines consumer behavior.
- Thread base_type_id into diagnostic inputs before resolving collapsed item type slugs.
- Review needs_review item types before adding translations.
- Do not resolve unknown or name-only records by guessing.
- Treat context gaps as warnings; do not silently fall back to slug/name matching.

