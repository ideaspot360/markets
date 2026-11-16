#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit and Integration Tests for Market Context 360 Global Blog Validator
------------------------------------------------------------------------
Tests real repository validation as well as all synthetic edge cases,
failure paths, schema violations, and mathematical disjointness guards.
"""

import os
import shutil
import tempfile
from pathlib import Path
import pytest
import yaml

from validate_global_blog import (
    ALLOWED_CATEGORIES,
    RESEARCH_PILLARS,
    find_blog_root,
    extract_frontmatter,
    validate_category_templates,
    validate_post_frontmatter,
    validate_mathematical_isolation,
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
    errors = validate_category_templates(real_blog_root)
    assert errors == []


def test_loose_tag_pollution_detection(tmp_path):
    """Verifies that injecting 'tags contains' into a category template triggers Stage 1 failure."""
    # Create mock blog structure
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

    errors = validate_category_templates(tmp_path)
    assert len(errors) >= 1
    assert any("[Template Tag Pollution]" in e for e in errors)
    assert any("[Template Loose OR]" in e for e in errors)


def test_category_mismatch_detection(tmp_path):
    """Verifies that if a template checks the wrong category name, it triggers Stage 1 failure."""
    for p_key, p_info in RESEARCH_PILLARS.items():
        p_dir = tmp_path / "category" / p_key
        p_dir.mkdir(parents=True)
        # Invert macro and equities
        wrong_cat = "US Systematic Equity" if p_key == "macro" else p_info["category"]
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

    errors = validate_category_templates(tmp_path)
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
        "post2.md": {"category": "US Systematic Equity"},
        "manifesto.md": {"category": "Platform Manifesto"},
    }
    errors = validate_mathematical_isolation(posts_mock, Path("."))
    assert errors == []


def test_disjointness_violation_synthetic():
    """Verifies that if a post maps to an unrecognized category, it is flagged."""
    posts_mock = {
        "unrouted.md": {"category": "Unknown Sector"},
    }
    errors = validate_mathematical_isolation(posts_mock, Path("."))
    assert any("[Unrouted Research Post]" in e for e in errors)
