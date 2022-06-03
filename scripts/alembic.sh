#!/bin/sh

docker compose run --rm keyword-bot ./.venv/bin/alembic "$@"
