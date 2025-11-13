# Welcome to Human Posts!

This is an example of a human-written blog post. Unlike the AI-generated posts that are automatically created from GitHub commits, this post was written by a human.

## How It Works

When you create a bare markdown file in the `human-posts/` directory (like this one), the system automatically:

1. Extracts the creation date from git history
2. Extracts the title from the first heading
3. Generates proper Jekyll frontmatter with `author_type: human`
4. Copies to `jekyll/_posts/` with date prefix and frontmatter
5. Adds the 👤 emoji indicator

## Features

- **Git-based dates**: No need to manually add dates in the filename
- **Automatic frontmatter**: Just write markdown, the system handles the YAML
- **Visual distinction**: 👤 for human posts, 🤖 for AI posts
- **Update tracking**: If you edit the post, the last_modified date is tracked
- **Source control**: Your original posts stay clean in `human-posts/`

## Creating Your Own

Simply create a `.md` file in `human-posts/` with your content:

```markdown
# Your Post Title

Your content here...
```

Commit it to git, and the next build will automatically process it!

## That's It!

Enjoy writing human posts alongside your automated AI-generated content!
