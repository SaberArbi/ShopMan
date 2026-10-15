# Contributing

Thanks for considering a contribution! 🎉

## Setup

```bash
git clone https://github.com/<your-username>/stock-manager.git
cd stock-manager
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Ground rules

1. **Open an issue first** for anything bigger than a bug fix.
2. **One concern per PR** — keep diffs focused and reviewable.
3. **Don't break i18n.** Every user-facing string must go through `t("key")`
   and exist in all three languages (`en`, `fr`, `ar`) in `utils/i18n.py`.
4. **Never commit** `stock.db`, `backups/`, `reports/`, or `.idea/`.
5. **Don't drop tables in `create_tables()`** — it's destructive. Migrate instead.

## Code style

- PEP 8, 4-space indent, ~88 cols.
- Type hints welcome but not required.
- Keep SQL in `database/db_operations.py` — screens should not run raw SQL.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(sales): add quantity discount
fix(products): crash when photo path is missing
docs(readme): add demo GIF
```

## Reporting bugs

Please include:
- OS + Python version
- Steps to reproduce
- Expected vs. actual behaviour
- Traceback if available