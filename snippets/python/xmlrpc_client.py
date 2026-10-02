"""Talk to any Odoo from outside using XML-RPC (also what Power BI/ETL scripts use)."""
import xmlrpc.client

URL, DB, USER, API_KEY = "http://localhost:8069", "mydb", "admin", "<api-key-or-password>"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, API_KEY, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")


def call(model, method, *args, **kwargs):
    return models.execute_kw(DB, uid, API_KEY, model, method, list(args), kwargs)


if __name__ == "__main__":
    print(common.version())
    ids = call("res.partner", "search", [("is_company", "=", True)], limit=5)
    print(call("res.partner", "read", ids, fields=["name", "email"]))
    print(call("res.partner", "search_read", [("customer_rank", ">", 0)], fields=["name"], limit=3))
    new_id = call("res.partner", "create", {"name": "Test via RPC"})
    call("res.partner", "write", [new_id], {"phone": "123"})
    call("res.partner", "unlink", [new_id])
