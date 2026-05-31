# Production Deployment Blueprint (ArvanCloud + Ubuntu 24.04)

This guide is generated for your existing Django project without changing business logic.

## 1) Recommended Server Specs

- **Minimum (MVP production):**
  - 4 vCPU
  - 8 GB RAM
  - 120 GB NVMe SSD
- **Recommended (real business / SEO-sensitive):**
  - 8 vCPU
  - 16 GB RAM
  - 250+ GB NVMe SSD
- **OS:** Ubuntu 24.04 LTS

## 2) Directory Layout (on server)

Use this structure:

```text
/opt/adoniss/
  adonis_site/                 # git repo (this project)
    Dockerfile
    docker-compose.yml
    .env.production
    deploy/
      docker/
      nginx/
      backup/
      scripts/
      security/
      monitoring/
```

## 3) First-Time Server Bootstrap

```bash
sudo apt update && sudo apt -y upgrade
sudo apt -y install ca-certificates curl gnupg lsb-release git ufw fail2ban

# Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
```

## 4) Clone Project and Prepare Secrets

```bash
sudo mkdir -p /opt/adoniss
sudo chown -R $USER:$USER /opt/adoniss
cd /opt/adoniss
git clone <YOUR_GIT_URL> adonis_site
cd adonis_site

cp .env.production.example .env.production
nano .env.production
```

Set strong values:
- `DJANGO_SECRET_KEY`
- `POSTGRES_PASSWORD`
- `ALLOWED_HOSTS=adoniss.gr,www.adoniss.gr`
- `CSRF_TRUSTED_ORIGINS=https://adoniss.gr,https://www.adoniss.gr`

## 5) SSL Strategy (choose one)

### Option A: Let's Encrypt on origin server

1. Start stack with HTTP config:
```bash
docker compose up -d db redis web nginx
```

2. Request cert:
```bash
docker run --rm \
  -v adoniss_certbot_certs:/etc/letsencrypt \
  -v adoniss_certbot_www:/var/www/certbot \
  certbot/certbot certonly --webroot \
  -w /var/www/certbot \
  -d adoniss.gr -d www.adoniss.gr \
  --email admin@adoniss.gr --agree-tos --no-eff-email
```

3. HTTPS config is already present in:
- `deploy/nginx/conf.d/adoniss.https.conf.example`

If you prefer Arvan origin cert, edit the SSL certificate paths in that file.

4. Enable HTTPS config and reload nginx:
```bash
cp deploy/nginx/conf.d/adoniss.https.conf.example deploy/nginx/conf.d/adoniss.https.conf
docker compose up -d --no-deps nginx
```

### Option B: Arvan SSL / CDN in front

Use Arvan origin certificate paths in `deploy/nginx/conf.d/adoniss.https.conf.example`, then:
```bash
cp deploy/nginx/conf.d/adoniss.https.conf.example deploy/nginx/conf.d/adoniss.https.conf
docker compose up -d --no-deps nginx
```

## 6) Arvan DNS (ip.gr domain) -> Server

At DNS provider for `adoniss.gr`:
- `A` record: `@` -> `<ARVAN_ORIGIN_SERVER_IP>`
- `A` record: `www` -> `<ARVAN_ORIGIN_SERVER_IP>`
- TTL: 300s during migration, later 3600s

At Arvan panel:
- Add domain
- Enable CDN/Proxy (optional but recommended)
- Enable WAF + bot protection
- Set SSL mode to Full (strict if possible)

## 7) Launch Production

```bash
docker compose pull
docker compose build web
docker compose up -d
docker compose ps
docker compose logs -f web
```

Healthchecks:
- `https://adoniss.gr/health/live/`
- `https://adoniss.gr/health/ready/`

## 8) Security Hardening

### UFW
```bash
bash deploy/security/ufw-setup.sh
```

### Fail2ban
```bash
sudo cp deploy/security/fail2ban/jail.local /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl restart fail2ban
sudo fail2ban-client status
```

## 9) Logging Strategy

- App logs: `docker compose logs web`
- Nginx logs: volume `nginx_logs`
- DB logs: `docker compose logs db`
- Keep logs centralized later (Loki/ELK recommended).

## 10) Daily PostgreSQL Backups

Backup container already runs daily.

Check backups:
```bash
docker compose exec backup ls -lah /backups
```

Manual backup:
```bash
docker compose exec backup sh -c 'TS=$(date -u +%Y%m%dT%H%M%SZ); pg_dump -h db -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > /backups/${POSTGRES_DB}_${TS}.sql.gz'
```

Restore:
```bash
export POSTGRES_USER=<user>
export POSTGRES_DB=<db>
bash deploy/backup/restore.sh /absolute/path/to/backup.sql.gz
```

## 11) Deploy / Update Safely

```bash
bash deploy/scripts/deploy.sh
```

This script:
- pulls latest code
- builds image
- runs migrations
- collects static
- restarts web/nginx with minimal disruption

## 12) Rollback Strategy

1. Roll code back:
```bash
bash deploy/scripts/rollback.sh <previous_commit_sha>
```
2. If needed, restore DB from backup.
3. Keep backward-compatible migrations whenever possible.

## 13) Zero-Downtime Notes

With single-host Compose, this is **near-zero downtime**, not perfect zero.
For real zero-downtime:
- move to Swarm/Kubernetes
- run at least 2 web replicas behind Nginx
- use blue/green deployment pattern

## 14) Production Settings Recommendations (current project)

Keep these in `.env.production`:
- `ENV=production`
- `DEBUG=0`
- `DB_ENGINE=postgres`
- strict `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`

Your project currently allows sqlite fallback. In production, enforce PostgreSQL only by env policy (already documented in this guide).

## 15) Static / Media

- Static: collected in volume `static_data`, served by Nginx with immutable cache.
- Media: volume `media_data`, served by Nginx with 30-day cache.
- Future scaling: move media to object storage (S3/Arvan object storage) + CDN.

## 16) SEO and Performance

- Keep sitemap cached and available.
- Keep `robots.txt` disallowing admin and internal endpoints.
- Add Brotli/gzip (Nginx already configured).
- Enable long cache headers for static assets.
- Use WebP/AVIF and responsive images.
- Add structured data (see `deploy/seo/structured-data-notes.md`).
- Add AI crawler friendliness (see `deploy/seo/ai-crawler-guidelines.md`).

## 17) Redis Future Readiness

Redis service is already in compose.
When ready:
- cache backend -> Redis
- queue -> Celery + Redis broker
- rate-limit -> Redis-based throttling

## 18) Brute-Force / Common Attack Protection

- Fail2ban (`sshd`, nginx filters)
- UFW (allow only 22/80/443)
- Django security headers
- strong passwords + 2FA for admin users
- optional: add `django-axes` for admin login rate-limit
- Arvan WAF rules for `/admin/` hardening

## 19) CI/CD Ready Structure

- Example GitHub Actions file at:
  - `deploy/cicd/github-actions-deploy.example.yml`
- Store secrets only in CI secret vaults, never in repository.

## 20) Secret Management Best Practice

- Do not commit `.env.production`
- Use:
  - Arvan secret manager (if available) OR
  - GitHub Actions Secrets + server-side `.env.production`
- Rotate `DJANGO_SECRET_KEY`, DB password, API keys periodically.
