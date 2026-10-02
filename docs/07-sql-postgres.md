# SQL & PostgreSQL for Odoo

## Odoo table facts
Model `account.move` → table `account_move`; many2one = `<field>_id` column; many2many = `a_b_rel` table; `create_date/write_date/create_uid/write_uid` always exist; translatable fields are `jsonb` (v16+): `name->>'en_US'`.
Useful tables: `res_partner, res_users, sale_order(_line), account_move(_line), product_product/template, stock_move(_line), ir_model_data (xmlids), ir_module_module, ir_config_parameter`.

## Query patterns
```sql
-- top 5 partners by invoiced amount last 12 months
SELECT p.name, SUM(m.amount_total) AS total
FROM account_move m JOIN res_partner p ON p.id = m.partner_id
WHERE m.move_type = 'out_invoice' AND m.state = 'posted'
  AND m.invoice_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY p.name ORDER BY total DESC LIMIT 5;

-- latest row per group (window function)
SELECT * FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY date DESC) rn FROM price_history
) t WHERE rn = 1;

-- running total
SELECT date, SUM(amount) OVER (ORDER BY date) FROM payments;

-- duplicates
SELECT email, COUNT(*) FROM res_partner GROUP BY email HAVING COUNT(*) > 1;

-- rows with no children (anti-join)
SELECT p.id FROM res_partner p WHERE NOT EXISTS (SELECT 1 FROM sale_order s WHERE s.partner_id = p.id);

-- CTE
WITH monthly AS (SELECT date_trunc('month', invoice_date) m, SUM(amount_total) t FROM account_move GROUP BY 1)
SELECT m, t, t - LAG(t) OVER (ORDER BY m) AS delta FROM monthly;

-- upsert
INSERT INTO t (id, name) VALUES (1,'x') ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;
```
Joins: INNER (both) · LEFT (all left) · RIGHT · FULL · CROSS. `WHERE` filters rows, `HAVING` filters groups. `COUNT(*)` vs `COUNT(col)` (non-null). `UNION` dedupes, `UNION ALL` doesn't.
`COALESCE(a,b)`, `NULLIF`, `CASE WHEN`, `ILIKE`, `date_trunc`, `EXTRACT`, `string_agg`, `array_agg`, `jsonb ->>`.

## Performance
- `EXPLAIN (ANALYZE, BUFFERS) <query>`: look for **Seq Scan on big table** (missing index), estimated vs actual rows far apart (stale stats → `ANALYZE`), **Sort Method: external merge Disk** (raise `work_mem`), Nested Loop with huge loops, high `Buffers: read`.
- Index: btree (equality/range/sort), GIN trigram (`pg_trgm`) for `ILIKE '%x%'`, partial index, composite order = equality columns first. Cost: slower writes + disk. Odoo: `index=True` on field (v16+: `index="btree"`, `"btree_not_null"`, `"trigram"`).
- `pg_stat_statements` → slowest queries · `pg_stat_activity` → what's running/locks · `VACUUM (ANALYZE)` · autovacuum tuning.
- Odoo side: avoid N+1 (search in loop), `read_group`, `mapped`, store computed fields you filter/group on, batching, pagination.
- Config pointers: `shared_buffers` ≈ 25% RAM, `effective_cache_size` ≈ 50–75% RAM, `work_mem` per sort per connection (careful), `max_connections` vs PgBouncer, `random_page_cost` 1.1 on SSD.

## Safety
- Parameterise: `cr.execute("... WHERE id = %s", (id,))` / `IN %s` with tuple `(tuple(ids),)`.
- Read-only in tasks unless needed; after raw writes `self.env.invalidate_all()`; raw SQL bypasses ACL/rules/ORM triggers.
- Use transactions & backups before destructive SQL: `BEGIN; ...; ROLLBACK/COMMIT;`
