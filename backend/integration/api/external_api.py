from __future__ import annotations
from dataclasses import dataclass, field
import importlib
import time

# Load import package via importlib (reserved keyword workaround)
_import_pkg = importlib.import_module("integration.import.build_import_parser")
BuildImportParser = _import_pkg.BuildImportParser

from integration.export.build_exporter import BuildExporter
from integration.storage.build_repository import BuildRepository, StoredBuild
from integration.auth.auth_manager import AuthManager
from integration.sharing.share_link_generator import ShareLinkGenerator


@dataclass
class ApiRequest:
    method: str           # "GET", "POST", "DELETE"
    path: str             # e.g. "/api/build/abc123"
    body: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)
    query_params: dict = field(default_factory=dict)


@dataclass
class ApiResponse:
    status_code: int
    body: dict
    headers: dict = field(default_factory=dict)


class ExternalApi:
    def __init__(
        self,
        repository: BuildRepository | None = None,
        auth: AuthManager | None = None,
    ):
        self._repo = repository or BuildRepository()
        self._auth = auth or AuthManager()
        self._parser = BuildImportParser()
        self._exporter = BuildExporter()
        self._share_gen = ShareLinkGenerator()

    def _authenticate(self, request: ApiRequest) -> str | None:
        # Returns user_id if authenticated via "X-Api-Key" header, else None
        api_key = request.headers.get("X-Api-Key")
        if not api_key:
            return None
        identity = self._auth.authenticate_api_key(api_key)
        return identity.user_id if identity else None

    def handle(self, request: ApiRequest) -> ApiResponse:
        # Route: POST /api/import/build, GET /api/export/build,
        #        POST /api/share/build, GET /api/build/{id}
        path = request.path.rstrip("/")
        if request.method == "POST" and path == "/api/import/build":
            return self._import_build(request)
        elif request.method == "GET" and path == "/api/export/build":
            return self._export_build(request)
        elif request.method == "POST" and path == "/api/share/build":
            return self._share_build(request)
        elif request.method == "GET" and path.startswith("/api/build/"):
            build_id = path.split("/api/build/")[-1]
            return self._get_build(request, build_id)
        return ApiResponse(404, {"error": "endpoint not found"})

    def _import_build(self, request: ApiRequest) -> ApiResponse:
        data = request.body.get("data", "")
        fmt = request.body.get("format")
        user_id = self._authenticate(request)
        parse_result = self._parser.parse(data)
        if not parse_result.success:
            return ApiResponse(400, {"error": "import failed", "details": parse_result.errors})
        schema = parse_result.schema
        build_id = self._share_gen.generate_build_id(schema.build_name, schema.version)
        stored = StoredBuild(
            build_id,
            schema.build_name,
            schema.character_class,
            schema.version,
            {"name": schema.build_name},
            user_id,
            True,
            time.time(),
            time.time(),
        )
        self._repo.save(stored)
        if user_id:
            self._auth.claim_ownership(build_id, user_id)
        return ApiResponse(200, {"build_id": build_id, "build_name": schema.build_name})

    def _export_build(self, request: ApiRequest) -> ApiResponse:
        build_id = request.query_params.get("id")
        if not build_id:
            return ApiResponse(400, {"error": "missing id param"})
        build = self._repo.get(build_id)
        if not build:
            return ApiResponse(404, {"error": "build not found"})
        return ApiResponse(
            200,
            {"build_id": build_id, "data": build.data, "version": build.version},
        )

    def _share_build(self, request: ApiRequest) -> ApiResponse:
        build_id = request.body.get("build_id")
        if not build_id:
            return ApiResponse(400, {"error": "missing build_id"})
        build = self._repo.get(build_id)
        if not build:
            return ApiResponse(404, {"error": "build not found"})
        link = self._share_gen.generate(build.build_name, build.version)
        return ApiResponse(200, {"share_url": link.url, "build_id": link.build_id})

    def _get_build(self, request: ApiRequest, build_id: str) -> ApiResponse:
        build = self._repo.get_and_increment_views(build_id)
        if not build:
            return ApiResponse(404, {"error": "build not found"})
        return ApiResponse(
            200,
            {
                "build": {
                    "id": build.build_id,
                    "name": build.build_name,
                    "class": build.character_class,
                    "version": build.version,
                    "views": build.view_count,
                }
            },
        )
