---
title: "Crossplane Snapshot Testing: Your Infrastructure’s Photoshoot Session 📸"
published: false
description: "Learn how snapshot testing in Crossplane is like running a professional photoshoot - complete with reference photos, Photoshop comparisons, and the occasional wardrobe malfunction"
tags: [crossplane, kubernetes, testing, devops]
series: “Infrastructure as Code"
cover_image: ""
canonical_url: ""
organization: "the-software-s-journey"
---

Ever wondered what your infrastructure would look like if it had to go through a professional photoshoot? Well, buckle up, because that’s exactly what snapshot testing in Crossplane is all about! Just like a fashion photographer meticulously compares test shots against reference photos, we’re going to make sure our Crossplane compositions look *absolutely fabulous* every single time.

## The Studio Setup: Understanding Test-Driven Development with Snapshots

Picture this: You’re a high-end fashion photographer preparing for a major campaign. Before the actual shoot, you create detailed reference shots showing exactly how the final photos should look. Every detail matters - the lighting, the pose, the background, even that mysterious smudge that somehow makes it into every third photo.

In Crossplane terms, these reference shots are your **snapshot tests**. They’re frozen-in-time representations of how your infrastructure compositions should render. Just like a photographer wouldn’t want their model showing up in pajamas when the shoot calls for evening wear, you don’t want your Crossplane compositions suddenly generating the wrong cloud resources!

## Why Snapshot Testing? (aka “Why Not Just Eyeball It?”)

Traditional testing is like describing your ideal photograph in words:

```python
def test_render_traditional():
    result = render_composition()
    assert "apiVersion: pkg.crossplane.io/v1" in result
    assert "kind: Provider" in result
    assert "name: provider-aws-s3" in result
    # ... 47 more assertions about what should be in the photo
```

That’s exhausting! It’s like writing a novel to describe what could be a single reference photo.

Snapshot testing says: “Just take a picture and compare”:

```python
def test_render_snapshot(snapshot):
    result = render_composition()
    assert result == snapshot  # One line. Boom. 📸
```

## Act 1: The Reference Shoot (Creating Your First Snapshots)

Let’s start with the basics. When you create a snapshot test, you’re essentially doing a reference photoshoot. You’re saying, “This is EXACTLY how my composition should look, and I’m taking a picture to prove it!”

### Step 1: Setting Up Your Studio (The Test Environment)

First, we need our photography studio. Install Syrupy (our camera):

```bash
pip install syrupy
```

Or add it to your `requirements.txt` (because professionals keep their equipment organized):

```toml
[project.optional-dependencies]
test = [
    "pytest",
    "syrupy",  # Our fancy camera
]
```

### Step 2: The First Photo Session

Here’s your first test (think of it as a test shoot):

```python
# tests/unit/test_render_snapshot.py
def test_s3_bucket_composition_snapshot(snapshot):
    """
    Our S3 bucket composition's debut photoshoot.
    If it changes unexpectedly, we'll know immediately.
    """
    rendered = render_composition("s3-bucket-composition.yaml")
    assert rendered == snapshot
```

Now, take the reference photo:

```bash
pytest --snapshot-update
```

**What just happened?**

1. Your test ran
1. Syrupy captured the output (took the photo)
1. Saved it to `__snapshots__/test_render_snapshot.ambr`
1. Test passed ✓ (because there’s nothing to compare yet)

The snapshot file looks like this:

```python
# serializer version: 1
# name: test_s3_bucket_composition_snapshot
  '''
  apiVersion: s3.aws.crossplane.io/v1beta1
  kind: Bucket
  metadata:
    name: my-fancy-bucket
  spec:
    forProvider:
      region: us-east-1
  '''
# ---
```

This is your reference photo! 📸

## Act 2: The Photoshop Session (Detecting Changes)

Now comes the magic. Every time you run your tests, Syrupy acts like a meticulous Photoshop expert doing a pixel-perfect comparison.

Run your tests normally (no `--snapshot-update`):

```bash
pytest
```

**Scenario 1: Nothing Changed (Perfect Match)**

```
✓ test_s3_bucket_composition_snapshot PASSED
```

Your composition still looks exactly like the reference photo. Ship it!

**Scenario 2: Something Changed (The “Wait, What?” Moment)**

Someone “accidentally” changed your bucket name from `my-fancy-bucket` to `my-fancy-bukkit` (typos happen in the best studios):

```diff
AssertionError: Snapshot does not match

- Snapshot
+ Received

  apiVersion: s3.aws.crossplane.io/v1beta1
  kind: Bucket
  metadata:
-   name: my-fancy-bucket
+   name: my-fancy-bukkit  # <-- Houston, we have a problem
  spec:
    forProvider:
      region: us-east-1
```

This is like Photoshop’s “Difference” mode highlighting exactly what changed between two images. Except instead of pixels, it’s YAML!

## Act 3: The Wardrobe Change (Intentional Updates)

Sometimes you *want* to change things. Maybe your composition needs to evolve - perhaps you’re adding versioning to that S3 bucket (it’s growing up! 🥲).

**Step 1: Make your changes**

```python
def render_composition(name):
    return {
        "apiVersion": "s3.aws.crossplane.io/v1beta1",
        "kind": "Bucket",
        "metadata": {"name": name},
        "spec": {
            "forProvider": {
                "region": "us-east-1",
                "versioningConfiguration": {  # New wardrobe!
                    "status": "Enabled"
                }
            }
        }
    }
```

**Step 2: See the diff**

```bash
pytest  # This will fail - we changed the outfit!
```

**Step 3: Review the changes like a professional**

Look at the diff. Is this what you intended? Did someone sneak a Hawaiian shirt into a black-tie photoshoot?

**Step 4: Update the reference photo (if it looks good)**

```bash
pytest --snapshot-update
```

This is saying: “Yes, I approve this new look. Update the portfolio!”

## The TDD Photoshoot Workflow (Red → Green → Refactor)

Test-Driven Development with snapshots is like planning a photoshoot from concept to final image:

### 1. Red: The Concept Sketch (Write Failing Test)

```python
def test_versioned_bucket_snapshot(snapshot):
    """We want buckets with versioning. Let's see how it looks!"""
    config = generate_versioned_bucket(
        name="my-bucket",
        versioning=True
    )
    assert config == snapshot
```

First run (creates the baseline):

```bash
pytest --snapshot-update  # Takes the first "concept" photo
```

### 2. Green: The Actual Shoot (Implement Feature)

```python
def generate_versioned_bucket(name, versioning=False):
    """Now let's make this real"""
    config = {
        "apiVersion": "s3.aws.crossplane.io/v1beta1",
        "kind": "Bucket",
        "metadata": {"name": name},
        "spec": {"forProvider": {"region": "us-east-1"}}
    }
    
    if versioning:
        config["spec"]["forProvider"]["versioningConfiguration"] = {
            "status": "Enabled"
        }
    
    return config
```

Run the test:

```bash
pytest  # Should pass - matches our snapshot
```

### 3. Refactor: The Post-Production (Improve Without Breaking)

Maybe you want to clean up the code, make it more modular:

```python
def generate_versioned_bucket(name, versioning=False):
    """Refactored - cleaner, more maintainable"""
    base = _create_base_bucket(name)
    
    if versioning:
        _add_versioning(base)
    
    return base

def _create_base_bucket(name):
    return {
        "apiVersion": "s3.aws.crossplane.io/v1beta1",
        "kind": "Bucket",
        "metadata": {"name": name},
        "spec": {"forProvider": {"region": "us-east-1"}}
    }

def _add_versioning(config):
    config["spec"]["forProvider"]["versioningConfiguration"] = {
        "status": "Enabled"
    }
```

Run the test again:

```bash
pytest  # Still passes! Same output, better code
```

The reference photo hasn’t changed (the *what*), but your process improved (the *how*). This is the magic of snapshot testing!

## The Multi-Model Shoot (Testing Multiple Scenarios)

Real photoshoots have different looks, different outfits, different poses. Same with your compositions:

```python
@pytest.mark.parametrize("region,encryption", [
    ("us-east-1", True),
    ("eu-west-1", True),
    ("ap-south-1", False),
])
def test_regional_bucket_snapshot(region, encryption, snapshot):
    """Different regions, different security requirements"""
    bucket = generate_regional_bucket(region, encryption)
    assert bucket == snapshot
```

This creates separate reference photos for each combination:

- `test_regional_bucket_snapshot[us-east-1-True]`
- `test_regional_bucket_snapshot[eu-west-1-True]`
- `test_regional_bucket_snapshot[ap-south-1-False]`

Each gets its own snapshot in your portfolio!

## The Photo Retouching Guide (Filtering Sensitive Data)

Sometimes you need to retouch photos before saving them (remove blemishes, adjust lighting). In testing, this means filtering out dynamic or sensitive values:

```python
import re

def test_composition_without_secrets_snapshot(snapshot):
    """Clean up the photo - no secrets in the portfolio!"""
    rendered = render_composition("secure-app.yaml")
    
    # Blur out the passwords (like blurring faces in witness protection)
    retouched = re.sub(
        r'password: .*',
        'password: <REDACTED>',
        rendered
    )
    
    assert retouched == snapshot
```

## The Portfolio Management Guide (Best Practices)

### 1. **Version Control Your Portfolio**

Your snapshots ARE your tests. Check them in!

```bash
git add __snapshots__/
git commit -m "Add snapshot tests for new bucket composition"
```

### 2. **Review Changes Like a Professional**

When someone submits changes:

```bash
git diff __snapshots__/
```

Look carefully! Did they actually mean to change the bucket region from `us-east-1` to `eu-west-1`, or did their cat walk across the keyboard?

### 3. **Keep Your Shots Focused**

```python
# Good: Focused shot
def test_bucket_policy_snapshot(snapshot):
    """Just testing the bucket policy - nothing else"""
    policy = generate_bucket_policy()
    assert policy == snapshot

# Bad: Everything including the kitchen sink
def test_entire_infrastructure_snapshot(snapshot):
    """Testing... um... everything? All 10,000 lines?"""
    everything = generate_all_resources()
    assert everything == snapshot  # Good luck debugging this!
```

### 4. **Use Descriptive Names (Your Portfolio Needs Labels)**

```python
# Good: You know exactly what this tests
def test_bucket_with_versioning_enabled_snapshot(snapshot): ...

# Bad: What bucket? What test? Is this even mine?
def test_bucket_snapshot(snapshot): ...
```

## Common Photography Disasters (And How to Avoid Them)

### Disaster 1: The “Update Everything Without Looking” Approach

❌ **Don’t do this:**

```bash
# NO NO NO NO NO
pytest --snapshot-update && git add . && git commit -m "updated snapshots"
```

This is like approving photos without looking at them. That’s how embarrassing photos end up in the portfolio!

✅ **Do this instead:**

```bash
# Review the changes first!
pytest  # See what changed

# Look at the actual diff
git diff __snapshots__/

# THEN decide if the changes are good
pytest --snapshot-update
```

### Disaster 2: The “Moving Target” Photoshoot

❌ **Bad: Non-deterministic data**

```python
import datetime

def test_snapshot_with_timestamp(snapshot):
    """This will NEVER work consistently"""
    config = {
        "timestamp": datetime.datetime.now().isoformat(),  # Different every time!
        "data": "value"
    }
    assert config == snapshot  # 😭
```

✅ **Good: Fixed reference data**

```python
def test_snapshot_deterministic(snapshot):
    """Ah, much better"""
    config = {
        "timestamp": "2024-01-15T10:00:00Z",  # Same every time
        "data": "value"
    }
    assert config == snapshot  # 😊
```

### Disaster 3: The “Photograph Everything” Approach

❌ **Bad: One massive snapshot**

```python
def test_everything_snapshot(snapshot):
    """Testing 10,000 lines of YAML in one test"""
    assert massive_infrastructure == snapshot
```

When this fails, good luck figuring out what went wrong!

✅ **Good: Multiple focused snapshots**

```python
def test_networking_config_snapshot(snapshot):
    assert networking == snapshot

def test_security_config_snapshot(snapshot):
    assert security == snapshot

def test_database_config_snapshot(snapshot):
    assert database == snapshot
```

## The Complete Photoshoot Example

Here’s a full example showing snapshot testing in action:

```python
# tests/unit/test_crossplane_composition.py
import pytest
from crossplane_renderer import (
    render_composition,
    render_with_parameters
)

def test_basic_s3_bucket_snapshot(snapshot):
    """Our basic S3 bucket - the classic headshot"""
    rendered = render_composition("s3-bucket-basic.yaml")
    assert rendered == snapshot

def test_encrypted_bucket_snapshot(snapshot):
    """S3 bucket with encryption - the security glamour shot"""
    rendered = render_with_parameters(
        "s3-bucket.yaml",
        encryption=True,
        versioning=True
    )
    assert rendered == snapshot

@pytest.mark.parametrize("environment", ["dev", "staging", "prod"])
def test_environment_specific_snapshot(environment, snapshot):
    """Different environments - different photoshoot themes"""
    rendered = render_composition(
        "s3-bucket.yaml",
        env=environment
    )
    assert rendered == snapshot

def test_complete_composition_snapshot(snapshot):
    """
    The full composition portfolio:
    - Resource Group
    - S3 Bucket  
    - Bucket Policy
    - CloudFront Distribution
    
    This is our magazine cover spread!
    """
    rendered = render_composition("complete-cdn-composition.yaml")
    assert rendered == snapshot
```

**First time (create the portfolio):**

```bash
pytest --snapshot-update
```

**Every other time (verify against portfolio):**

```bash
pytest
```

**When something changes intentionally:**

```bash
pytest  # Review the diff
pytest --snapshot-update  # Approve the new shots
```

## The Studio Workflow Summary

1. **Create reference photos** (`pytest --snapshot-update`)
1. **Run comparisons** (`pytest`)
1. **Review any differences** (`git diff __snapshots__/`)
1. **Update when intentional** (`pytest --snapshot-update`)
1. **Version control everything** (`git add __snapshots__/`)

## Why This Matters (The “Money Shot”)

Snapshot testing catches the changes you *didn’t* mean to make:

- Someone refactored composition logic and accidentally changed AWS regions
- A “minor” update to a function caused ripple effects across 15 resources
- That “harmless” variable rename broke the naming conventions required by Azure
- A library upgrade changed how YAML is serialized

Without snapshots, these slip through. With snapshots, they show up in your diff like a photobomber in a wedding photo - impossible to miss!

## Resources (Your Photography References)

- **Syrupy Documentation**: [github.com/syrupy-project/syrupy](https://github.com/syrupy-project/syrupy)
- **Crossplane Rendering**: Use `crossplane render` locally before testing
- **Testing Philosophy**: Think in portfolios, not just individual shots

## The Final Frame

Snapshot testing is your infrastructure’s professional photoshoot. It ensures that every render of your Crossplane compositions matches your carefully curated reference portfolio.

When someone asks “did this change break anything?”, your tests don’t just say “yes” or “no” - they show you a side-by-side comparison like a Photoshop expert pointing out every pixel that shifted.

Now go forth and photograph your infrastructure! 📸✨

-----

**About the Author**: I’m Willem, a Cloud Engineer who believes testing infrastructure should be as straightforward as comparing photos - because who has time to manually verify 10,000 lines of YAML? Not this guy.
