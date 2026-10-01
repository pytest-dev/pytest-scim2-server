# Unreleased

- The package ships a `py.typed` marker, so type checkers use its annotations.
- The code is checked with mypy in strict mode.

# 0.2.0 - 2026-09-18

- **Breaking:** scim2-server 0.3.0 is now required. The `scim2_server_app` fixture returns a `SCIMApplication` serving the default schemas and resource types.
- Python 3.11 is now the minimum supported version.

# 0.1.6 - 2025-01-14

- Add the `scim2_server_object` fixture.

# 0.1.5 - 2025-05-14

- Add the `scim2_server_app` fixture.

# 0.1.4 - 2025-05-11

- Python package metadata update.

# 0.1.3 - 2025-03-28

- Option to disable the server request logging.

# 0.1.2 - 2025-01-27

- Initial GHA workflow.

# 0.1.1 - 2025-01-27

- The fixture returns a dataclass object instead of a tuple.

# 0.1.0 - 2025-01-27

- Initial release.
