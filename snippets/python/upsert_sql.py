"""Safe parameterised UPSERT builder (never f-string VALUES into SQL)."""
from psycopg2 import sql


def build_upsert(table, data: dict, conflict_col="id"):
    cols = list(data)
    query = sql.SQL(
        "INSERT INTO {t} ({c}) VALUES ({v}) ON CONFLICT ({k}) DO UPDATE SET {u}"
    ).format(
        t=sql.Identifier(table),
        c=sql.SQL(", ").join(map(sql.Identifier, cols)),
        v=sql.SQL(", ").join(sql.Placeholder() * len(cols)),
        k=sql.Identifier(conflict_col),
        u=sql.SQL(", ").join(
            sql.SQL("{0} = EXCLUDED.{0}").format(sql.Identifier(c)) for c in cols if c != conflict_col
        ),
    )
    return query, [data[c] for c in cols]
# cur.execute(*build_upsert("res_partner", {"id": 1, "name": "X"}))
