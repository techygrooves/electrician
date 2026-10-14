# Bright Flow Services — Website

Static marketing website for Bright Flow Services, a residential and commercial electrical contractor in Florida.

Plain HTML5, CSS3 and vanilla JavaScript. There is no build step: upload the folder contents to any static host (e.g. Hostinger `public_html`) and `index.html` serves as the homepage. Double-clicking `index.html` locally also works.

## Structure

```
index.html                 Homepage
services.html              Services overview
services/*.html            One detail page per service:
                           residential: electrical-panel-upgrades, ev-charger-installation,
                           backup-generator-installation, lighting-and-fan-upgrades,
                           dedicated-electrical-circuits, smart-home-integration
                           commercial: new-construction-wiring, commercial-lighting-retrofits,
                           specialized-equipment-hookups, commercial-service-upgrades,
                           commercial-troubleshooting-repairs
residential.html           Residential electrical
commercial.html            Commercial electrical
about.html                 About
contact.html               Contact / booking (#booking anchor)
privacy.html, terms.html   Legal pages (content to be supplied)
404.html                   Not-found page (root-absolute paths, used by .htaccess)
assets/css/main.css        Global design system and shared components
assets/js/main.js          Header, dropdown, mobile menu, reveal animations
assets/images/             Logo, favicons, and social preview images (social/)
assets/images/photos/      Site photography (add your own, see below)
sitemap.xml, robots.txt    SEO (indexable pages only)
docs/SEO.md                SEO notes: keyword map, audit results, local SEO and launch checklist
tools/                     Development helpers (not needed by the live site): seo_audit.py, set_domain.py, optimize_images.py
assets/fonts/              Self-hosted Inter and Manrope variable fonts
.htaccess                  Apache/LiteSpeed config: 404, compression, caching, security headers
```

## Shared components

The header, mobile menu, footer and mobile call bar are the same markup on every page; change them on all pages together. Pages in `services/` use `../` relative paths.

Commercial patterns: `.bento` / `.svc-tile` (`--dark`, `--blue`, `--tint`), `.industry-grid`, `.audience-list`, `.consult` (consultation CTA). Commercial CTAs read "Request a Consultation".

Detail-page patterns: `.page-hero--media` (photo hero with an "at a glance" `.hero-panel`), `.split` / `.prose` / `.panel-card`, `.signs`, `.callout` (safety note), `.process--custom` (set `--steps`), `.faq` (native `<details>` accordion).

Main CSS patterns: `.btn` (`--primary`, `--ghost`, `--light`, `--white`), `.section`, `.section-head`, `.grid--2/3/4`, `.card` / `.service-card`, `.cta-band`, `.page-hero`, `.form` / `.field`, `.reveal` (scroll animation).

Fonts (Inter and Manrope, SIL Open Font License) are self-hosted in `assets/fonts/`; the site loads no third-party resources.

Accessible color tokens: use `--blue-ink` for blue text on light backgrounds and `--blue-btn` for blue fills behind white text (both meet WCAG AA). The brighter `--blue-500` is for icons, borders and large accents.

When CSS or JS changes, bump the `?v=` query string on the `main.css` / `main.js` links so browsers pick up the new file (they are cached for a month).

## Business details and the estimate form

Set everything once in `assets/js/main.js`:

```js
var BRIGHT_FLOW_CONTACT = {
  phone: "(407) 000-0000",
  email: "hello@yourdomain.com",
  address: "123 Example St, Orlando, FL 32801",
  hours: "Mon–Fri, 8am–5pm",
  formEndpoint: "https://formspree.io/f/yourFormId"
};
```

- **Phone / email:** every call button, header phone, footer contact line and email link stays hidden until set, so no placeholder is ever linked. The contact page shows "To be confirmed" in their place.
- **Address / hours:** replace the "To be confirmed" placeholders on the contact page.
- **formEndpoint:** where the Request an Estimate form is sent. The form POSTs `multipart/form-data` with `Accept: application/json` and treats any 2xx response as success. This works with hosted form services (e.g. Formspree, Basin, Getform) or your own server-side script (e.g. a PHP handler on Hostinger). You can also set `data-endpoint="…"` on the `<form>` in `contact.html` instead. **Never put API keys or secrets in this file**: it is public. Any secret belongs on the server that receives the form.
- While `formEndpoint` is empty, the form still validates input but tells the visitor that online requests aren't connected yet. It never shows a false "sent" message.

Once the phone and email are confirmed, also add `"telephone"` and `"email"` to the JSON-LD block in `index.html`.

### Form details

- Fields sent: `name`, `email`, `phone` (required), `service_type`, `service`, `location`, `description`, `contact_method`, plus `page` and `seconds_on_page`.
- `_gotcha` is a hidden honeypot field. If it is filled in, the submission is silently dropped. It is not sent to the endpoint.
- Service pages link to `contact.html?service=<page-name>#booking` and the residential and commercial pages to `?type=residential|commercial`, so the form arrives pre-filled.
- Logic lives in `assets/js/estimate-form.js`, which is loaded only on the contact page.

## Privacy Policy

`privacy.html` is a **draft**. Sections marked "Requires business review" and text in [brackets] must be completed by the business, ideally with a qualified professional. The page is set to `noindex` until it's final; remove that from `privacy.html` once it has been reviewed.

## Photography

Photo slots are already in the HTML as commented-out `<picture>` elements, so the live site never requests a missing image. Each slot shows a designed fallback until you enable it:

1. Create the optimized files (AVIF, WebP and JPEG at several widths) from one high-resolution photo:
   ```bash
   python3 tools/optimize_images.py my-photo.jpg hero --preset wide
   python3 tools/optimize_images.py kitchen.jpg residential --preset portrait
   python3 tools/optimize_images.py panel.jpg services/electrical-panel-upgrades --preset wide
   ```
2. In the page's HTML, find the `<!-- PHOTO SLOT "…"` comment for that slot and delete the opening `<!-- PHOTO SLOT … -->` line and the closing `-->` around its `<picture>` element.

| Slot | Page | Preset |
| --- | --- | --- |
| `hero` | Homepage hero (loaded with high priority) | wide (16:9) |
| `residential`, `commercial` | Homepage and About category cards (lazy-loaded) | portrait (4:5) |
| `residential-hero`, `commercial-hero` | Residential / Commercial page heroes | wide |
| `services/<page-name>` | Each service page hero | wide |

Use your own job photos or properly licensed images. Hero photos sit behind a dark overlay; keep the main subject toward the right. Photos in these slots are decorative backgrounds, so `alt=""` is correct; any photo added to body content needs a real description.

## Content waiting on verified information

Nothing below is published until it is confirmed:

- **Service area** (`index.html`, "Service area" section): add each verified county or city as `<li>…</li>` inside `<ul class="area-chips">`. The list stays hidden while empty.
- **Customer reviews** (`index.html`): the section is built but has the `hidden` attribute. Add genuine reviews using the commented template and remove `hidden`.
- **Licenses, insurance, ratings, years in business, customer counts**: intentionally not stated anywhere. Add them only once verified.
- **Emergency availability**: the commercial troubleshooting page does not promise 24/7 or immediate response. Add response details only once confirmed.
- **Free estimates**: CTAs say "Request an Estimate". Change to "Request a Free Estimate" only if free estimates are confirmed.

## Renamed pages

Earlier service URLs were renamed; `.htaccess` 301-redirects `panel-upgrades`, `generator-installation`, `lighting-fan-installation`, `commercial-wiring` and `electrical-troubleshooting` to their new pages.

## Domain and SEO

The site uses the placeholder domain `https://www.example.com` in canonical URLs, social tags, JSON-LD, `sitemap.xml` and `robots.txt`. When the real domain is confirmed:

```bash
python3 tools/set_domain.py https://www.yourdomain.com
python3 tools/seo_audit.py     # should report 0 errors
```

See `docs/SEO.md` for everything else (keyword map, structured data, local SEO and Google Business Profile, content ideas, launch checklist). When uploading to the host, `tools/` and `docs/` don't need to be uploaded; `.htaccess` blocks them if they are.

## Other placeholders

- Privacy Policy and Terms of Use text
