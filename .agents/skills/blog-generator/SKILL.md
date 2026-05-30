---
name: blog-generator
description: Generates structured blog posts from markdown templates, extracts images, calculates read time, and validates frontmatter. Use when writing long-form essays or documentation.
compatibility: Requires Python 3.8+ for template processing. Works on any OS with bash/zsh.
metadata:
  version: "1.0.0"
  author: "Quortol Team"
---

# Blog Post Generator Skill

## Overview

This skill provides tools to generate, validate, and optimize blog posts from markdown templates. It handles frontmatter extraction, image processing, read time calculation, and SEO metadata generation.

## Setup

Run once before first use:

```bash
cd /path/to/blog-generator && chmod +x scripts/*.sh
```

No additional dependencies required - uses standard Unix tools.

## Usage

### Generate Post from Template

```bash
./scripts/generate.sh "post-title" --template essay-template.md
```

### With Custom Frontmatter

```bash
./scripts/generate.sh "My Essay Title" \
  --template essay-template.md \
  --tags "AI,Future" \
  --excerpt "Exploring the future of AI agents."
```

### Validate Existing Post

```bash
./scripts/validate.sh backend/blogs/my-post.md
```

### Extract