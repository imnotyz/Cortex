"""Add monthly_budget_usd and budget_alert_threshold to agent_defaults."""

from yoyo import step


def apply(conn):
    cursor = conn.execute("PRAGMA table_info(agent_defaults)")
    columns = [row[1] for row in cursor.fetchall()]
    if columns and "monthly_budget_usd" not in columns:
        conn.execute("ALTER TABLE agent_defaults ADD COLUMN monthly_budget_usd REAL DEFAULT NULL")
    if columns and "budget_alert_threshold" not in columns:
        conn.execute(
            "ALTER TABLE agent_defaults ADD COLUMN budget_alert_threshold REAL DEFAULT 0.8"
        )


def rollback(conn):
    pass


steps = [step(apply, rollback)]
