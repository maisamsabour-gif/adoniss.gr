# Structured Data Recommendations

Add JSON-LD blocks per template type:

- Organization / LocalBusiness:
  - name, logo, url, address, telephone, sameAs
- BreadcrumbList:
  - for blog posts and internal pages
- Article / BlogPosting:
  - headline, datePublished, dateModified, author, image, mainEntityOfPage
- FAQPage:
  - for FAQ sections where content is visible on page
- WebSite + SearchAction:
  - if site search exists

Implementation tips:

- Render JSON-LD via Django template blocks to keep business logic intact.
- Use absolute URLs.
- Keep data synchronized with admin-managed fields.
