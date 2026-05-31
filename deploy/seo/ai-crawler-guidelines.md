# AI Crawler Optimization Guidelines

- Keep `robots.txt` explicit:
  - allow public content
  - disallow admin/auth/private endpoints
- Provide clean canonical tags on all indexable pages.
- Ensure sitemap freshness and low error rates.
- Add machine-readable structured data (JSON-LD).
- Keep page titles/descriptions unique and content-rich.
- Avoid rendering critical content only via JS.
- Return consistent language/hreflang signals for multilingual pages.
- Maintain stable URLs and 301 on URL changes.

Optional:
- Add `llms.txt` and `llms-full.txt` once content policy is finalized.
