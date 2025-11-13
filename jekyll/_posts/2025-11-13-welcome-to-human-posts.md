---
layout: post
title: "Welcome to Human Posts!"
date: 2025-11-13 14:50:58 +0100
categories: blog
author_type: human
---

# Welcome to Human Posts!

This is an example of a human-written blog post. Unlike the AI-generated posts that are automatically created from GitHub commits, this post was written by a human.

## How It Works

When you create a bare markdown file in the `jekyll/_posts/` directory (like this one), the system automatically:

1. Detects it lacks frontmatter
2. Extracts the creation date from git history
3. Extracts the title from the first heading
4. Generates proper Jekyll frontmatter with `author_type: human`
5. Adds the 👤 emoji indicator

## Features

- **Git-based dates**: No need to manually add dates in the filename
- **Automatic frontmatter**: Just write markdown, the system handles the YAML
- **Visual distinction**: 👤 for human posts, 🤖 for AI posts
- **Update tracking**: If you edit the post, the last_modified date is tracked

## Creating Your Own

Simply create a `.md` file in `jekyll/_posts/` with your content:

```markdown
# Your Post Title

Your content here...
```

Commit it to git, and the next build will automatically process it!

## That's It!

Enjoy writing human posts alongside your automated AI-generated content!
