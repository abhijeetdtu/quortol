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

### Evaluate Propositional Idea Density

Use the repository's CPIDR-inspired evaluator for an English Markdown (`.md`)
or plain-text (`.txt`) document, or for every supported file below a directory:

```bash
python scripts/evaluate_blog_cpidr.py backend/blogs/my-post.md
python scripts/evaluate_blog_cpidr.py path/to/source.txt
python scripts/evaluate_blog_cpidr.py backend/blogs --format json --output cpidr-report.json
```

Install spaCy and its English model first:

```bash
pip install -r backend/requirements.txt
python -m spacy download en_core_web_sm
```

The score is diagnostic only. It approximates propositional idea density using
a modern POS tagger and selected rules from Brown et al. (2008); it is not
numerically interchangeable with the original CPIDR 3 or proprietary CPIDR 5.
