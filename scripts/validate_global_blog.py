#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Market Context 360 - Global Blog Validator & Linter Guard Engine
-----------------------------------------------------------------
Enforces strict 1:1 category routing, frontmatter schema validation,
Liquid template condition integrity, and mathematical disjoint set isolation.

Repository: ideaspot360/markets (Market Context 360)
Directory:  growth_engine/03_blog_hub/stock_blog_global
"""

import sys
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional
import yaml

# Standard Allowed Categories
ALLOWED_CATEGORIES: Set[str] = {
    "Macro Intelligence",
    "US Systematic Equity",
    "Options & Income",
    "Quantitative Frameworks",
    "Platform Manifesto",
}

# The 4 Core Research Pillars and their exact template & category configuration
RESEARCH_PILLARS: Dict[str, Dict[str, str]] = {
    "macro": {
        "title": "Macro Intelligence & Central Bank Liquidity",
        "category": "Macro Intelligence",
        "template": "category/macro/index.html",
        "permalink": "/category/macro/",
        "pillar_badge": "PILLAR 01",
    },
    "equities": {
        "title": "US Systematic Equity & Cash Flow Analytics",
        "category": "US Systematic Equity",
        "template": "category/equities/index.html",
        "permalink": "/category/equities/",
        "pillar_badge": "PILLAR 02",
    },
    "options-income": {
        "title": "Covered Call ETFs & Option Income Strategies",
        "category": "Options & Income",
        "template": "category/options-income/index.html",
        "permalink": "/category/options-income/",
        "pillar_badge": "PILLAR 03",
    },
    "quant": {
        "title": "Quantitative Frameworks & Algorithmic Trading",
        "category": "Quantitative Frameworks",
        "template": "category/quant/index.html",
        "permalink": "/category/quant/",
        "pillar_badge": "PILLAR 04",
    },
}

# Categories strictly forbidden from appearing in any research pillar
EXCLUDED_CATEGORIES_FROM_RESEARCH: Set[str] = {
    "Platform Manifesto",
}

# Frontmatter mandatory fields
REQUIRED_FRONTMATTER_FIELDS: Set[str] = {
    "title",
    "date",
    "category",
    "tags",
    "author",
    "summary",
    "layout",
}


def find_blog_root(start_path: Optional[Path] = None) -> Path:
    """
    Locates the stock_blog_global root directory by checking current directory,
    parent directories, or standard workspace locations.
    """
    if start_path is None:
        start_path = Path.cwd()

    candidates = [
        start_path,
        start_path / "growth_engine" / "03_blog_hub" / "stock_blog_global",
        start_path.parent / "stock_blog_global",
        start_path.parent,
    ]

    for c in candidates:
        if (c / "_config.yml").exists() and (c / "_posts").exists() and (c / "category").exists():
            return c.resolve()

    # Search upward for _config.yml containing "Market Context 360"
    curr = start_path.resolve()
    for _ in range(5):
        cfg = curr / "_config.yml"
        if cfg.exists():
            try:
                content = cfg.read_text(encoding="utf-8")
                if "Market Context 360" in content:
                    return curr
            except Exception:
                pass
        curr = curr.parent

    raise FileNotFoundError(
        f"Could not locate stock_blog_global root directory starting from {start_path}"
    )


def extract_frontmatter(content: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Extracts and parses YAML frontmatter from markdown file text.
    Returns (data, error_message).
    """
    pattern = r"^---\r?\n(.*?)\r?\n---\r?\n"
    match = re.match(pattern, content, re.DOTALL)
    if not match:
        return None, "Missing or malformed frontmatter (must start with '---' and end with '---')"

    raw_yaml = match.group(1)
    try:
        data = yaml.safe_load(raw_yaml)
        if not isinstance(data, dict):
            return None, "Frontmatter YAML is not a key-value mapping"
        return data, None
    except yaml.YAMLError as exc:
        return None, f"YAML parsing error: {exc}"


def validate_category_templates(blog_root: Path) -> List[str]:
    """
    Validates that the 4 category index templates:
    1. Exist on disk.
    2. Have correct permalink frontmatter.
    3. Use strictly 'post.category == <EXPECTED>' with NO loose tags OR conditions.
    4. Prohibit any 'post.tags' or 'tags contains' in filtering logic.
    """
    errors: List[str] = []

    for pillar_key, pillar_info in RESEARCH_PILLARS.items():
        template_rel = pillar_info["template"]
        template_file = blog_root / template_rel
        expected_category = pillar_info["category"]
        expected_permalink = pillar_info["permalink"]

        if not template_file.exists():
            errors.append(f"[Template Missing] {template_rel} does not exist.")
            continue

        try:
            content = template_file.read_text(encoding="utf-8")
        except Exception as e:
            errors.append(f"[Template Read Error] Failed to read {template_rel}: {e}")
            continue

        # 1. Frontmatter check
        fm_data, fm_err = extract_frontmatter(content)
        if fm_err:
            errors.append(f"[Template Frontmatter] {template_rel}: {fm_err}")
        else:
            if fm_data.get("permalink") != expected_permalink:
                errors.append(
                    f"[Template Permalink] {template_rel} permalink '{fm_data.get('permalink')}' "
                    f"does not match expected '{expected_permalink}'"
                )

        # 2. Strict Liquid loop condition check
        # Look for {% for post in site.posts %} followed by {% if ... %}
        for_loop_match = re.search(
            r"\{%\s*for\s+post\s+in\s+site\.posts\s*%\}\s*(.*?)\s*\{%\s*endfor\s*%\}",
            content,
            re.DOTALL,
        )
        if not for_loop_match:
            errors.append(f"[Template Liquid Loop] {template_rel} is missing '{{% for post in site.posts %}}' loop.")
            continue

        loop_body = for_loop_match.group(1)

        # Find the first {% if ... %} inside the post loop
        if_match = re.search(r"\{%\s*if\s+(.*?)\s*%\}", loop_body)
        if not if_match:
            errors.append(f"[Template Liquid Filter] {template_rel} does not contain '{{% if ... %}}' condition.")
            continue

        condition = if_match.group(1).strip()

        # Strict checks against loose tag-based conditions
        if "post.tags" in condition or "tags contains" in condition:
            errors.append(
                f"[Template Tag Pollution] {template_rel} contains loose tag matching: '{condition}'. "
                f"Tag-based filtering in category templates is strictly prohibited."
            )

        if " or " in condition:
            errors.append(
                f"[Template Loose OR] {template_rel} contains multi-clause OR condition: '{condition}'. "
                f"Only strict single category equality is permitted."
            )

        # Expected strict pattern: post.category == 'Macro Intelligence'
        strict_pattern = r"^post\.category\s*==\s*['\"]" + re.escape(expected_category) + r"['\"]$"
        if not re.match(strict_pattern, condition):
            errors.append(
                f"[Template Category Mismatch] {template_rel} filter condition '{condition}' "
                f"does not match strict expected condition 'post.category == \\'{expected_category}\\'"
            )

    return errors


def validate_post_frontmatter(file_path: Path, blog_root: Path) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """
    Validates a single markdown post file:
    - Filename syntax YYYY-MM-DD-*.md
    - Frontmatter existence and schema
    - Category validity against ALLOWED_CATEGORIES
    - Non-empty tags list
    - Referenced image assets existence on disk
    """
    errors: List[str] = []
    rel_path = file_path.relative_to(blog_root)

    # 1. Filename syntax
    if not re.match(r"^\d{4}-\d{2}-\d{2}-.+\.md$", file_path.name):
        errors.append(f"[Post Filename] {rel_path} does not follow standard 'YYYY-MM-DD-title.md' format.")

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        errors.append(f"[Post Read Error] Failed to read {rel_path}: {e}")
        return None, errors

    # 2. Frontmatter extraction
    fm_data, fm_err = extract_frontmatter(content)
    if fm_err:
        errors.append(f"[Post Frontmatter] {rel_path}: {fm_err}")
        return None, errors

    # 3. Required fields check
    for req in REQUIRED_FRONTMATTER_FIELDS:
        val = fm_data.get(req)
        if val is None or (isinstance(val, str) and not val.strip()):
            errors.append(f"[Post Missing Field] {rel_path} is missing required field: '{req}'.")

    # 4. Strict category verification
    category = fm_data.get("category")
    if not isinstance(category, str) or not category.strip():
        errors.append(f"[Post Invalid Category] {rel_path} category must be a non-empty string.")
    elif category not in ALLOWED_CATEGORIES:
        allowed_list = sorted(list(ALLOWED_CATEGORIES))
        errors.append(
            f"[Post Unauthorized Category] {rel_path} category '{category}' is NOT in allowed categories: {allowed_list}."
        )

    # 5. Tags verification
    tags = fm_data.get("tags")
    if not isinstance(tags, list) or len(tags) == 0:
        errors.append(f"[Post Invalid Tags] {rel_path} 'tags' must be a non-empty list of tags.")
    else:
        for t in tags:
            if not isinstance(t, str) or not t.strip():
                errors.append(f"[Post Empty Tag] {rel_path} contains empty or non-string tag: {t!r}")

    # 6. Asset references verification (images in markdown or HTML)
    # Match markdown images: ![alt](/assets/...)
    img_matches = re.findall(r"!\[.*?\]\((/assets/[^)]+)\)", content)
    # Match HTML images: <img ... src="/assets/..."
    img_matches += re.findall(r'<img[^>]+src=["\'](/assets/[^"\']+)["\']', content)

    for img_ref in img_matches:
        # Strip anchors / query params
        clean_ref = img_ref.split("?")[0].split("#")[0].lstrip("/")
        asset_file = blog_root / clean_ref
        if not asset_file.exists():
            errors.append(f"[Missing Asset] {rel_path} references non-existent asset: '{img_ref}' -> {clean_ref}")

    return fm_data, errors


def validate_mathematical_isolation(
    posts_data: Dict[str, Dict[str, Any]],
    blog_root: Path
) -> List[str]:
    """
    Performs rigorous mathematical set-theory isolation checks:
    1. Disjointness: S_i ∩ S_j = ∅ for all research categories i ≠ j.
    2. Manifesto Isolation: S_manifesto ∩ S_i = ∅ for all research pillars i.
    3. Completeness: Every research post is assigned to exactly one category.
    """
    errors: List[str] = []

    # Map each research pillar to its matched post file set
    matched_sets: Dict[str, Set[str]] = {}
    for pillar_key, pillar_info in RESEARCH_PILLARS.items():
        cat_name = pillar_info["category"]
        matched_sets[pillar_key] = {
            post_file for post_file, meta in posts_data.items()
            if meta.get("category") == cat_name
        }

    # Set of manifesto / announcement posts
    manifesto_posts: Set[str] = {
        post_file for post_file, meta in posts_data.items()
        if meta.get("category") in EXCLUDED_CATEGORIES_FROM_RESEARCH
    }

    # 1. Disjoint Set Check (No post may belong to more than 1 pillar)
    pillar_keys = list(RESEARCH_PILLARS.keys())
    for i in range(len(pillar_keys)):
        for j in range(i + 1, len(pillar_keys)):
            k1, k2 = pillar_keys[i], pillar_keys[j]
            overlap = matched_sets[k1] & matched_sets[k2]
            if overlap:
                c1 = RESEARCH_PILLARS[k1]["category"]
                c2 = RESEARCH_PILLARS[k2]["category"]
                errors.append(
                    f"[Disjoint Set Violation] Posts {sorted(list(overlap))} matched BOTH "
                    f"'{c1}' and '{c2}'. Posts must be 1:1 strictly mutually exclusive!"
                )

    # 2. Manifesto / Announcement Isolation Check
    for pillar_key, post_set in matched_sets.items():
        pillar_cat = RESEARCH_PILLARS[pillar_key]["category"]
        leaked = post_set & manifesto_posts
        if leaked:
            errors.append(
                f"[Manifesto Leak Violation] Excluded manifesto posts {sorted(list(leaked))} "
                f"leaked into research pillar '{pillar_cat}'!"
            )

    # 3. Exhaustive Assignment Check
    # Verify that every post in posts_data belongs to either one research pillar OR manifesto
    all_pillar_posts = set().union(*matched_sets.values()) if matched_sets else set()
    for post_file, meta in posts_data.items():
        cat = meta.get("category")
        if cat in EXCLUDED_CATEGORIES_FROM_RESEARCH:
            continue
        if post_file not in all_pillar_posts:
            errors.append(
                f"[Unrouted Research Post] Post '{post_file}' with category '{cat}' "
                f"is not mapped to any defined research pillar!"
            )

    return errors


def run_full_validation(blog_root: Optional[Path] = None) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Executes full multi-stage validation:
    Stage 1: Category Liquid Template Integrity (Linter)
    Stage 2: Post Frontmatter Schema & Asset Existence
    Stage 3: Mathematical Disjoint Set & Manifesto Isolation
    """
    if blog_root is None:
        blog_root = find_blog_root()

    all_errors: List[str] = []
    stats: Dict[str, Any] = {
        "blog_root": str(blog_root),
        "templates_checked": len(RESEARCH_PILLARS),
        "posts_checked": 0,
        "categories_found": {},
        "stage1_errors": 0,
        "stage2_errors": 0,
        "stage3_errors": 0,
    }

    # Stage 1: Category Template Linter
    template_errors = validate_category_templates(blog_root)
    stats["stage1_errors"] = len(template_errors)
    all_errors.extend(template_errors)

    # Stage 2: Post Schema & Asset Verification
    posts_dir = blog_root / "_posts"
    post_files = sorted(list(posts_dir.glob("*.md")))
    stats["posts_checked"] = len(post_files)

    posts_data: Dict[str, Dict[str, Any]] = {}
    stage2_err_count = 0

    for pf in post_files:
        meta, p_errs = validate_post_frontmatter(pf, blog_root)
        if p_errs:
            stage2_err_count += len(p_errs)
            all_errors.extend(p_errs)
        if meta:
            posts_data[pf.name] = meta
            cat = meta.get("category", "UNKNOWN")
            stats["categories_found"][cat] = stats["categories_found"].get(cat, 0) + 1

    stats["stage2_errors"] = stage2_err_count

    # Stage 3: Mathematical Set Isolation Check
    isolation_errors = validate_mathematical_isolation(posts_data, blog_root)
    stats["stage3_errors"] = len(isolation_errors)
    all_errors.extend(isolation_errors)

    is_valid = len(all_errors) == 0
    return is_valid, all_errors, stats


def print_report(is_valid: bool, errors: List[str], stats: Dict[str, Any]) -> None:
    """Prints a beautiful and detailed terminal report."""
    print("=" * 78)
    print(" 🛡️  MARKET CONTEXT 360 — GLOBAL BLOG LINTER & INTEGRITY GUARD ENGINE")
    print("=" * 78)
    print(f" Root Directory      : {stats['blog_root']}")
    print(f" Templates Checked   : {stats['templates_checked']} Core Category Indices")
    print(f" Posts Analyzed      : {stats['posts_checked']} Publications")
    print(" Category Breakdown  :")
    for cat, count in stats.get("categories_found", {}).items():
        print(f"   • {cat:<26}: {count} post(s)")
    print("-" * 78)
    s1_res = "✅ PASS" if stats['stage1_errors'] == 0 else f"❌ FAIL ({stats['stage1_errors']} errors)"
    s2_res = "✅ PASS" if stats['stage2_errors'] == 0 else f"❌ FAIL ({stats['stage2_errors']} errors)"
    s3_res = "✅ PASS" if stats['stage3_errors'] == 0 else f"❌ FAIL ({stats['stage3_errors']} errors)"

    print(" Guard Stage Results :")
    print(f"   [Stage 1] Category Template Liquid Linter : {s1_res}")
    print(f"   [Stage 2] Frontmatter Schema & Asset Guard: {s2_res}")
    print(f"   [Stage 3] Mathematical Disjoint Isolation : {s3_res}")
    print("-" * 78)

    if is_valid:
        print(" 🎉 OVERALL STATUS: ALL CHECKS PASSED (100% Mathematically Isolated & Valid)")
        print("=" * 78)
    else:
        print(f" ❌ OVERALL STATUS: FAILED ({len(errors)} total violation(s) detected)")
        print("=" * 78)
        print("\nDETAILED VIOLATIONS LIST:")
        for idx, err in enumerate(errors, 1):
            print(f"  {idx}. {err}")
        print("\n" + "=" * 78)


def main() -> int:
    try:
        blog_root = find_blog_root()
    except Exception as e:
        print(f"[FATAL] {e}", file=sys.stderr)
        return 1

    is_valid, errors, stats = run_full_validation(blog_root)
    print_report(is_valid, errors, stats)

    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
