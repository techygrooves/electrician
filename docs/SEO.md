# SEO implementation notes — Bright Flow Services

This document records what has been implemented, what still depends on business information, and how to keep the site consistent. SEO work improves how clearly search engines can understand and present the site; it does not guarantee rankings, and structured data does not guarantee rich results.

---

## 1. Before launch: required information

| Item | Where it goes | Status |
| --- | --- | --- |
| Production domain | `python3 tools/set_domain.py https://www.yourdomain.com` updates canonicals, Open Graph/Twitter URLs, JSON-LD, `sitemap.xml`, `robots.txt` and the `.htaccess` host rule | **Placeholder** `https://www.example.com` |
| Phone, email | `assets/js/main.js` (`BRIGHT_FLOW_CONTACT`) **and** the business JSON-LD in `index.html` (`telephone`, `email`) | Not provided |
| Business address | Contact page config **and** JSON-LD `address` (street, city, ZIP), only if the address is public | Not provided |
| Business hours | Config **and** JSON-LD `openingHoursSpecification` | Not provided |
| Cities / counties served | Homepage service-area list (`<ul class="area-chips">`) and JSON-LD `areaServed` | Not provided (currently "Florida") |
| Google Business Profile URL | JSON-LD `sameAs` | Not provided |
| License number | Only if the business wants it displayed | Not provided |

**Never add** ratings, review counts, geo-coordinates, hours, or credentials to the markup until they are real and verifiable.

After any change, run:

```bash
python3 tools/seo_audit.py
```

---

## 2. Keyword map

One primary theme per page avoids pages competing with each other. City names are intentionally **not** used yet; add them only after service areas are confirmed (see §5).

| Page | Primary theme | Supporting terms used naturally in copy |
| --- | --- | --- |
| `/` | Electrical contractor Florida | residential and commercial electrician, panel upgrades, EV chargers |
| `/residential.html` | Residential electrician Florida | home electrical services, panel upgrade, EV charger, generator |
| `/commercial.html` | Commercial electrician Florida | commercial electrical contractor, build-outs, LED retrofits |
| `/services.html` | Electrical services Florida | residential and commercial service overview |
| `/services/electrical-panel-upgrades.html` | Electrical panel upgrade, 200 amp panel upgrade | breaker box replacement, 100 to 200 amp service |
| `/services/ev-charger-installation.html` | EV charger installation | Level 2 home charging, 240-volt circuit |
| `/services/backup-generator-installation.html` | Home generator installation | standby generator, transfer switch, hurricane season |
| `/services/lighting-and-fan-upgrades.html` | LED lighting installation | recessed lighting, dimmers, ceiling fans, exhaust fans |
| `/services/dedicated-electrical-circuits.html` | Dedicated circuit installation | hot tub, sauna, appliance, workshop circuits |
| `/services/smart-home-integration.html` | Smart home electrical installation | smart thermostat, smart switches, video doorbell |
| `/services/new-construction-wiring.html` | Commercial electrical wiring | new construction, tenant build-out, data infrastructure |
| `/services/commercial-lighting-retrofits.html` | Commercial lighting retrofit | fluorescent to LED, occupancy sensors |
| `/services/specialized-equipment-hookups.html` | Commercial equipment hookups | commercial kitchen, HVAC, three-phase |
| `/services/commercial-service-upgrades.html` | Commercial electrical service upgrade | load assessment, capacity expansion |
| `/services/commercial-troubleshooting-repairs.html` | Electrical troubleshooting (commercial) | tripping breakers, flickering lights, power loss |
| `/about.html` | Brand / Florida electrical contractor | approach, values |
| `/contact.html` | Request an electrical estimate | contact, consultation |

---

## 3. What is implemented

**On-page**
- Unique `<title>` (≤ 65 characters) and meta description (70–160 characters) on every page.
- Exactly one `<h1>` per page and no skipped heading levels (verified by `tools/seo_audit.py`).
- Descriptive, crawlable `<a href>` navigation: header, mega menu, footer columns, breadcrumbs, related-service cards.
- Contextual in-copy links between related services (for example, panel upgrades ↔ EV chargers ↔ dedicated circuits; commercial service upgrades ↔ equipment hookups ↔ troubleshooting) with descriptive anchor text.
- Images: every `<img>` has an `alt` attribute. The current photo slots are decorative backgrounds behind text, so they use `alt=""`. **When you add real photos that carry meaning (e.g., a project photo in content), write an alt description of what the photo actually shows.**

**Technical**
- Absolute canonical URL on every indexable page. The homepage canonical is `/` and `.htaccess` 301-redirects `/index.html` to `/` to prevent duplicate homepage URLs.
- A commented `.htaccess` rule forces one host (https + www) once the domain and SSL are live.
- `robots` meta: `index, follow` on all production pages. **Intentionally `noindex`:** `404.html`, `privacy.html` (draft pending business review) and `terms.html` (placeholder). Once the legal pages are final, remove their `noindex`, add a canonical tag, and add them to `sitemap.xml`. The audit script will flag anything that's out of step.
- `sitemap.xml` lists only the 17 indexable pages, with the homepage as `/`.
- `robots.txt` allows crawling, disallows `/tools/` and `/docs/`, and references the sitemap.
- Useful `404.html` with root-relative links (works at any URL depth), configured via `ErrorDocument`.
- 301 redirects for previously renamed service URLs.

**Structured data (JSON-LD)**
- Homepage: one business entity typed `Organization` + `Electrician` (`@id …/#business`) with name, URL, logo, description, `areaServed: Florida`, region/country only, plus an offer catalog of services; and `WebSite` (`@id …/#website`).
- Every interior page: `BreadcrumbList`.
- Service pages: `Service` (name, type, description, audience, `areaServed`, provider → `#business`) and `FAQPage` for the on-page FAQs.
- Residential and commercial hubs: `OfferCatalog` + `FAQPage`. About: `AboutPage`. Contact: `ContactPage`.
- Validate after launch with Google's Rich Results Test and the Schema.org validator. Google currently shows FAQ rich results only for a limited set of sites, so FAQ markup is there for clarity, not an expected search feature.

**Social sharing**
- Open Graph (`og:title`, `og:description`, `og:url`, `og:type`, `og:image` with size and alt) and Twitter/X `summary_large_image` tags on every page.
- Preview images (1200×630): `assets/images/social/og-default.jpg` (home, hub, about, contact), `og-residential.jpg` (residential pages), `og-commercial.jpg` (commercial pages). Replace them with branded photography later if you like; keep the file names and size.
- PNG icons: `favicon-32.png`, `apple-touch-icon.png`, and `logo-512.png` (used as the structured-data logo).

---

## 4. SEO audit results

`tools/seo_audit.py` checks titles, descriptions, canonicals, robots directives, H1 count, heading order, internal links and anchors, alt attributes, social tags, JSON-LD syntax/required fields, and sitemap/robots consistency.

**Before this pass (20 HTML pages): 32 errors, 13 warnings**

| Finding | Pages | Fix |
| --- | --- | --- |
| Missing `og:image` / Twitter image | all 20 | Added 1200×630 preview images and full OG/Twitter tags |
| `Service` items without `provider` | home, residential, commercial offer catalogs | Every Service now references the `#business` provider |
| Heading level skipped (h1 → h3) | home and commercial trust strips | Added a visually hidden `<h2>` to each strip |
| Sitemap listed a `noindex` page | `privacy.html` | Sitemap now generated from indexable pages only |
| Meta descriptions over 160 characters | 7 pages | Rewritten (all now 120–160) |
| Titles over 65 characters | 4 pages | Rewritten around each page's primary theme |
| Assumed domain `brightflowservices.com` in canonicals and schema | all | Replaced with a documented placeholder plus `tools/set_domain.py` |
| Thin About page (heading only) | `about.html` | Added real content: who we are, approach, services, process |
| Thin placeholder Terms page indexable | `terms.html` | Set to `noindex` until terms are published |

No missing titles, duplicate titles or descriptions, broken internal links, or missing alt attributes were found.

**After: 0 errors, 0 warnings.**

---

## 5. Local SEO

**Google Business Profile (GBP)**
1. Create or claim the profile with the exact business name **Bright Flow Services**.
2. Use one phone number and (if shown publicly) one address, and enter them **identically** on the website config, the JSON-LD, the GBP, and any directory listings (NAP consistency).
3. If the business serves customers at their location without a public storefront, set it up as a *service-area business* and hide the address.
4. Add the service areas you actually serve, the primary category ("Electrician") and relevant secondary categories, and your hours.
5. Add the GBP URL to the JSON-LD `sameAs` array on the homepage.
6. Link the GBP website field to the homepage (or a tracking-parameter version of it).

**Service areas**
- The homepage "Service area" section has an empty, auto-hidden list ready for verified counties/cities. Add each as `<li>Orange County</li>`.
- When cities are confirmed, also list them in JSON-LD, e.g. `"areaServed": [{"@type":"City","name":"Orlando"}, …]`.
- **Avoid doorway pages.** Only create a city page when you can write genuinely local, useful content for it (projects completed there, local utility or permitting notes, neighborhood-specific considerations, real photos). A page that just swaps the city name is likely to be treated as low quality.
- Reviews: once you have genuine reviews, publish them with the hidden reviews section on the homepage. Do not add review or rating markup for reviews you did not collect on your own site.

---

## 6. Content opportunities

Educational topics that answer genuine customer questions and link naturally to service pages. Write these as standalone guides only when they can be thorough and accurate; never publish DIY wiring instructions.

**Residential**
- Signs your home may need an electrical panel upgrade → panel upgrades
- 100-amp vs. 200-amp service: what's the difference for a Florida home? → panel upgrades
- Level 1 vs. Level 2 EV charging at home → EV chargers
- Standby vs. portable generators for Florida hurricane season → generators
- Why you should never backfeed a generator through an outlet (safety explainer) → generators
- Choosing LED bulbs and dimmers that work together → lighting
- Bathroom exhaust fans and humidity in Florida homes → lighting & fans
- What a hot tub needs electrically before delivery day → dedicated circuits
- Smart switches and the neutral-wire question → smart home

**Commercial**
- Planning electrical work for a tenant build-out: what to have ready → new construction wiring
- LED retrofit kits vs. new fixtures for commercial spaces → lighting retrofits
- Electrical planning for a new commercial kitchen → equipment hookups
- How to tell whether your building has electrical capacity for new equipment or EV chargers → service upgrades
- Why breakers keep tripping in commercial buildings and when to call an electrician → troubleshooting

---

## 7. Ongoing checklist

- [ ] Run `tools/set_domain.py` with the real domain.
- [ ] Uncomment the https/www host rule in `.htaccess` once SSL is active.
- [ ] Add phone/email/address/hours to the config and JSON-LD (only verified values).
- [ ] Add verified service areas (homepage list + JSON-LD).
- [ ] Finalize Privacy Policy and Terms, then remove their `noindex` and add them to the sitemap.
- [ ] Submit `sitemap.xml` in Google Search Console and Bing Webmaster Tools.
- [ ] Validate pages with the Rich Results Test.
- [ ] Add real project photos with descriptive alt text where photos convey information.
- [ ] Run `python3 tools/seo_audit.py` before each publish.
