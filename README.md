# Bright Flow Services — Website

Static marketing website for Bright Flow Services, a residential and commercial electrical contractor in Florida.

Plain HTML5, CSS3 and vanilla JavaScript. There is no build step: upload the folder contents to any static host (e.g. Hostinger `public_html`) and `index.html` serves as the homepage. Double-clicking `index.html` locally also works.

## Structure

```
index.html                 Homepage
services.html              Services overview
services/*.html            One page per major service (panel upgrades, EV chargers, generators, lighting, repairs, inspections)
residential.html           Residential electrical
commercial.html            Commercial electrical
about.html                 About
contact.html               Contact / booking (#booking anchor)
privacy.html               Privacy policy (placeholder)
404.html                   Not-found page (root-absolute paths, used by .htaccess)
assets/css/main.css        Global design system and shared components
assets/js/main.js          Header, dropdown, mobile menu, reveal animations
assets/images/             Logo and favicon (SVG)
sitemap.xml, robots.txt    SEO
.htaccess                  Apache/LiteSpeed config: 404, compression, caching, security headers
```

## Shared components

The header, mobile menu, footer and mobile call bar are the same markup on every page; change them on all pages together. Pages in `services/` use `../` relative paths.

Main CSS patterns: `.btn` (`--primary`, `--ghost`, `--light`, `--white`), `.section`, `.section-head`, `.grid--2/3/4`, `.card` / `.service-card`, `.cta-band`, `.page-hero`, `.form` / `.field`, `.reveal` (scroll animation).

When CSS or JS changes, bump the `?v=` query string on the `main.css` / `main.js` links so browsers pick up the new file (they are cached for a month).

## Placeholders to replace before launch

- Phone `(407) 555-0142` / `tel:+14075550142`
- Email `service@brightflowservices.com`
- Florida license `EC13000000`
- Domain `https://www.brightflowservices.com` (canonical URLs, JSON-LD, sitemap, robots.txt)
- Social profile links (`href="#"` in the footer)
- Business hours, and the "24/7 emergency" and "5-Star Rated" claims
