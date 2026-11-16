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

## 📚 Core Research Categories

1. **`Macro Intelligence`**: Fed Net Liquidity, Treasury General Account (TGA), Reverse Repo Facility (RRP), interest rate expectations, and global central bank balance sheets.
2. **`US Equity Deep-Dive`**: Megacap hyperscalers, structural Free Cash Flow (FCF) yields, AI infrastructure CapEx returns, and multiple compression analysis.
3. **`Earnings Post-Mortem`**: Quarterly earnings decompilation, consensus divergence, guidance quality, and margin trajectory.
4. **`Systematic & Factor Frameworks`**: Equity Risk Premium (ERP), cross-asset volatility (VIX, MOVE), and quantitative factor rotation models.

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

### Step 2: Commit & Push
```bash
git add .
git commit -m "feat(markets): publish new report title"
git push origin main
```
The publication goes live globally at `https://markets.ideaspot360.com` immediately upon push.
