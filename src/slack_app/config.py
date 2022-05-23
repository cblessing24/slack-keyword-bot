import os


def get_postgres_uri() -> str:
    user = os.environ.get("DB_USER", "slack-app")
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "5432")
    password = os.environ.get("DB_PASSWORD", "abc123")
    db_name = os.environ.get("DB_NAME", "slack-app")
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
