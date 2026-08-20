"""Add thumbnail_path column to library_items."""

from yoyo import step


def apply(conn):
    try:
        cursor = conn.execute("PRAGMA table_info(library_items)")
        columns = [row[1] for row in cursor.fetchall()]
        if columns and "thumbnail_path" not in columns:
            conn.execute("ALTER TABLE library_items ADD COLUMN thumbnail_path TEXT")
    except Exception:
        # library_items table may not exist yet (knowledge engine creates it lazily)
        pass


def rollback(conn):
    pass


steps = [step(apply, rollback)]
