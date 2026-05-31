# Basic Monitoring Baseline

- Use `docker compose ps` and `docker compose logs -f` for service health.
- Add uptime checks for:
  - `https://adoniss.gr/health/live/`
  - `https://adoniss.gr/health/ready/`
- Recommended stack (incremental):
  - Node Exporter + Prometheus + Grafana
  - cAdvisor for container metrics
  - Loki + Promtail for centralized logs
  - Sentry for Django exceptions
- Alert thresholds:
  - CPU > 80% for 10m
  - Memory > 85% for 10m
  - Disk free < 20%
  - DB connections > 80% of max
  - 5xx rate > 2% in 5m
