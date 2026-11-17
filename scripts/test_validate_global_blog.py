#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit and Integration Tests for Market Context 360 Global Blog Validator
------------------------------------------------------------------------
Tests real repository validation as well as all synthetic edge cases,
failure paths, schema violations, multi-clause tags, plural categories,
forbidden elsif branches, rogue category directories, and mathematical disjointness.
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path
import pytest
import yaml

# Ensure scripts directory is in path
sys.path.insert(0, str(Path(__file__).parent))

from validate_global_blog import (
    ALLOWED_CATEGORIES,
    RESEARCH_PILLARS,
    EXCLUDED_CATEGORIES_FROM_RESEARCH,
    find_blog_root,
    extract_frontmatter,
    validate_category_templates,
    validate_post_frontmatter,
    evaluate_liquid_condition,
    validate_mathematical_isolation,
    install_git_hook,
    run_full_validation,
)


@pytest.fixture
def real_blog_root():
    """Returns the path to the real stock_blog_global repository."""
    return find_blog_root()


def test_real_blog_repository_passes(real_blog_root):
    """Verifies that the actual repository passes all 3 validation stages with zero errors."""
    is_valid, errors, stats = run_full_validation(real_blog_root)
    assert is_valid is True, f"Real repository failed validation: {errors}"
    assert len(errors) == 0
    assert stats["templates_checked"] == 4
    assert stats["posts_checked"] >= 2
    assert stats["stage1_errors"] == 0
    assert stats["stage2_errors"] == 0
    assert stats["stage3_errors"] == 0


def test_category_templates_strict_liquid(real_blog_root):
    """Verifies each category template strictly filters by post.category with no tag pollution."""
    errors, conditions = validate_category_templates(real_blog_root)
    assert errors == []
    assert len(conditions) == 4
    for p_key, cond in conditions.items():
        exp_cat = RESEARCH_PILLARS[p_key]["category"]
        assert f"post.category == '{exp_cat}'" in cond or f'post.category == "{exp_cat}"' in cond


def test_loose_tag_pollution_detection(tmp_path):
    """Verifies that injecting 'tags contains' into a category template triggers Stage 1 failure."""
    mock_cat_dir = tmp_path / "category" / "macro"
    mock_cat_dir.mkdir(parents=True)
    bad_template = mock_cat_dir / "index.html"
    bad_template.write_text(
        """---
layout: default
permalink: /category/macro/
---
{% for post in site.posts %}
  {% if post.category == 'Macro Intelligence' or post.tags contains 'MacroIntelligence' %}
    <p>{{ post.title }}</p>
  {% endif %}
{% endfor %}
""",
        encoding="utf-8",
    )

    # Populate other templates correctly
    for p_key, p_info in RESEARCH_PILLARS.items():
        if p_key == "macro":
            continue
        p_dir = tmp_path / "category" / p_key
        p_dir.mkdir(parents=True)
        (p_dir / "index.html").write_text(
            f"""---
layout: default
permalink: {p_info['permalink']}
---
{{% for post in site.posts %}}
  {{% if post.category == '{p_info['category']}' %}}
    <p>{{{{ post.title }}}}</p>
  {{% endif %}}
{{% endfor %}}
""",
            encoding="utf-8",
        )

    errors, _ = validate_category_templates(tmp_path)
    assert len(errors) >= 1
    assert any("[Template Tag Pollution]" in e for e in errors)
    assert any("[Template Loose OR]" in e for e in errors)


def test_forbidden_elsif_branch_detection(tmp_path):
    """Verifies that using 'elsif' in a category template triggers Stage 1 failure."""
    for p_key, p_info in RESEARCH_PILLARS.items():
        p_dir = tmp_path / "category" / p_key
        p_dir.mkdir(parents=True)
        template_file = p_dir / "index.html"
        if p_key == "equities":
            template_file.write_text(
                f"""---
layout: default
permalink: {p_info['permalink']}
---
{{% for post in site.posts %}}
  {{% if post.category == '{p_info['category']}' %}}
    <p>{{{{ post.title }}}}</p>
  {{% elsif post.category == 'Macro Intelligence' %}}
    <p>Leak</p>
  {{% endif %}}
{{% endfor %}}
""",
                encoding="utf-8",
            )
        else:
            template_file.write_text(
                f"""---
layout: default
permalink: {p_info['permalink']}
---
{{% for post in site.posts %}}
  {{% if post.category == '{p_info['category']}' %}}
    <p>{{{{ post.title }}}}</p>
  {{% endif %}}
{{% endfor %}}
""",
                encoding="utf-8",
            )

    errors, _ = validate_category_templates(tmp_path)
    assert any("[Template Forbidden Elsif]" in e for e in errors)


def test_unauthorized_category_directory(tmp_path):
    """Verifies that an unregistered directory under category/ triggers Stage 1 failure."""
    for p_key, p_info in RESEARCH_PILLARS.items():
        p_dir = tmp_path / "category" / p_key
        p_dir.mkdir(parents=True)
        (p_dir / "index.html").write_text(
            f"""---
layout: default
permalink: {p_info['permalink']}
---
{{% for post in site.posts %}}
  {{% if post.category == '{p_info['category']}' %}}
    <p>{{{{ post.title }}}}</p>
  {{% endif %}}
{{% endfor %}}
""",
            encoding="utf-8",
        )

    # Inject unauthorized category directory
    rogue_dir = tmp_path / "category" / "crypto-speculation"
    rogue_dir.mkdir(parents=True)
    (rogue_dir / "index.html").write_text("rogue", encoding="utf-8")

    errors, _ = validate_category_templates(tmp_path)
    assert any("[Unauthorized Category Directory]" in e for e in errors)
    assert any("crypto-speculation" in e for e in errors)


def test_category_mismatch_detection(tmp_path):
    """Verifies that if a template checks the wrong category name, it triggers Stage 1 failure."""
    for p_key, p_info in RESEARCH_PILLARS.items():
        p_dir = tmp_path / "category" / p_key
        p_dir.mkdir(parents=True)
        wrong_cat = "Equities & Factor Research" if p_key == "macro" else p_info["category"]
        (p_dir / "index.html").write_text(
            f"""---
layout: default
permalink: {p_info['permalink']}
---
{{% for post in site.posts %}}
  {{% if post.category == '{wrong_cat}' %}}
    <p>{{{{ post.title }}}}</p>
  {{% endif %}}
{{% endfor %}}
""",
            encoding="utf-8",
        )

    errors, _ = validate_category_templates(tmp_path)
    assert any("[Template Category Mismatch]" in e for e in errors)


def test_invalid_post_category(tmp_path):
    """Verifies that an unauthorized category in frontmatter triggers Stage 2 failure."""
    posts_dir = tmp_path / "_posts"
    posts_dir.mkdir(parents=True)
    post_file = posts_dir / "2026-11-16-test-post.md"
    post_file.write_text(
        """---
title: "Test Publication"
date: 2026-11-16 10:00:00 +0900
category: "Crypto Moonshot Speculation"
tags: [Crypto, Bitcoin]
author: "Test Author"
summary: "Test summary text"
layout: post
---
Body text.
""",
        encoding="utf-8",
    )

    meta, errors = validate_post_frontmatter(post_file, tmp_path)
    assert any("[Post Unauthorized Category]" in e for e in errors)


def test_ambiguous_categories_plural_field(tmp_path):
    """Verifies that specifying ambiguous 'categories' (plural) triggers Stage 2 failure."""
    posts_dir = tmp_path / "_posts"
    posts_dir.mkdir(parents=True)
    post_file = posts_dir / "2026-11-16-test-post.md"
    post_file.write_text(
        """---
title: "Test Ambiguous Categories"
date: 2026-11-16 10:00:00 +0900
category: "Macro Intelligence"
categories: ["Macro Intelligence", "Equities & Factor Research"]
tags: [Liquidity]
author: "Test Author"
summary: "Test summary"
layout: post
---
Body text.
""",
        encoding="utf-8",
    )

    meta, errors = validate_post_frontmatter(post_file, tmp_path)
    assert any("[Post Ambiguous Categories]" in e for e in errors)


def test_missing_frontmatter_fields(tmp_path):
    """Verifies that missing required fields trigger Stage 2 errors."""
    posts_dir = tmp_path / "_posts"
    posts_dir.mkdir(parents=True)
    post_file = posts_dir / "2026-11-16-test-post.md"
    post_file.write_text(
        """---
title: "Incomplete Post"
tags: [Macro]
---
Body text.
""",
        encoding="utf-8",
    )

    meta, errors = validate_post_frontmatter(post_file, tmp_path)
    assert any("missing required field: 'category'" in e for e in errors)
    assert any("missing required field: 'date'" in e for e in errors)
    assert any("missing required field: 'author'" in e for e in errors)


def test_missing_image_asset_reference(tmp_path):
    """Verifies that referencing a non-existent asset triggers [Missing Asset] error."""
    posts_dir = tmp_path / "_posts"
    posts_dir.mkdir(parents=True)
    post_file = posts_dir / "2026-11-16-test-post.md"
    post_file.write_text(
        """---
title: "Test Post With Missing Image"
date: 2026-11-16 10:00:00 +0900
category: "Macro Intelligence"
tags: [Fed]
author: "Test Author"
summary: "Test summary"
layout: post
---
Here is an image:
![Non existent image](/assets/images/posts/ghost-chart.png)
""",
        encoding="utf-8",
    )

    meta, errors = validate_post_frontmatter(post_file, tmp_path)
    assert any("[Missing Asset]" in e for e in errors)
    assert any("ghost-chart.png" in e for e in errors)


def test_manifesto_isolation_and_disjointness():
    """Verifies mathematical disjoint set and manifesto isolation logic."""
    posts_mock = {
        "post1.md": {"category": "Macro Intelligence"},
        "post2.md": {"category": "Equities & Factor Research"},
        "manifesto.md": {"category": "Platform Manifesto"},
    }
    errors = validate_mathematical_isolation(posts_mock)
    assert errors == []


def test_unrouted_research_post():
    """Verifies that if a post maps to an unrecognized category, it is flagged."""
    posts_mock = {
        "unrouted.md": {"category": "Unknown Sector"},
    }
    errors = validate_mathematical_isolation(posts_mock)
    assert any("[Unrouted Research Post]" in e for e in errors)


def test_disjoint_set_collision_simulation():
    """
    Simulates a real collision scenario:
    Equities template has loose tag matching 'post.tags contains SP500'.
    A Macro post tagged with 'SP500' matches BOTH Macro and Equities templates.
    Verifies that Stage 3 simulation catches:
    1. [Disjoint Set Violation]
    2. [Multiple Category Routing Violation]
    3. [Template Incongruence]
    """
    posts_mock = {
        "fed-liquidity.md": {
            "category": "Macro Intelligence",
            "tags": ["FederalReserve", "SP500"],
        },
        "apple-fcf.md": {
            "category": "Equities & Factor Research",
            "tags": ["Apple", "CashFlow"],
        },
    }

    # Equities template improperly includes loose tag condition
    tampered_conditions = {
        "macro": "post.category == 'Macro Intelligence'",
        "technicals": "post.category == 'Market Structure & Technicals'",
        "options-income": "post.category == 'Options & Systematic Income'",
        "equities": "post.category == 'Equities & Factor Research' or post.tags contains 'SP500'",
    }

    errors = validate_mathematical_isolation(posts_mock, tampered_conditions)
    assert any("[Disjoint Set Violation]" in e for e in errors)
    assert any("fed-liquidity.md" in e for e in errors)
    assert any("[Multiple Category Routing Violation]" in e for e in errors)
    assert any("[Template Incongruence]" in e for e in errors)


def test_manifesto_leak_simulation():
    """
    Simulates an accidental template leakage where Manifesto matches a research pillar.
    Verifies that [Manifesto Leak Violation] is raised.
    """
    posts_mock = {
        "post1.md": {"category": "Macro Intelligence", "tags": []},
        "manifesto.md": {"category": "Platform Manifesto", "tags": ["ManifestoTag"]},
    }

    tampered_conditions = {
        "macro": "post.category == 'Macro Intelligence' or post.tags contains 'ManifestoTag'",
        "technicals": "post.category == 'Market Structure & Technicals'",
        "options-income": "post.category == 'Options & Systematic Income'",
        "equities": "post.category == 'Equities & Factor Research'",
    }

    errors = validate_mathematical_isolation(posts_mock, tampered_conditions)
    assert any("[Manifesto Leak Violation]" in e for e in errors)
    assert any("manifesto.md" in e for e in errors)


def test_install_git_hook(tmp_path):
    """Verifies that install_git_hook creates a functional pre-commit script."""
    git_dir = tmp_path / ".git"
    git_dir.mkdir(parents=True)

    success, msg = install_git_hook(tmp_path)
    assert success is True
    hook_file = git_dir / "hooks" / "pre-commit"
    assert hook_file.exists()
    content = hook_file.read_text(encoding="utf-8")
    assert "validate_global_blog.py" in content


if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))
