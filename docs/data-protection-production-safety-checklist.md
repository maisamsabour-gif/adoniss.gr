# ADONIS Data Protection & Production Safety Baseline

This document tracks implementation status for the requested baseline and points to code locations.

## A) Data Safety

### 1) Soft delete (implemented)
- Implemented reusable soft delete stack:
  - `core/safety.py`
- Applied to critical models:
  - `properties.models.Property`
  - `properties.models.PropertyUnit`
  - `properties.models.UnitBooking`
  - `properties.models.PropertyInterest`
  - `core.models.ContactSubmission`
  - `core.models.ChatLead`
  - `core.models.Customer` (new)
  - `core.models.ChatMessage` (new)
- Default manager now returns active records; `all_objects` returns active + archived.
- Admin hard delete disabled and replaced by archive/restore actions:
  - `core/admin_mixins.py`
  - `core/admin.py`
  - `properties/admin.py`
  - Confirmation template: `adonis/templates/admin/soft_delete_confirmation.html`

### 2) Prevent destructive cascades (implemented)
- Replaced critical `CASCADE` FKs with safer policies:
  - `PropertyInterest.property` -> `PROTECT`
  - `PropertyUnit.property` -> `PROTECT`
  - `UnitBooking.unit` -> `PROTECT`
  - `PropertyImage.property` -> `PROTECT`
- Added explicit hard-delete safeguards:
  - `Property.hard_delete()` blocks when bookings exist.
  - `PropertyUnit.hard_delete()` blocks when bookings exist.
- Deleting `Property` / `PropertyUnit` now archives children (not hard-delete).

### 3) Block destructive management commands in production (implemented)
- `manage.py` now blocks dangerous commands in production unless explicitly overridden:
  - blocked: `flush`, `sqlflush`, `reset_db`, `resetdb`, `dropdb`, `cleardb`
  - override only with `ALLOW_DESTRUCTIVE_COMMANDS=1`

### 4) Constraints, indexes, validation (implemented)
- Added indexes for high-volume lookups on critical models.
- Added uniqueness constraint:
  - active `unit_label` unique per `property` (`PropertyUnit`).
- Added booking duplicate/pending validation:
  - `UnitBooking.clean()` and `save()` with `full_clean()`.

## B) Backups & Restore

### 5) Automated backups (implemented in code)
- Command: `python manage.py backup_db --label daily`
- Supports sqlite/postgres backup and optional S3 upload.
- Retention policy implemented (local + S3): `BACKUP_RETENTION_DAYS` (default 30).
- Files:
  - `core/management/commands/backup_db.py`
  - settings keys in `adonis/settings.py`

### 6) Restore drill (implemented in code)
- Restore command:
  - `python manage.py restore_backup --local-file /path/to/backup.gz`
  - or `--s3-key <key>`
  - includes `--dry-run`
- Post-restore verification drill:
  - `python manage.py restore_drill`
- Files:
  - `core/management/commands/restore_backup.py`
  - `core/management/commands/restore_drill.py`

### 7) Media persistence safety (implemented in code + env-driven)
- Upload path now uses Django storage backend (no hardcoded filesystem writes):
  - `core/views.py` (`upload_video`)
- Optional S3 media backend support:
  - `adonis/storage_backends.py`
  - `USE_S3_MEDIA=1` configuration in `adonis/settings.py`

## C) Environments & Deploy Safety

### 8) Separate environments (implemented baseline)
- Added `ENV` and `DB_ENV_TAG` safety check in `adonis/settings.py`.
- Environment/DB mismatch raises `ImproperlyConfigured`.

### 9) Safe migration policy (implemented as process + structure)
- Models and constraints were introduced with additive schema changes.
- For future risky changes, use phased nullable -> backfill -> enforce strategy.
- This baseline includes migration-safe design notes and predeploy checks.

### 10) Deployment checks (implemented)
- Command: `python manage.py predeploy_check`
- Verifies:
  - recent backup marker exists/fresh
  - DB connectivity
  - no pending migrations
  - dangerous admin bulk delete action disabled
- File: `core/management/commands/predeploy_check.py`

## D) Security & Privacy

### 11) RBAC for admin/dashboard (implemented baseline)
- Role constants/helpers:
  - `core/rbac.py`
- Group seeding command:
  - `python manage.py seed_rbac_roles`
  - `core/management/commands/seed_rbac_roles.py`
- Sensitive admin pages restricted by roles in:
  - `core/admin.py`
  - `properties/admin.py`
- Dashboard access now role-gated:
  - `core/views.py` (`_can_access_dashboard`)

### 12) PII handling + HTTPS (implemented baseline)
- Phone masking for non-privileged roles in admin list views:
  - contacts, chat leads, property interests, bookings, customers
- Log PII redaction filter:
  - `core/logging_filters.py`
  - logging config in `adonis/settings.py`
- HTTPS/security headers in production:
  - `SECURE_SSL_REDIRECT`, HSTS, secure cookies, referrer policy

### 13) Rate limiting + anti-spam + validation (implemented baseline)
- Added endpoint rate limiting:
  - `core/rate_limit.py`
  - applied in `core/views.py`, `properties/views.py`
- Removed `csrf_exempt` from chat lead endpoint; JS now sends CSRF header:
  - `core/views.py`
  - `adonis/static/js/main.js`
- Added server-side phone validation and honeypot handling:
  - `core/forms.py`, `core/views.py`, `properties/views.py`

### 14) Secrets management (implemented baseline)
- Moved key runtime secrets to environment-variable flow:
  - `DJANGO_SECRET_KEY`, DB creds, S3 creds, Sentry DSN
- Added `.env.example`.
- **Operational required follow-up:** rotate any previously exposed secrets outside code deployment.

## E) Audit, Logging, Monitoring

### 15) Audit log (implemented baseline)
- New model: `core.models.AuditLog`
- Utility logger:
  - `core/audit.py`
- Hooks:
  - admin create/update/archive/restore via `core/admin_mixins.py`
  - public lead/booking/contact/chat create events in views
- Captures actor, timestamp, IP, action, object ref, before/after snapshots.

### 16) Error monitoring (implemented baseline)
- Optional Sentry integration if `SENTRY_DSN` set:
  - `adonis/settings.py`

### 17) Health/readiness checks (implemented)
- Endpoints:
  - `/health/live/`
  - `/health/ready/`
- Files:
  - `core/views.py`
  - `core/urls.py`

## F) Admin Panel Hardening

### 18) Prevent accidental mass deletion (implemented baseline)
- Disabled `delete_selected` globally:
  - `core/admin.py`
  - `properties/admin.py`
- Added explicit archive/restore actions with confirmation page:
  - `core/admin_mixins.py`
  - `adonis/templates/admin/soft_delete_confirmation.html`
- Hard delete blocked for protected models via admin mixin (`has_delete_permission=False`).

---

## Operational Runbook Snippets

### Daily and 6-hour backup schedule (cron example)
```bash
# every day at 02:15
15 2 * * * /path/to/venv/bin/python /root/adonis_site/manage.py backup_db --label daily

# every 6 hours
5 */6 * * * /path/to/venv/bin/python /root/adonis_site/manage.py backup_db --label 6h
```

### Staging restore drill
1. Restore latest backup to staging:
   - `python manage.py restore_backup --s3-key <latest-key>`
2. Run verification:
   - `python manage.py restore_drill`
3. Verify critical pages manually:
   - `/`, `/properties/`, `/admin/login/`, `/health/ready/`
