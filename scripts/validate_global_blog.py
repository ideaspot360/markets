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
    Handles UTF-8 BOM if present.
    Returns (data, error_message).
    """
    cleaned_content = content.lstrip("\ufeff")
    pattern = r"^---\r?\n(.*?)\r?\n---\r?\n"
    match = re.match(pattern, cleaned_content, re.DOTALL)
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


def validate_category_templates(blog_root: Path) -> Tuple[List[str], Dict[str, str]]:
    """
    Validates that:
    1. Only authorized category directories exist under category/.
    2. The 4 category index templates exist on disk.
    3. Have correct permalink frontmatter.
    4. Prohibit any 'post.tags' or 'tags contains' in the template.
    5. Prohibit any 'elsif' branches.
    6. Use strictly 'post.category == <EXPECTED>' with NO loose OR conditions.

    Returns:
      (errors, template_conditions_map)
      where template_conditions_map maps pillar_key to the exact extracted Liquid condition string.
    """
    errors: List[str] = []
    template_conditions: Dict[str, str] = {}

    # 1. Directory Structure Scan: ensure no rogue category directories exist
    category_base = blog_root / "category"
    if category_base.exists() and category_base.is_dir():
        for item in category_base.iterdir():
            if item.is_dir() and item.name not in RESEARCH_PILLARS:
                errors.append(
                    f"[Unauthorized Category Directory] Unregistered category directory detected: 'category/{item.name}'. "
                    f"Only the 4 registered pillars {list(RESEARCH_PILLARS.keys())} are permitted."
                )

    # 2. Template Integrity Checks for registered pillars
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

        # Frontmatter check
        fm_data, fm_err = extract_frontmatter(content)
        if fm_err:
            errors.append(f"[Template Frontmatter] {template_rel}: {fm_err}")
        else:
            if fm_data.get("permalink") != expected_permalink:
                errors.append(
                    f"[Template Permalink] {template_rel} permalink '{fm_data.get('permalink')}' "
                    f"does not match expected '{expected_permalink}'"
                )

        # Global Tag-pollution check across entire template
        # Any condition in the file containing tags contains or post.tags is illegal
        liquid_tags = re.findall(r"\{%\s*(.*?)\s*%\}", content)
        for l_tag in liquid_tags:
            l_clean = l_tag.strip()
            if l_clean.startswith("elsif"):
                errors.append(
                    f"[Template Forbidden Elsif] {template_rel} contains multi-branch 'elsif': '{{% {l_clean} %}}'. "
                    f"Category templates must use strict single category routing without fallback branches."
                )
            if "post.tags" in l_clean or "tags contains" in l_clean or "post.tag" in l_clean:
                errors.append(
                    f"[Template Tag Pollution] {template_rel} contains forbidden tag-based logic: '{{% {l_clean} %}}'. "
                    f"Tag-based filtering in category templates is strictly prohibited."
                )

        # Post loop validation
        for_loop_matches = re.findall(
            r"\{%\s*for\s+post\s+in\s+site\.posts\s*%\}(.*?)\{%\s*endfor\s*%\}",
            content,
            re.DOTALL,
        )
        if not for_loop_matches:
            errors.append(f"[Template Liquid Loop] {template_rel} is missing '{{% for post in site.posts %}}' loop.")
            continue

        # Check all loops in the template
        for loop_idx, loop_body in enumerate(for_loop_matches):
            if_matches = re.findall(r"\{%\s*if\s+(.*?)\s*%\}", loop_body)
            if not if_matches:
                errors.append(f"[Template Liquid Filter] {template_rel} loop #{loop_idx+1} does not contain '{{% if ... %}}' condition.")
                continue

            primary_condition = if_matches[0].strip()
            template_conditions[pillar_key] = primary_condition

            if " or " in primary_condition:
                errors.append(
                    f"[Template Loose OR] {template_rel} contains multi-clause OR condition: '{primary_condition}'. "
                    f"Only strict single category equality is permitted."
                )

            # Strict pattern: post.category == 'Macro Intelligence' or "Macro Intelligence"
            strict_pattern = r"^post\.category\s*==\s*['\"]" + re.escape(expected_category) + r"['\"]$"
            if not re.match(strict_pattern, primary_condition):
                errors.append(
                    f"[Template Category Mismatch] {template_rel} filter condition '{primary_condition}' "
                    f"does not match strict expected condition 'post.category == \\'{expected_category}\\'"
                )

    return errors, template_conditions


def validate_post_frontmatter(file_path: Path, blog_root: Path) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """
    Validates a single markdown post file:
    - Filename syntax YYYY-MM-DD-*.md
    - Frontmatter existence and schema
    - Mandatory singular 'category' in ALLOWED_CATEGORIES
    - Guard against ambiguous plural 'categories'
    - Non-empty tags list of non-empty strings
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

    # 5. Guard against ambiguous plural 'categories' field in Jekyll
    if "categories" in fm_data:
        cats_val = fm_data.get("categories")
        if isinstance(cats_val, list):
            if len(cats_val) != 1 or cats_val[0] != category:
                errors.append(
                    f"[Post Ambiguous Categories] {rel_path} defines plural 'categories: {cats_val}' "
                    f"which does not strictly match canonical singular 'category: {category}'. "
                    f"To preserve 1:1 category routing, remove 'categories' or specify only [{category!r}]."
                )
        elif isinstance(cats_val, str):
            if cats_val.strip() != category:
                errors.append(
                    f"[Post Ambiguous Categories] {rel_path} defines plural 'categories: {cats_val}' "
                    f"differing from 'category: {category}'."
                )
        else:
            errors.append(f"[Post Ambiguous Categories] {rel_path} defines invalid 'categories' format.")

    # 6. Tags verification
    tags = fm_data.get("tags")
    if not isinstance(tags, list) or len(tags) == 0:
        errors.append(f"[Post Invalid Tags] {rel_path} 'tags' must be a non-empty list of tags.")
    else:
        for t in tags:
            if not isinstance(t, str) or not t.strip():
                errors.append(f"[Post Empty Tag] {rel_path} contains empty or non-string tag: {t!r}")

    # 7. Asset references verification (images in markdown or HTML)
    img_matches = re.findall(r"!\[.*?\]\((/assets/[^)]+)\)", content)
    img_matches += re.findall(r'<img[^>]+src=["\'](/assets/[^"\']+)["\']', content)

    for img_ref in img_matches:
        clean_ref = img_ref.split("?")[0].split("#")[0].lstrip("/")
        asset_file = blog_root / clean_ref
        if not asset_file.exists():
            errors.append(f"[Missing Asset] {rel_path} references non-existent asset: '{img_ref}' -> {clean_ref}")

    return fm_data, errors


def evaluate_liquid_condition(condition: str, post_meta: Dict[str, Any]) -> bool:
    """
    Evaluates a Liquid condition string against a post's metadata dictionary.
    Supports atomic expressions and boolean combinators:
      - post.category == 'Value' / "Value"
      - post.category != 'Value' / "Value"
      - post.tags contains 'Value' / "Value"
      - Logical 'or' (split by ' or ')
      - Logical 'and' (split by ' and ')
    """
    condition = condition.strip()

    if " or " in condition:
        clauses = [c.strip() for c in condition.split(" or ")]
        return any(evaluate_liquid_condition(c, post_meta) for c in clauses if c)

    if " and " in condition:
        clauses = [c.strip() for c in condition.split(" and ")]
        return all(evaluate_liquid_condition(c, post_meta) for c in clauses if c)

    # Atomic condition: post.category == 'Value'
    m_eq = re.match(r"^post\.category\s*(==|!=)\s*['\"](.*?)['\"]$", condition)
    if m_eq:
        op = m_eq.group(1)
        target = m_eq.group(2)
        actual = str(post_meta.get("category", ""))
        return (actual == target) if op == "==" else (actual != target)

    # Atomic condition: post.tags contains 'Value'
    m_tags = re.match(r"^post\.tags\s+contains\s+['\"](.*?)['\"]$", condition)
    if m_tags:
        target_tag = m_tags.group(1)
        actual_tags = post_meta.get("tags", [])
        if isinstance(actual_tags, str):
            actual_tags = [actual_tags]
        elif not isinstance(actual_tags, list):
            actual_tags = []
        return target_tag in actual_tags

    # Fallback equality check
    return False


def validate_mathematical_isolation(
    posts_data: Dict[str, Dict[str, Any]],
    template_conditions: Optional[Dict[str, str]] = None,
    blog_root: Optional[Path] = None,
) -> List[str]:
    """
    Performs rigorous mathematical set-theory isolation checks:
    1. Template Simulation: Evaluates each template's Liquid filter against all posts to determine
       the actual set of posts matched by each category template.
    2. Disjointness: S_i ∩ S_j = ∅ for all research categories i ≠ j.
    3. Manifesto Isolation: S_manifesto ∩ S_i = ∅ for all research pillars i.
    4. Completeness & Singularity: Every research post is routed to EXACTLY ONE research pillar.
    5. Template-Category Congruence: Matched post set equals declared category post set.
    """
    errors: List[str] = []
    matched_sets: Dict[str, Set[str]] = {}
    declared_sets: Dict[str, Set[str]] = {}

    for pillar_key, pillar_info in RESEARCH_PILLARS.items():
        cat_name = pillar_info["category"]
        declared_sets[pillar_key] = {
            post_file for post_file, meta in posts_data.items()
            if meta.get("category") == cat_name
        }

        # If template conditions are available, simulate runtime matching
        if template_conditions and pillar_key in template_conditions:
            cond = template_conditions[pillar_key]
            matched_sets[pillar_key] = {
                post_file for post_file, meta in posts_data.items()
                if evaluate_liquid_condition(cond, meta)
            }
        else:
            # Direct mapping fallback
            matched_sets[pillar_key] = set(declared_sets[pillar_key])

    # Set of manifesto / announcement posts
    manifesto_posts: Set[str] = {
        post_file for post_file, meta in posts_data.items()
        if meta.get("category") in EXCLUDED_CATEGORIES_FROM_RESEARCH
    }

    # 1. Disjoint Set Check: No post may be matched by more than 1 pillar template
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

    # 3. Exhaustive and Singular Routing Check
    for post_file, meta in posts_data.items():
        cat = meta.get("category")
        if cat in EXCLUDED_CATEGORIES_FROM_RESEARCH:
            continue

        matched_pillars = [
            RESEARCH_PILLARS[k]["category"]
            for k in pillar_keys
            if post_file in matched_sets[k]
        ]

        if len(matched_pillars) == 0:
            errors.append(
                f"[Unrouted Research Post] Post '{post_file}' with category '{cat}' "
                f"is not mapped to any defined research pillar!"
            )
        elif len(matched_pillars) > 1:
            errors.append(
                f"[Multiple Category Routing Violation] Post '{post_file}' matched multiple "
                f"research pillars: {matched_pillars}! Posts must map to exactly 1 category."
            )

    # 4. Template-Category Congruence Check (when template_conditions provided)
    if template_conditions:
        for pillar_key in pillar_keys:
            cat_name = RESEARCH_PILLARS[pillar_key]["category"]
            extra = matched_sets[pillar_key] - declared_sets[pillar_key]
            missing = declared_sets[pillar_key] - matched_sets[pillar_key]
            if extra:
                errors.append(
                    f"[Template Incongruence] Category '{cat_name}' template matched extra posts "
                    f"not declared in '{cat_name}': {sorted(list(extra))}"
                )
            if missing:
                errors.append(
                    f"[Template Incongruence] Category '{cat_name}' template failed to match "
                    f"posts declared in '{cat_name}': {sorted(list(missing))}"
                )

    return errors


def install_git_hook(blog_root: Path) -> Tuple[bool, str]:
    """
    Installs a git pre-commit hook in the repository to guarantee
    automated validation before every local commit.
    """
    git_dir = blog_root / ".git"
    if not git_dir.exists():
        return False, f"Directory '{blog_root}' is not a git repository."

    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_file = hooks_dir / "pre-commit"

    hook_content = """#!/bin/sh
# Market Context 360 - Global Blog Pre-Commit Integrity Guard
# Automatically validates blog templates, frontmatter schemas, and category disjointness.

echo "🛡️  [Pre-Commit Hook] Running Market Context 360 Blog Integrity Guard..."

PYTHON_BIN=""
if python -c "import sys" >/dev/null 2>&1; then
    PYTHON_BIN="python"
elif python3 -c "import sys" >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif py -c "import sys" >/dev/null 2>&1; then
    PYTHON_BIN="py"
else
    echo "❌ Python is required to run integrity validation but was not found." >&2
    exit 1
fi

$PYTHON_BIN scripts/validate_global_blog.py
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "❌ [Pre-Commit Hook] Commit aborted: blog integrity validation failed!" >&2
    echo "   Please fix the errors above or run 'python scripts/validate_global_blog.py' to inspect." >&2
    exit 1
fi

echo "✅ [Pre-Commit Hook] Blog integrity verified (0 violations). Proceeding with commit."
exit 0
"""
    try:
        hook_file.write_text(hook_content, encoding="utf-8")
        # Attempt to make hook executable
        try:
            import stat
            hook_file.chmod(hook_file.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        except Exception:
            pass
        return True, f"Pre-commit hook successfully installed at: {hook_file}"
    except Exception as e:
        return False, f"Failed to install pre-commit hook: {e}"


def run_full_validation(blog_root: Optional[Path] = None) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Executes full multi-stage validation:
    Stage 1: Category Liquid Template Integrity (Linter) & Directory Architecture
    Stage 2: Post Frontmatter Schema, Plural Categories Check & Asset Guard
    Stage 3: Mathematical Disjoint Set, Manifesto Isolation & Template Simulation
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
        "git_hook_installed": (blog_root / ".git" / "hooks" / "pre-commit").exists(),
    }

    # Stage 1: Category Template Linter & Directory Scan
    template_errors, template_conditions = validate_category_templates(blog_root)
    stats["stage1_errors"] = len(template_errors)
    all_errors.extend(template_errors)

    # Stage 2: Post Schema & Asset Verification
    posts_dir = blog_root / "_posts"
    post_files = sorted(list(posts_dir.glob("*.md"))) if posts_dir.exists() else []
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

    # Stage 3: Mathematical Set Isolation & Simulation Check
    isolation_errors = validate_mathematical_isolation(posts_data, template_conditions, blog_root)
    stats["stage3_errors"] = len(isolation_errors)
    all_errors.extend(isolation_errors)

    # Stage 4: Ironclad Gatekeeper Hard Block Quality Guard
    stage4_errors: List[str] = []
    try:
        ws_root = blog_root.parents[2]
        if str(ws_root) not in sys.path:
            sys.path.insert(0, str(ws_root))
        from ironclad_gatekeeper import IroncladGatekeeper

        gate = IroncladGatekeeper()
        for post_file in posts_data.keys():
            full_path = str(posts_dir / post_file)
            report = gate.verify(full_path, platform_override="markets")
            if not report.is_passed:
                for v in report.violations:
                    if v.severity == "REJECT":
                        stage4_errors.append(f"[Ironclad Gatekeeper] {post_file} Line {v.line_number}: {v.message}")
    except Exception as e:
        stage4_errors.append(f"[Ironclad Gatekeeper Integration] Failed to execute gatekeeper: {e}")

    stats["stage4_errors"] = len(stage4_errors)
    all_errors.extend(stage4_errors)

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
    print(f" Git Pre-Commit Hook : {'✅ Installed & Active' if stats['git_hook_installed'] else '⚠️  Not Installed (run --install-hook)'}")
    print(" Category Breakdown  :")
    for cat, count in stats.get("categories_found", {}).items():
        print(f"   • {cat:<26}: {count} post(s)")
    print("-" * 78)
    s1_res = "✅ PASS" if stats['stage1_errors'] == 0 else f"❌ FAIL ({stats['stage1_errors']} errors)"
    s2_res = "✅ PASS" if stats['stage2_errors'] == 0 else f"❌ FAIL ({stats['stage2_errors']} errors)"
    s3_res = "✅ PASS" if stats['stage3_errors'] == 0 else f"❌ FAIL ({stats['stage3_errors']} errors)"
    s4_res = "✅ PASS" if stats.get('stage4_errors', 0) == 0 else f"❌ FAIL ({stats.get('stage4_errors', 0)} errors)"

    print(" Guard Stage Results :")
    print(f"   [Stage 1] Category Template Liquid Linter : {s1_res}")
    print(f"   [Stage 2] Frontmatter Schema & Asset Guard: {s2_res}")
    print(f"   [Stage 3] Mathematical Disjoint Isolation : {s3_res}")
    print(f"   [Stage 4] Ironclad Gatekeeper Quality Guard: {s4_res}")
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

    if "--install-hook" in sys.argv:
        success, msg = install_git_hook(blog_root)
        print(msg)
        return 0 if success else 1

    # Auto-ensure git pre-commit hook is installed if git repo exists
    git_dir = blog_root / ".git"
    hook_file = git_dir / "hooks" / "pre-commit"
    if git_dir.exists() and not hook_file.exists():
        install_git_hook(blog_root)

    is_valid, errors, stats = run_full_validation(blog_root)
    print_report(is_valid, errors, stats)

    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
