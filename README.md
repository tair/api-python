# api-python

This is a RESTful API designed to provide all the services required to support Phoenix subscriptions and partners. The API is written in Python using Django framework.

## Database environment check

To see which database the API is currently using (host, port, name, user; password is masked):

```bash
curl http://localhost:9000/env/database/
```

Response includes `database_url`, `host`, `port`, `name`, `user`, and `engine`.

## Docker

Set remote DB and Django secret in `.env` (e.g. `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `SECRET_KEY`), then:

```bash
docker-compose up
```

API: http://localhost:9000

## Migrations

To run migrations (with Docker Compose):

```bash
docker-compose run web python manage.py migrate
docker-compose run web python manage.py makemigrations subscription  # if needed
```

Confluence Links:
Subscription -> controls.py
https://phoenixbioinformatics.atlassian.net/wiki/x/C4D9Ig

## Cursor skills

Project-specific Cursor skills are authored under the `cursor-skill/` directory. To sync them into `.cursor/skills/` (so Cursor picks them up), run from the project root:

```bash
./cursor-skill/sync_cursor_skills.sh
```

If you get "Permission denied", run `chmod +x cursor-skill/sync_cursor_skills.sh` once.

Use `--link` to create symlinks instead of copying, so edits in `cursor-skill/` apply immediately.
