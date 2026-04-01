"""
Domain models for the Python/Flask layer.

These are pure data objects — no DB, no HTTP.
All domain objects are constructed at the service boundary from validated
request data or from the data pipeline, then passed inward to engines.
"""
