"""
R0 regression: build ownership and visibility boundary (API-4, API-5, API-6).

Matrix: requester (owner / other user / anonymous) x build (public / private /
anonymous-owned) across every build-by-slug route. Denied reads are 404 so
private slugs are not confirmed; denied mutations never change stored state.
"""

import pytest
from flask_jwt_extended import create_access_token

from app.models import Build, BuildSkill, CraftSession, User
from app.routes import analysis as analysis_routes
from app.routes import skills as skills_routes
from app.services import build_service

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _token_headers(app, user):
    with app.app_context():
        return {"Authorization": f"Bearer {create_access_token(identity=user.id)}"}


@pytest.fixture
def owner(db):
    u = User(discord_id="r0-owner", username="R0Owner")
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def other(db):
    u = User(discord_id="r0-other", username="R0Other")
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def headers(app, owner, other):
    return {
        "owner": _token_headers(app, owner),
        "other": _token_headers(app, other),
        "anonymous": {},
    }


@pytest.fixture(scope="module")
def tree_case():
    """A real skill tree plus one node that only requires the root node."""
    trees = skills_routes._load_trees()
    for tree_id, tree in sorted(trees.items()):
        nodes = tree.get("nodes") or []
        ability = tree.get("ability")
        if not ability or not nodes:
            continue
        node_map = {n["id"]: n for n in nodes}
        for node in nodes:
            reqs = node.get("requirements") or []
            if node.get("maxPoints", 1) < 1 or not reqs:
                continue
            if all(node_map.get(r.get("node", r.get("nodeId")), {}).get("maxPoints", 1) == 0
                   for r in reqs):
                return {"tree_id": tree_id, "ability": ability, "node_id": node["id"]}
    pytest.skip("no skill tree with a root-adjacent node available")


def _make_build(db, *, author, is_public, name, ability):
    build = build_service.create_build(
        {
            "name": name,
            "character_class": "Mage",
            "mastery": "Sorcerer",
            "is_public": is_public,
            "skills": [{"skill_name": ability, "points_allocated": 0, "spec_tree": []}],
        },
        user_id=author.id if author else None,
    )
    return build


@pytest.fixture
def builds(db, owner, tree_case):
    a = tree_case["ability"]
    return {
        "public": _make_build(db, author=owner, is_public=True, name="R0 Public", ability=a),
        "private": _make_build(db, author=owner, is_public=False, name="R0 Private", ability=a),
        "anon_public": _make_build(db, author=None, is_public=True, name="R0 Anon Public", ability=a),
        "anon_private": _make_build(db, author=None, is_public=False, name="R0 Anon Private", ability=a),
    }


def _snapshot(db, slug):
    db.session.expire_all()
    b = Build.query.filter_by(slug=slug).first()
    if b is None:
        return None
    skills = sorted((s.slot, s.skill_name, tuple(s.spec_tree or []), s.points_allocated) for s in b.skills)
    return (b.name, b.description, b.is_public, b.level, tuple(skills))


# ---------------------------------------------------------------------------
# Read matrix
# ---------------------------------------------------------------------------

READ_ROUTES = [
    ("GET", "/api/builds/{slug}"),
    ("POST", "/api/builds/{slug}/simulate"),
    ("POST", "/api/builds/{slug}/optimize"),
    ("GET", "/api/builds/{slug}/optimize"),
    ("GET", "/api/builds/{slug}/skills"),
    ("GET", "/api/builds/{slug}/report"),
    ("GET", "/api/builds/{slug}/analysis/corruption"),
    ("GET", "/api/builds/{slug}/analysis/gear-upgrades"),
    ("GET", "/api/builds/{slug}/analysis/boss/{boss}"),
    ("POST", "/api/builds/{slug}/view"),
]

# (build kind, requester) -> may read?
READ_EXPECTATIONS = {
    ("public", "owner"): True, ("public", "other"): True, ("public", "anonymous"): True,
    ("private", "owner"): True, ("private", "other"): False, ("private", "anonymous"): False,
    ("anon_public", "owner"): True, ("anon_public", "other"): True, ("anon_public", "anonymous"): True,
    ("anon_private", "owner"): True, ("anon_private", "other"): True, ("anon_private", "anonymous"): True,
}


def _call(client, method, path, headers, json=None):
    return client.open(path, method=method, headers=headers, json=json)


@pytest.mark.parametrize("method,template", READ_ROUTES)
@pytest.mark.parametrize("kind,who", sorted(READ_EXPECTATIONS))
def test_read_matrix(client, db, builds, headers, method, template, kind, who):
    boss = analysis_routes._default_boss_id()
    path = template.format(slug=builds[kind].slug, boss=boss)
    resp = _call(client, method, path, headers[who])
    if READ_EXPECTATIONS[(kind, who)]:
        assert resp.status_code not in (401, 403, 404), (path, who, resp.status_code, resp.get_data(as_text=True)[:200])
    else:
        assert resp.status_code == 404, (path, who, resp.status_code)


def test_private_build_not_exposed_through_cached_optimize(client, db, builds, headers):
    slug = builds["private"].slug
    first = client.get(f"/api/builds/{slug}/optimize", headers=headers["owner"])
    assert first.status_code not in (401, 403, 404)
    assert client.get(f"/api/builds/{slug}/optimize").status_code == 404
    assert client.get(f"/api/builds/{slug}/optimize", headers=headers["other"]).status_code == 404


@pytest.mark.parametrize("who,expected_ok", [("owner", True), ("other", False), ("anonymous", False)])
def test_compare_requires_both_builds_readable(client, db, builds, headers, who, expected_ok):
    path = f"/api/compare/{builds['public'].slug}/{builds['private'].slug}"
    resp = client.get(path, headers=headers[who])
    if expected_ok:
        assert resp.status_code not in (401, 403, 404)
    else:
        assert resp.status_code == 404


@pytest.mark.parametrize("who", ["other"])
def test_vote_on_unreadable_private_build_is_404(client, db, builds, headers, who):
    resp = client.post(f"/api/builds/{builds['private'].slug}/vote",
                       json={"direction": 1}, headers=headers[who])
    assert resp.status_code == 404


def test_private_builds_absent_from_public_listing(client, db, builds):
    resp = client.get("/api/builds?per_page=100")
    slugs = {b["slug"] for b in resp.get_json()["data"]}
    assert builds["public"].slug in slugs
    assert builds["private"].slug not in slugs
    assert builds["anon_private"].slug not in slugs


# ---------------------------------------------------------------------------
# Mutation matrix
# ---------------------------------------------------------------------------

# (build kind, requester) -> expected status for a denied mutation, or None if allowed
MUTATION_EXPECTATIONS = {
    ("public", "owner"): None, ("public", "other"): 403, ("public", "anonymous"): 401,
    ("private", "owner"): None, ("private", "other"): 404, ("private", "anonymous"): 404,
    ("anon_public", "owner"): 403, ("anon_public", "other"): 403, ("anon_public", "anonymous"): 403,
    ("anon_private", "owner"): 403, ("anon_private", "other"): 403, ("anon_private", "anonymous"): 403,
}


@pytest.mark.parametrize("kind,who", sorted(MUTATION_EXPECTATIONS))
def test_update_matrix(client, db, builds, headers, kind, who):
    slug = builds[kind].slug
    before = _snapshot(db, slug)
    resp = client.patch(f"/api/builds/{slug}", json={"description": "R0 tamper"}, headers=headers[who])
    expected = MUTATION_EXPECTATIONS[(kind, who)]
    if expected is None:
        assert resp.status_code == 200
        assert _snapshot(db, slug)[1] == "R0 tamper"
    else:
        assert resp.status_code == expected
        assert _snapshot(db, slug) == before


@pytest.mark.parametrize("kind,who", sorted(MUTATION_EXPECTATIONS))
def test_skill_node_matrix(client, db, builds, headers, tree_case, kind, who):
    slug = builds[kind].slug
    before = _snapshot(db, slug)
    path = f"/api/builds/{slug}/skills/{tree_case['tree_id']}/nodes/{tree_case['node_id']}"
    resp = client.patch(path, json={"points": 1}, headers=headers[who])
    expected = MUTATION_EXPECTATIONS[(kind, who)]
    if expected is None:
        assert resp.status_code == 200, resp.get_data(as_text=True)[:300]
        assert _snapshot(db, slug) != before
    else:
        assert resp.status_code == expected
        assert _snapshot(db, slug) == before


@pytest.mark.parametrize("kind,who", sorted(MUTATION_EXPECTATIONS))
def test_delete_matrix(client, db, builds, headers, kind, who):
    slug = builds[kind].slug
    resp = client.delete(f"/api/builds/{slug}", headers=headers[who])
    expected = MUTATION_EXPECTATIONS[(kind, who)]
    if expected is None:
        assert resp.status_code == 204
        assert _snapshot(db, slug) is None
    else:
        # Delete still requires a login first.
        if who == "anonymous":
            expected = 401
        assert resp.status_code == expected
        assert _snapshot(db, slug) is not None


def test_new_anonymous_private_build_gets_unguessable_slug(db):
    b = build_service.create_build(
        {"name": "Guessable Name", "character_class": "Mage", "mastery": "Sorcerer", "is_public": False},
        user_id=None,
    )
    assert b.slug.startswith("guessable-name-")
    assert len(b.slug) >= len("guessable-name-") + 16


# ---------------------------------------------------------------------------
# Craft sessions
# ---------------------------------------------------------------------------

def _make_session(db, user):
    s = CraftSession(
        slug=f"r0-craft-{'owned' if user else 'anon'}",
        user_id=user.id if user else None,
        item_type="Helmet",
        item_level=80,
        forge_potential=30,
        affixes=[],
    )
    db.session.add(s)
    db.session.commit()
    return s


@pytest.mark.parametrize("who,expected", [("owner", 204), ("other", 403), ("anonymous", 403)])
def test_owned_craft_session_delete(client, db, owner, headers, who, expected):
    s = _make_session(db, owner)
    resp = client.delete(f"/api/craft/{s.slug}", headers=headers[who])
    assert resp.status_code == expected
    db.session.expire_all()
    assert (CraftSession.query.filter_by(slug=s.slug).first() is None) == (expected == 204)


@pytest.mark.parametrize("who", ["owner", "other", "anonymous"])
def test_ownerless_craft_session_cannot_be_deleted(client, db, headers, who):
    s = _make_session(db, None)
    resp = client.delete(f"/api/craft/{s.slug}", headers=headers[who])
    assert resp.status_code == 403
    db.session.expire_all()
    assert CraftSession.query.filter_by(slug=s.slug).first() is not None


@pytest.mark.parametrize("who,expected", [("other", 403), ("anonymous", 403)])
def test_owned_craft_session_action_denied_for_non_owner(client, db, owner, headers, who, expected):
    s = _make_session(db, owner)
    resp = client.post(f"/api/craft/{s.slug}/action", json={"action": "add_affix"}, headers=headers[who])
    assert resp.status_code == expected
