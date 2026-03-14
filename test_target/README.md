# VulnSight Test Target Server

This local server is intentionally insecure so VulnSight scanners have a predictable target.

## Start

```bash
./scripts/start_test_server.sh
```

Service URL:

- `http://127.0.0.1:8081`

## Suggested scan targets in VulnSight

- General web scan target: `http://127.0.0.1:8081`
- SQLMap-oriented target: `http://127.0.0.1:8081/product?id=1`

## Included test surface

- Reflected input: `/search?q=test`
- SQL-like injectable query path: `/product?id=1`
- Exposed sensitive files: `/.env`, `/.git/config`
- Basic admin page: `/admin/`

Warning: Use this server only on localhost for testing.
