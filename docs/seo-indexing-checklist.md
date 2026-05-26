# SEO Indexing Checklist (pokhi.in)

Use this checklist after each production deployment.

## 1) Technical Validation

1. Confirm `https://pokhi.in/` redirects to `https://pokhi.in/blog`.
2. Confirm `https://pokhi.in/blogs` redirects to `https://pokhi.in/blog`.
3. Confirm `https://pokhi.in/robots.txt` is reachable and references `https://pokhi.in/sitemap.xml`.
4. Confirm `https://pokhi.in/sitemap.xml` is reachable and includes `/blog` and blog detail URLs.

## 2) Search Console Submission

1. Open Google Search Console for the `pokhi.in` property.
2. Submit sitemap URL: `https://pokhi.in/sitemap.xml`.
3. Use URL Inspection for:
   - `https://pokhi.in/blog`
   - Two to three recent blog detail URLs
4. Request indexing if status is not yet indexed.

## 3) Bing Webmaster Submission

1. Open Bing Webmaster Tools for the `pokhi.in` site.
2. Submit sitemap URL: `https://pokhi.in/sitemap.xml`.
3. Run URL inspection for `/blog` plus sample blog detail URLs.

## 4) Weekly Monitoring

1. Check indexing coverage and crawl errors in both Google and Bing.
2. Fix canonical or redirect issues immediately.
3. Re-run `npm run seo:generate-sitemap` whenever blog content changes.
