#!/bin/bash
set -e

rsync \
    -av \
    --delete \
    --exclude=".git" \
    --exclude="tests" \
    --exclude="alembic*" \
    --exclude="reports" \
    --exclude="slack" \
    --filter="dir-merge,- .gitignore" \
    "$PWD" slack-app:
ssh slack-app sudo /bin/systemctl restart slack-app.service
