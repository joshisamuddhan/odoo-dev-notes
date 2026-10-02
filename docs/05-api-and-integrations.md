# REST APIs & Integrations (the strongest area on your resume — expect a task here)

Working reference implementation (tested on Odoo 18): `../snippets/library_demo/controllers/main.py`
Python helpers: `../snippets/python/` (retry, pagination, HMAC, rate limiter, XML-RPC client).

## Design checklist
- **Resources as nouns**: `/api/library/books`, `/api/library/books/<id>`; verbs by HTTP method.
- Methods: GET read (safe, idempotent) · POST create (not idempotent) · PUT replace/update (idempotent) · PATCH partial · DELETE (idempotent).
- Status codes: `200` OK · `201` created · `204` no content · `400` malformed (bad JSON) · `401` missing/invalid credentials · `403` authenticated but not allowed · `404` not found · `409` conflict (duplicate/state) · `422` valid JSON but fails validation · `429` too many requests · `500` our bug · `502/503/504` upstream/overload.
- Consistent envelope: `{"status": "success|error", "error_code": "VALIDATION_ERROR", "message": "...", "data": {...}}`.
- **Validate inputs** (whitelist writable fields; never `create(body)` with raw client dict).
- **Pagination**: `limit` (cap it), `offset`, return `total`. Cursor pagination for huge/changing data.
- **Idempotency** for retries: unique external reference (`external_id`/`UBL_ID`), or `Idempotency-Key` header; lookup-before-create.
- **Bulk endpoints**: per-item `savepoint` + per-item result; return 200/207 with results list. Very large → async job + poll.
- **Auth**: API key (`res.users.apikeys`) in `Authorization: Bearer`; run as that user (ACL/rules apply). JWT/OAuth for third parties. Never log secrets; HTTPS only.
- **Versioning**: `/api/v1/...`; add optional fields without breaking clients.
- **Docs**: put curl examples in README (below).
- **Webhooks (inbound)**: verify HMAC on raw body, respond fast (200) and process async, dedupe by event id.
- **Outbound calls**: timeout always, retry only 5xx/timeouts/429 with backoff, never retry 4xx, log request ids, one record failing must not stop the batch.
- **Polling vs webhooks**: polling = simple, delays; webhooks = real-time, need public endpoint + verification + retries.

## Odoo controller anatomy
```python
@http.route("/api/x", type="http", auth="none", methods=["POST"], csrf=False)
@api_key_required
def create(self, **kw):
    body = json.loads(request.httprequest.get_data() or "{}")     # client must send Content-Type: application/json
    ...
    return json_response({...}, 201)
```
- `type="json"`: body must be JSON-RPC `{"jsonrpc":"2.0","method":"call","params":{...}}` and response is wrapped in `{"result": ...}`. Fine for Odoo's own JS; awkward for third parties → prefer `type="http"` for REST.
- `auth="user"` → needs session cookie; `auth="public"` → anonymous but with env; `auth="none"` → you authenticate yourself (API key).
- CORS: `cors="*"` on route + handle OPTIONS if browser clients.

## curl test snippets (put in README)
```bash
KEY=<api key>   # Odoo: avatar > Preferences > Account Security > New API Key
curl -s localhost:8069/api/library/books -H "Authorization: Bearer $KEY"
curl -s -X POST localhost:8069/api/library/books -H "Authorization: Bearer $KEY" \
     -H "Content-Type: application/json" -d '{"name":"Dune","isbn":"A-1","price":12}'
curl -s -X PUT localhost:8069/api/library/books/5 -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" -d '{"price":15}'
curl -i -X DELETE localhost:8069/api/library/books/5 -H "Authorization: Bearer $KEY"
```
Postman: Authorization tab → Bearer Token; Body → raw → JSON.
Create a key in code (shell): `env['res.users.apikeys'].with_user(2)._generate('rpc', 'name', None)`.

## Odoo external APIs (to consume Odoo from outside)
- XML-RPC `/xmlrpc/2/common` (`version`, `authenticate`) + `/xmlrpc/2/object` (`execute_kw`) — see `snippets/python/xmlrpc_client.py`.
- JSON-RPC `/jsonrpc` (`service: object, method: execute_kw`). Newer versions also document a JSON-2 external API — check the docs if the task names it.
- Methods: `search, read, search_read, create, write, unlink, fields_get, name_search`, `search_count`, any public method.

## Integration (sync) pattern — marketplace-style
1. Config model (singleton): URL, key via `ir.config_parameter` or password field with `groups`.
2. Push on events (override `write`/`create` or server action) · pull via cron (`ir.cron`).
3. Mapping fields: store `external_id` (indexed) on the Odoo record for idempotent upsert.
4. Per-record try/except + savepoint; collect errors; notify via chatter/`bus` notification; commit per batch in cron.
5. Log table or `message_post` for audit; manual "sync now" button; "last sync" timestamp.
6. Conflict policy: define source of truth per field (Odoo owns orders/stock; remote owns tracking).
7. Rate limiting & timeouts (`requests.get(url, timeout=30)`), retries with backoff (`snippets/python/decorators.py`).

## Third-party libs
`requests` (HTTP) · `urllib3.Retry` + `HTTPAdapter` for retries · `zeep` SOAP · `pandas` for CSV/XLSX · `xlsxwriter` Excel output · `cryptography`/`hmac` signatures · `paramiko`/`sshtunnel` SFTP/SSH.
Odoo import of external libs: add to `external_dependencies = {"python": ["requests"]}` in manifest.
