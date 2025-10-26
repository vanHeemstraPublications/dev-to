# 🚀 DEV.to Auto-Publishing Setup Guide

Complete guide for setting up GitHub to DEV.to automation.

## Why DEV.to?

**DEV.to is BETTER than Medium for automation because:**

✅ **Active API**: Well-maintained and documented  
✅ **More features**: Series, cover images, organizations  
✅ **Better tags**: Up to 4 tags (vs Medium’s 3)  
✅ **Free forever**: No paid requirements  
✅ **Developer-friendly**: Made by developers, for developers  
✅ **Update support**: Can update existing articles  
✅ **Cover images**: API supports cover images  
✅ **Better community**: More engaged tech audience

## 📋 What You’ll Build

An automated system that:

1. Detects when you push articles to GitHub
1. Automatically publishes to DEV.to
1. Supports drafts and published articles
1. Handles updates to existing articles
1. Supports all DEV.to features (series, cover images, etc.)

## 🎯 Quick Setup (15 Minutes)

### Step 1: Get DEV.to API Key (3 minutes)

1. **Go to DEV.to settings**
- Visit: https://dev.to/settings/extensions
- Or: Click your profile → Settings → Extensions
1. **Generate API Key**
- Scroll to “DEV Community API Keys”
- Click “Generate API Key”
- Give it a description: “GitHub Auto-Publisher”
- **Copy the key immediately** - you won’t see it again!
1. **Save securely**
- Store in password manager
- You’ll need it for GitHub Secrets

### Step 2: Set Up GitHub Repository (5 minutes)

```bash
# Clone or create your repository
git clone <your-repo-url>
cd <your-repo>

# Create directory structure
mkdir -p .github/workflows articles scripts

# You should have these files:
# - .github/workflows/publish-to-devto.yml
# - scripts/publish_to_devto.py
# - articles/your-article.md
# - requirements.txt
```

### Step 3: Add GitHub Secret (2 minutes)

1. Go to your GitHub repository
1. Click **Settings** (repository settings, not profile)
1. In left sidebar: **Secrets and variables** → **Actions**
1. Click **New repository secret**
1. Enter details:
- **Name**: `DEVTO_API_KEY`
- **Secret**: Paste your DEV.to API key
1. Click **Add secret**

### Step 4: Copy Files (3 minutes)

Copy these files to your repository:

```
.github/workflows/publish-to-devto.yml  ← Workflow
scripts/publish_to_devto.py             ← Publishing script
requirements.txt                        ← Dependencies
articles/gilded-rose-devto.md          ← Your article
.gitignore                             ← Git rules
```

### Step 5: Commit and Push (2 minutes)

```bash
git add .
git commit -m "Add DEV.to auto-publishing"
git push origin main
```

### Step 6: Verify (1 minute)

1. Go to **Actions** tab in GitHub
1. You should see “Publish to DEV.to” workflow running
1. Wait for it to complete (green checkmark ✅)
1. Check DEV.to: https://dev.to/dashboard
1. Your article should appear in drafts!

## 📝 Writing Articles for DEV.to

### Article Frontmatter

DEV.to uses different frontmatter than Medium:

```yaml
---
title: "Your Article Title"
published: false              # false = draft, true = published
description: "Short summary"  # Subtitle/meta description
tags: ["python", "webdev", "tutorial", "beginners"]  # Max 4 tags
series: "Python Fundamentals" # Optional: group related articles
canonical_url: ""             # Original URL if cross-posting
cover_image: ""              # URL to cover image
organization: "the-software-s-journey"  # Optional: publish to organization
---
```

### Frontmatter Fields Explained

|Field          |Required|Description             |Example                         |
|---------------|--------|------------------------|--------------------------------|
|`title`        |✅ Yes   |Article title           |“Mastering Python Decorators”   |
|`published`    |❌ No    |Publish immediately?    |`false` (default) or `true`     |
|`description`  |❌ No    |Article subtitle/summary|“Learn decorators in 10 minutes”|
|`tags`         |❌ No    |Article tags (max 4)    |`["python", "tutorial"]`        |
|`series`       |❌ No    |Series name             |“Python Advanced Topics”        |
|`canonical_url`|❌ No    |Original post URL       |“https://yourblog.com/post”     |
|`cover_image`  |❌ No    |Cover image URL         |“https://images.com/cover.jpg”  |
|`organization` |❌ No    |Organization slug       |`"the-software-s-journey"`      |

### Complete Article Example

```markdown
---
title: "Building REST APIs with FastAPI"
published: false
description: "A comprehensive guide to creating production-ready APIs with FastAPI, including authentication, validation, and deployment"
tags: ["python", "api", "webdev", "tutorial"]
series: "Modern Python Development"
canonical_url: ""
cover_image: "https://images.unsplash.com/photo-1234567890"
organization: "the-software-s-journey"
---

# Building REST APIs with FastAPI

FastAPI is a modern, fast web framework...

## Getting Started

First, install FastAPI:

\`\`\`bash
pip install fastapi uvicorn
\`\`\`

## Your First Endpoint

\`\`\`python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
\`\`\`

...rest of your article...
```

## 🏷️ DEV.to Tags Guide

### Popular Tags (High Traffic)

**General:**

- `webdev` - Web development
- `programming` - General programming
- `tutorial` - Step-by-step guides
- `beginners` - Beginner-friendly content
- `discuss` - Discussion topics
- `showdev` - Show your projects

**Languages:**

- `javascript` - JavaScript
- `python` - Python
- `typescript` - TypeScript
- `rust` - Rust
- `go` - Go/Golang
- `java` - Java

**Frameworks:**

- `react` - React
- `vue` - Vue.js
- `angular` - Angular
- `nextjs` - Next.js
- `django` - Django
- `flask` - Flask

**Topics:**

- `devops` - DevOps
- `career` - Career advice
- `productivity` - Productivity tips
- `aws` - Amazon Web Services
- `docker` - Docker
- `kubernetes` - Kubernetes

### Tag Best Practices

1. **Use exactly 4 tags** - Maximum visibility
1. **Mix broad + specific** - e.g., `python` + `fastapi`
1. **Check tag pages** - See what’s popular in your niche
1. **Use existing tags** - DEV.to suggests tags as you type
1. **Avoid creating new tags** - Stick to established ones

## 📸 Adding Cover Images

DEV.to supports cover images via API (unlike Medium!):

### Option 1: Use Free Image Services

```yaml
cover_image: "https://unsplash.com/photos/abc123/download?w=1000"
```

**Free image sources:**

- [Unsplash](https://unsplash.com) - High-quality photos
- [Pexels](https://pexels.com) - Free stock photos
- [Pixabay](https://pixabay.com) - Free images
- [Carbon](https://carbon.now.sh) - Beautiful code screenshots

### Option 2: Host on GitHub

```yaml
cover_image: "https://raw.githubusercontent.com/username/repo/main/images/cover.jpg"
```

### Option 3: Use DEV.to CDN

1. Upload image to a draft article on DEV.to
1. Copy the CDN URL
1. Use in your frontmatter

### Cover Image Specs

- **Dimensions**: 1000x420px (or similar 1000px width)
- **Format**: JPG, PNG, or GIF
- **Size**: Under 1MB
- **Aspect Ratio**: ~2.38:1 (landscape)

## 📚 Creating Article Series

Group related articles into a series:

```yaml
series: "Mastering Python"
```

**All articles in a series must have:**

- Same exact series name (case-sensitive)
- Related content
- Logical order (readers can navigate between them)

**Series Example:**

Article 1:

```yaml
title: "Mastering Python: Part 1 - Basics"
series: "Mastering Python"
```

Article 2:

```yaml
title: "Mastering Python: Part 2 - Advanced"
series: "Mastering Python"
```

DEV.to automatically links them together!

## 🏢 Publishing to Organizations

You can publish articles to a DEV.to organization instead of your personal account.

### Benefits of Organizations

- **Branded content**: Articles appear under the organization
- **Separate analytics**: Track organization-specific metrics
- **Team collaboration**: Multiple members can publish
- **Professional appearance**: Better for companies/teams

### Setting Up Organization Publishing

1. **Create an organization on DEV.to**
   - Go to https://dev.to/settings/organizations
   - Click "New Organization"
   - Complete setup process

2. **Add organization to article frontmatter**

```yaml
---
title: "Your Article Title"
organization: "the-software-s-journey"  # Your organization slug
---
```

3. **The organization slug is the part after `dev.to/`**
   - Example: `dev.to/the-software-s-journey` → slug is `"the-software-s-journey"`

### How It Works

The publishing script automatically:
1. Fetches your organizations from DEV.to API
2. Resolves the organization slug to an organization ID
3. Publishes the article under your organization

### Example

```yaml
---
title: "The Gilded Rose Kata: Composition Over Inheritance"
published: false
description: "A deep dive into solving the Gilded Rose refactoring kata"
tags: ["python", "designpatterns", "refactoring", "tutorial"]
organization: "the-software-s-journey"
---

# Your article content...
```

### Finding Your Organization

Your organization URL will look like:
- `https://dev.to/the-software-s-journey`

The slug is everything after `dev.to/`

### Alternative: Use Organization ID

You can also use the numeric organization ID directly:

```yaml
organization_id: 12345  # Use this if you know the ID
```

The slug approach is recommended as it's more maintainable.

## 🔄 Publishing Workflow

### Option 1: Draft-First (Recommended)

```yaml
published: false  # Start as draft
```

1. Push to GitHub → Creates draft on DEV.to
1. Review draft on DEV.to
1. Make any final edits
1. Change `published: true` in GitHub
1. Push again → Article goes live!

### Option 2: Direct Publishing

```yaml
published: true  # Publish immediately
```

⚠️ **Careful!** Article goes live immediately.

### Option 3: Manual Publishing

1. Keep `published: false`
1. Review on DEV.to
1. Click “Publish” button on DEV.to manually

## 🔄 Updating Articles

The script automatically handles updates!

**When you push changes:**

1. Script checks if article exists (by title)
1. If exists → Updates the article
1. If new → Creates new article

**To update an article:**

```bash
# Edit your article
vim articles/my-article.md

# Commit and push
git add articles/my-article.md
git commit -m "Update article with new examples"
git push origin main

# GitHub Actions updates it on DEV.to
```

## 🎨 Markdown Features

DEV.to supports extended markdown:

### Liquid Tags

```markdown
{% github username/repo %}
{% youtube video_id %}
{% twitter tweet_url %}
{% codepen pen_url %}
{% glitch project_name %}
```

### Code Blocks with Syntax

```python
def hello_world():
    print("Hello, DEV.to!")
```

### Embeds

```markdown
{% embed https://www.youtube.com/watch?v=... %}
```

## 🚀 Advanced Features

### Publishing to Organization

If you’re part of a DEV.to organization:

```yaml
organization_id: 12345  # Your organization ID
```

### Multiple Languages

DEV.to doesn’t have built-in multi-language support, but you can:

1. Use tags: `["python", "spanish"]`
1. Add language in title: “Tutorial de Python (Spanish)”
1. Create separate articles per language

### Scheduling

Use GitHub Actions cron:

```yaml
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM UTC
```

## 🔍 Troubleshooting

### “Authentication failed”

- Check your DEV.to API key is correct
- Verify secret name is exactly `DEVTO_API_KEY`
- Regenerate key if needed: https://dev.to/settings/extensions

### “Tag not found”

- DEV.to only accepts existing tags
- Check tag spelling: https://dev.to/tags
- Use suggested tags when typing on DEV.to

### “Article not appearing”

- Check DEV.to dashboard (not just published)
- Look in drafts: https://dev.to/dashboard
- Check workflow logs for errors

### “Cover image not showing”

- Must be full URL (https://…)
- Image must be publicly accessible
- Check image size (< 1MB)
- Use supported format (JPG, PNG, GIF)

### “Series not linking”

- Series name must match exactly (case-sensitive)
- Both articles must be published
- Series appears after both articles exist

## 📊 DEV.to vs Medium Comparison

|Feature           |DEV.to       |Medium              |
|------------------|-------------|--------------------|
|API Status        |✅ Active     |⚠️ Limited/Deprecated|
|Cover Images      |✅ Via API    |❌ Manual only       |
|Tags              |4 maximum    |3 maximum           |
|Series Support    |✅ Yes        |❌ No                |
|Update Articles   |✅ Yes        |⚠️ Limited           |
|Organization Posts|✅ Yes        |⚠️ Publications      |
|Markdown          |✅ Extended   |✅ Basic             |
|Code Syntax       |✅ Excellent  |✅ Good              |
|Embeds            |✅ Liquid tags|❌ Limited           |
|Audience          |Developers   |General tech        |
|Paywall           |❌ Free       |⚠️ Partner program   |
|Community         |✅ Very active|✅ Active            |

## 🎯 Best Practices

### Content

1. **Start with draft** - Always review before publishing
1. **Use all 4 tags** - Maximize discoverability
1. **Add cover images** - Increases engagement
1. **Create series** - Build loyal readers
1. **Engage in comments** - Build community

### Technical

1. **Validate frontmatter** - Use YAML linter
1. **Test locally** - Run script before pushing
1. **Check workflow logs** - Debug issues quickly
1. **Keep tags consistent** - Build topic authority
1. **Update regularly** - Keep content fresh

### Growth

1. **Post consistently** - 1-2 articles per week
1. **Cross-post** - Use canonical_url for your blog
1. **Engage with others** - Comment on related articles
1. **Use trending tags** - Check DEV.to trending
1. **Share on social** - Twitter, LinkedIn, Reddit

## 📈 Tracking Success

### DEV.to Analytics

Visit: https://dev.to/dashboard/analytics

**Track these metrics:**

- **Reactions** - Hearts, Unicorns, Bookmarks
- **Comments** - Engagement level
- **Views** - Reach
- **Followers** - Audience growth

### Goals

**Week 1:**

- Publish first article
- Get comfortable with workflow

**Month 1:**

- 4-6 articles published
- Start building audience
- Engage with community

**Month 3:**

- Consistent posting schedule
- Growing follower count
- Established expertise

## 🔐 Security

**API Key Safety:**

- ✅ Store in GitHub Secrets only
- ❌ Never commit to repository
- ✅ Rotate every 6 months
- ❌ Never share publicly
- ✅ Use .gitignore properly

**Best Practices:**

- Use branch protection
- Require PR reviews
- Enable 2FA on GitHub
- Monitor workflow runs

## 📚 Additional Resources

**DEV.to:**

- [DEV.to API Docs](https://developers.forem.com/api/v1)
- [Writing Guide](https://dev.to/p/editor_guide)
- [Community Guidelines](https://dev.to/community-guidelines)

**GitHub Actions:**

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)

## ✅ Setup Checklist

Complete setup verification:

- [ ] DEV.to API key obtained
- [ ] GitHub repository created
- [ ] Directory structure created
- [ ] All files copied
- [ ] GitHub secret added (DEVTO_API_KEY)
- [ ] First article ready
- [ ] Committed and pushed
- [ ] Workflow succeeded
- [ ] Article appears on DEV.to
- [ ] Ready to write more!

## 🎉 You’re Ready!

You now have a fully automated DEV.to publishing system. Every time you push an article to GitHub, it automatically appears on DEV.to!

**Next steps:**

1. Write your second article
1. Experiment with series
1. Add cover images
1. Engage with the community
1. Build your audience

Happy writing! 📝✨

-----

**Questions?** Check the troubleshooting section or open an issue in your repository.
