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
assets/images/             Logo and favicon (SVG)
assets/images/photos/      Site photography (add your own, see below)
sitemap.xml, robots.txt    SEO
.htaccess                  Apache/LiteSpeed config: 404, compression, caching, security headers
```

## Shared components

The header, mobile menu, footer and mobile call bar are the same markup on every page; change them on all pages together. Pages in `services/` use `../` relative paths.

Commercial patterns: `.bento` / `.svc-tile` (`--dark`, `--blue`, `--tint`), `.industry-grid`, `.audience-list`, `.consult` (consultation CTA). Commercial CTAs read "Request a Consultation".

Detail-page patterns: `.page-hero--media` (photo hero with an "at a glance" `.hero-panel`), `.split` / `.prose` / `.panel-card`, `.signs`, `.callout` (safety note), `.process--custom` (set `--steps`), `.faq` (native `<details>` accordion).

Main CSS patterns: `.btn` (`--primary`, `--ghost`, `--light`, `--white`), `.section`, `.section-head`, `.grid--2/3/4`, `.card` / `.service-card`, `.cta-band`, `.page-hero`, `.form` / `.field`, `.reveal` (scroll animation).

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

The homepage, residential and commercial pages, and every service page have photo slots. Each shows a designed fallback until the image file exists, then fades the photo in automatically (with a dark overlay on the hero). Use your own job photos or properly licensed images:

| File | Used for | Suggested size |
| --- | --- | --- |
| `assets/images/photos/hero.jpg` | Homepage hero background | 2400 × 1600, subject on the right |
| `assets/images/photos/residential.jpg` | Residential category card | 1200 × 1500 |
| `assets/images/photos/commercial.jpg` | Commercial category card | 1200 × 1500 |
| `assets/images/photos/residential-hero.jpg` | Residential page hero | 2400 × 1400 |
| `assets/images/photos/commercial-hero.jpg` | Commercial page hero | 2400 × 1400 |
| `assets/images/photos/services/<page-name>.jpg` | Hero of each service page (e.g. `electrical-panel-upgrades.jpg`) | 2400 × 1400 |

Compress images (around 200–400 KB each) before uploading.

## Content waiting on verified information

Nothing below is published until it is confirmed:

- **Service area** (`index.html`, "Service area" section): add each verified county or city as `<li>…</li>` inside `<ul class="area-chips">`. The list stays hidden while empty.
- **Customer reviews** (`index.html`): the section is built but has the `hidden` attribute. Add genuine reviews using the commented template and remove `hidden`.
- **Licenses, insurance, ratings, years in business, customer counts**: intentionally not stated anywhere. Add them only once verified.
- **Emergency availability**: the commercial troubleshooting page does not promise 24/7 or immediate response. Add response details only once confirmed.
- **Free estimates**: CTAs say "Request an Estimate". Change to "Request a Free Estimate" only if free estimates are confirmed.

## Renamed pages

Earlier service URLs were renamed; `.htaccess` 301-redirects `panel-upgrades`, `generator-installation`, `lighting-fan-installation`, `commercial-wiring` and `electrical-troubleshooting` to their new pages.

## Other placeholders

- Domain `https://www.brightflowservices.com` (canonical URLs, JSON-LD, sitemap, robots.txt)
- Privacy Policy and Terms of Use text
