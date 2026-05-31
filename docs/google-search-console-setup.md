# Google Search Console Setup (adonisgroup.gr)

## 1) Add Property

1. Open [Google Search Console](https://search.google.com/search-console/).
2. Click **Add Property**.
3. Choose **Domain** property.
4. Enter: `adonisgroup.gr`.

## 2) Verify Domain via DNS

1. Copy the TXT verification record from Search Console.
2. In your DNS provider (or Arvan DNS), add TXT record for root (`@`).
3. Wait for DNS propagation (can take a few minutes to hours).
4. Back in Search Console, click **Verify**.

## 3) Submit Sitemap

1. In Search Console, open **Sitemaps**.
2. Submit:
   - `https://adonisgroup.gr/sitemap.xml`
3. Confirm status becomes **Success**.

## 4) Inspect Important URLs

Use **URL Inspection** for:

- `https://adonisgroup.gr/`
- `https://adonisgroup.gr/blog/`
- `https://adonisgroup.gr/greece-golden-visa/`
- `https://adonisgroup.gr/fa-new/`
- one Persian blog detail URL

## 5) Request Indexing

For newly updated critical pages:

1. Open URL Inspection.
2. Click **Test Live URL**.
3. Click **Request Indexing**.

## 6) Monitor Coverage / Indexing

In **Indexing > Pages**, monitor:

- Crawled – currently not indexed
- Discovered – currently not indexed
- Excluded by `noindex`
- Alternate page with proper canonical

Fix any accidental `noindex` or canonical mismatch first.

## 7) Monitor 404 and Soft-404

In **Indexing > Pages**:

- check **Not found (404)**
- check **Soft 404**

If URL changed, add 301 redirect (do not leave dead links).

## 8) Core Web Vitals

In **Experience > Core Web Vitals**:

- monitor LCP, CLS, INP
- prioritize mobile issues first
- validate fixes after deployment

## 9) Persian Pages Notes

- Ensure `/fa-new/` and related Persian pages remain in sitemap (unless draft/noindex).
- Keep canonical tags consistent with live URLs.
- Do not block CSS/JS/images in `robots.txt`.

## 10) Post-deploy Checklist

- `https://adonisgroup.gr/robots.txt` reachable
- `https://adonisgroup.gr/sitemap.xml` reachable
- sitemap contains key English and Persian URLs
- no accidental noindex on business pages
