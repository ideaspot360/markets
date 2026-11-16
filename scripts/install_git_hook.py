#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Market Context 360 - Git Pre-Commit Hook Installer
---------------------------------------------------
Installs the automated Blog Integrity Guard pre-commit hook into
the local .git/hooks directory.
"""

import sys
from pathlib import Path
from validate_global_blog import find_blog_root, install_git_hook


def main() -> int:
    try:
        blog_root = find_blog_root()
    except Exception as e:
        print(f"[FATAL] Could not find blog root: {e}", file=sys.stderr)
        return 1

    success, message = install_git_hook(blog_root)
    if success:
        print(f"✅ {message}")
        return 0
    else:
        print(f"❌ {message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
