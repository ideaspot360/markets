# 📈 Market Context 360 (`markets.ideaspot360.com`)

> **Platform Identity**: Institutional-grade macroeconomic analysis, global central bank liquidity regimes, US equity sector deep-dives, earnings post-mortems, and quantitative factor investment frameworks.  
> **Official Domain**: `https://markets.ideaspot360.com`  
> **Hosting & Infrastructure**: GitHub Pages (`ideaspot360/markets` repository) via Porkbun CNAME DNS Routing (Enforce HTTPS)  
> **Telemetry & Analytics**: Google Analytics 4 (`G-SNWRVFJ06Y`), Google Search Console verified (`sitemap.xml`)

---

## 🏛️ Operational Principles & Architecture

1. **Independent Publication Workflow**:
   - Editorial planning, macroeconomic data modeling, empirical charts, and analytical markdown authoring are maintained independently within this dedicated repository.
2. **Single-Command Publishing Pipeline**:
   - Create or update articles in `_posts/YYYY-MM-DD-slug.md` and push to `origin/main`. GitHub Pages automatically compiles and deploys globally within seconds.
3. **Institutional Compliance & Disclaimer**:
   - Every publication and global footer includes standardized financial research disclaimers ensuring institutional transparency and regulatory clarity.

---

## 🔍 Ultra-Precision Pan & Zoom Lightbox Engine

All macro time-series diagrams, Fed dot plots, and financial statement matrices automatically benefit from our built-in **Ultra-Precision Pan-Zoom Engine**:
- **Continuous Zoom**: Smooth cursor-anchored scaling from 0.5x to 6.0x via mouse wheel.
- **360° Free Pan**: Effortless drag-and-pan navigation across dense charts.
- **Smart Toggle**: Double-click toggles 2.5x instant magnification.
- **Mobile Touch**: Native pinch-to-zoom and single-finger panning support.

---

## 📚 Core Research Categories (The 4 Canonical Pillars)

Every publication must map **1:1 exclusively** to exactly one of the 4 research pillars (or Platform Manifesto):

1. **`Options & Systematic Income`** (`/category/options-income/`): Systematic covered call mechanics, variance risk premia harvesting, volatility skew exploitation, and structured derivative income strategies (JEPI, JEPQ, SPYI, 0DTE).
2. **`Macro Intelligence`** (`/category/macro/`): Fed Net Liquidity, Treasury General Account (TGA), Reverse Repo Facility (RRP), sovereign yield curves, and macroeconomic regime shifts.
3. **`Market Structure & Technicals`** (`/category/technicals/`): Options dealer gamma exposure (GEX), volatility surface positioning, auction theory, liquidity voids, and institutional technical setups.
4. **`Equities & Factor Research`** (`/category/equities/`): Cross-sectional momentum, quantitative factor models, balance sheet forensics, and single-stock fundamental valuations.

*(Note: `Platform Manifesto` is reserved exclusively for platform announcements and is strictly isolated from research pillars.)*

---

## 🛡️ Storefront Isolation & Quality Enforcement

In accordance with our **Factory-to-Storefront Architecture (PART 0-C)**, this repository serves exclusively as a **pure public storefront**. All research engines, diagram visualizers, and audit scripts are isolated in the central factory (`everhashk-justin/stock_alram`).

### Integrity Verification (Central Factory)
Before committing or publishing to this repository, publications are strictly verified using the central factory tools:
```bash
# Central Ironclad Gatekeeper
blog-gatekeeper --dir growth_engine/03_blog_hub/stock_blog_global/_posts/ --platform markets

# Or factory validator
python tools/blog_tools/stock_blog_global/scripts/validate_global_blog.py
pytest tools/blog_tools/stock_blog_global/scripts/test_validate_global_blog.py -v
```

---

## 🚀 Publishing SOP

### Step 1: Create Markdown Post
Draft new research inside `_posts/YYYY-MM-DD-title-slug.md`:

```markdown
---
title: "Institutional Research Title"
date: 2026-11-17 09:30:00 +0900
category: "Macro Intelligence"
tags: [GlobalLiquidity, Fed, S&P500]
author: "Market Context Research"
summary: "1-2 sentence core institutional thesis."
layout: post
---

# Publication Body...
```

### Step 2: Validate via Factory Gate & Commit
```bash
# Verify integrity via central factory gatekeeper (0 violations required)
blog-gatekeeper --dir growth_engine/03_blog_hub/stock_blog_global/_posts/ --platform markets

# Commit and Push from storefront
git add .
git commit -m "feat(markets): publish new report title"
git push origin main
```
The publication goes live globally at `https://markets.ideaspot360.com` via GitHub Pages immediately upon push.
