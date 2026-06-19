# SEO Indexing Checklist (quortol.pokhi.in)

Use this checklist after each production deployment.

## 1) Technical Validation

1. Confirm `https://quortol.pokhi.in/` redirects to `https://quortol.pokhi.in/blog`.
2. Confirm `https://quortol.pokhi.in/blogs` redirects to `https://quortol.pokhi.in/blog`.
3. Confirm `https://quortol.pokhi.in/robots.txt` is reachable and references `https://quortol.pokhi.in/sitemap.xml`.
4. Confirm `https://quortol.pokhi.in/sitemap.xml` is reachable and includes `/blog` and blog detail URLs.
5. Confirm any `pokhi.in` redirect preserves the full path and query string.

## 2) Search Console Submission

1. Open Google Search Console for the `quortol.pokhi.in` URL-prefix property.
2. Submit sitemap URL: `https://quortol.pokhi.in/sitemap.xml`.
3. Use URL Inspection for:
   - `https://quortol.pokhi.in/blog`
   - Two to three recent blog detail URLs
4. Request indexing if status is not yet indexed.

## 3) Bing Webmaster Submission

1. Open Bing Webmaster Tools for the `quortol.pokhi.in` site.
2. Submit sitemap URL: `https://quortol.pokhi.in/sitemap.xml`.
3. Run URL inspection for `/blog` plus sample blog detail URLs.

## 4) Weekly Monitoring

1. Check indexing coverage and crawl errors in both Google and Bing.
2. Fix canonical or redirect issues immediately.
3. Re-run `npm run seo:generate-sitemap` whenever blog content changes.
