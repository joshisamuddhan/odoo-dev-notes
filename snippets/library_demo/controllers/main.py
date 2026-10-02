import functools
import json
import logging

from odoo import http
from odoo.exceptions import AccessError, ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)

JSON_HEADERS = [("Content-Type", "application/json")]


def json_response(payload, status=200):
    return request.make_response(json.dumps(payload, default=str), headers=JSON_HEADERS, status=status)


def error(message, code="BAD_REQUEST", status=400, details=None):
    return json_response(
        {"status": "error", "error_code": code, "message": message, "details": details or {}}, status
    )


def api_key_required(func):
    """Validate 'Authorization: Bearer <odoo api key>' and run the request as that user."""

    @functools.wraps(func)  # keeps __name__/__doc__: http.route inspects the function
    def wrapper(self, *args, **kwargs):
        header = request.httprequest.headers.get("Authorization", "")
        token = header[7:] if header.lower().startswith("bearer ") else header
        if not token:
            return error("Missing API key", "UNAUTHORIZED", 401)
        uid = request.env["res.users.apikeys"]._check_credentials(scope="rpc", key=token)
        if not uid:
            return error("Invalid API key", "UNAUTHORIZED", 401)
        request.update_env(user=uid)  # ORM + ACLs/record rules now apply as this user
        return func(self, *args, **kwargs)

    return wrapper


class LibraryAPI(http.Controller):

    def _serialize(self, book):
        return {
            "id": book.id, "name": book.name, "isbn": book.isbn,
            "author": book.author, "price": book.price, "state": book.state,
        }

    def _body(self):
        try:
            return json.loads(request.httprequest.data.decode() or "{}")
        except ValueError:
            return None

    @http.route("/api/library/books", type="http", auth="none", methods=["GET"], csrf=False)
    @api_key_required
    def list_books(self, limit=20, offset=0, **kw):
        try:
            limit, offset = min(int(limit), 100), max(int(offset), 0)
        except ValueError:
            return error("limit/offset must be integers", "VALIDATION_ERROR", 422)
        Book = request.env["library.book"]
        domain = [("state", "=", kw["state"])] if kw.get("state") else []
        total = Book.search_count(domain)
        books = Book.search(domain, limit=limit, offset=offset)
        return json_response({
            "status": "success", "total": total, "limit": limit, "offset": offset,
            "data": [self._serialize(b) for b in books],
        })

    @http.route("/api/library/books/<int:book_id>", type="http", auth="none", methods=["GET"], csrf=False)
    @api_key_required
    def get_book(self, book_id):
        book = request.env["library.book"].browse(book_id).exists()
        if not book:
            return error("Book not found", "NOT_FOUND", 404)
        return json_response({"status": "success", "data": self._serialize(book)})

    @http.route("/api/library/books", type="http", auth="none", methods=["POST"], csrf=False)
    @api_key_required
    def create_book(self, **kw):
        body = self._body()
        if body is None:
            return error("Invalid JSON", "BAD_REQUEST", 400)
        if not body.get("name"):
            return error("'name' is required", "VALIDATION_ERROR", 422)
        allowed = {k: body[k] for k in ("name", "isbn", "author", "price") if k in body}  # whitelist
        try:
            with request.env.cr.savepoint():
                book = request.env["library.book"].create(allowed)
        except (ValidationError, Exception) as e:  # narrow this in real code
            return error(str(e), "VALIDATION_ERROR", 422)
        return json_response({"status": "success", "data": self._serialize(book)}, 201)

    @http.route("/api/library/books/<int:book_id>", type="http", auth="none", methods=["PUT"], csrf=False)
    @api_key_required
    def update_book(self, book_id, **kw):
        body = self._body() or {}
        book = request.env["library.book"].browse(book_id).exists()
        if not book:
            return error("Book not found", "NOT_FOUND", 404)
        try:
            book.write({k: body[k] for k in ("name", "author", "price") if k in body})
        except AccessError as e:
            return error(str(e), "FORBIDDEN", 403)
        return json_response({"status": "success", "data": self._serialize(book)})

    @http.route("/api/library/books/<int:book_id>", type="http", auth="none", methods=["DELETE"], csrf=False)
    @api_key_required
    def delete_book(self, book_id):
        book = request.env["library.book"].browse(book_id).exists()
        if not book:
            return error("Book not found", "NOT_FOUND", 404)
        book.unlink()
        return json_response({"status": "success"}, 200)
