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

1. **`Macro Intelligence`** (`/category/macro/`): Fed Net Liquidity, Treasury General Account (TGA), Reverse Repo Facility (RRP), sovereign yield curves, and global central bank balance sheets.
2. **`US Systematic Equity`** (`/category/equities/`): Megacap hyperscalers, structural Free Cash Flow (FCF) yields, AI infrastructure CapEx returns, and valuation multiple compression analysis.
3. **`Options & Income`** (`/category/options-income/`): Covered call ETFs (JEPI, JEPQ, 0DTE), volatility term structures, option writing yield mechanics, and downside asymmetric risk models.
4. **`Quantitative Frameworks`** (`/category/quant/`): Quantitative asset allocation, factor rotation, PineScript execution algorithms, and systematic risk management.

*(Note: `Platform Manifesto` is reserved exclusively for platform announcements and is strictly isolated from research pillars.)*

---

## 🛡️ Automated Integrity Guard & Pre-Commit Enforcement

To prevent category collisions, tag pollution, missing assets, or frontmatter schema errors, an automated 3-stage validation guard is strictly enforced:

### Install Local Git Pre-Commit Hook
```bash
python scripts/install_git_hook.py
# or
python scripts/validate_global_blog.py --install-hook
```
Once installed, `git commit` automatically runs the validator and aborts if any violation is detected.

### Manual Verification
```bash
python scripts/validate_global_blog.py
pytest scripts/test_validate_global_blog.py -v
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

### Step 2: Validate & Commit
```bash
# Verify integrity (0 violations required)
python scripts/validate_global_blog.py

# Commit and Push
git add .
git commit -m "feat(markets): publish new report title"
git push origin main
```
The publication is re-validated via GitHub Actions CI and goes live globally at `https://markets.ideaspot360.com` immediately upon push.
