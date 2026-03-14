#!/usr/bin/env python3
"""
Script to publish markdown articles to DEV.to using the DEV.to API.
Supports frontmatter for metadata (title, tags, cover image, series, etc.)

DEV.to API Documentation: https://developers.forem.com/api/v1
"""

import os
import sys
import time
import requests
import frontmatter
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode


class DevToPublisher:
    """Handles publishing articles to DEV.to via their API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://dev.to/api"
        self.headers = {
            "api-key": api_key,
            "Content-Type": "application/json"
        }

    def _request_with_retry(
        self,
        method: str,
        url: str,
        *,
        json: Optional[Dict] = None,
    ) -> requests.Response:
        timeout_s = int(os.environ.get("DEVTO_HTTP_TIMEOUT_SECONDS", "30"))
        max_retries = int(os.environ.get("DEVTO_MAX_RETRIES", "6"))
        base_sleep_s = float(os.environ.get("DEVTO_RETRY_BASE_SLEEP_SECONDS", "2"))

        last_exc: Optional[Exception] = None
        for attempt in range(max_retries):
            try:
                resp = requests.request(
                    method,
                    url,
                    headers=self.headers,
                    json=json,
                    timeout=timeout_s,
                )

                if resp.status_code in {429, 500, 502, 503, 504}:
                    retry_after = resp.headers.get("Retry-After")
                    if retry_after and retry_after.isdigit():
                        sleep_s = int(retry_after)
                    else:
                        sleep_s = base_sleep_s * (2 ** attempt)
                    print(
                        f"  Retrying DEV.to request ({resp.status_code}) in "
                        f"{sleep_s:.0f}s..."
                    )
                    time.sleep(sleep_s)
                    continue

                return resp
            except requests.exceptions.RequestException as exc:
                last_exc = exc
                sleep_s = base_sleep_s * (2 ** attempt)
                print(
                    f"  Network error talking to DEV.to, retrying in "
                    f"{sleep_s:.0f}s..."
                )
                time.sleep(sleep_s)

        if last_exc:
            raise last_exc
        raise requests.exceptions.RequestException("DEV.to request failed")
    
    @staticmethod
    def sanitize_tags(tags: List[str]) -> List[str]:
        """
        Sanitize tags to meet DEV.to requirements.
        DEV.to tags must be lowercase and purely alphanumeric (no hyphens, underscores, or special characters).
        All non-alphanumeric characters are removed.
        """
        sanitized = []
        for tag in tags:
            if not tag:
                continue
            # Convert to lowercase
            tag = tag.lower()
            # Remove ALL non-alphanumeric characters (only keep letters and numbers)
            tag = ''.join(c for c in tag if c.isalnum())
            if tag:  # Only add non-empty tags
                sanitized.append(tag)
        return sanitized
    
    def get_user_info(self) -> Dict:
        """Retrieve authenticated user information."""
        response = self._request_with_retry(
            "GET",
            f"{self.base_url}/users/me",
        )
        response.raise_for_status()
        return response.json()
    
    def get_my_articles(self) -> List[Dict]:
        """Get list of user's published articles."""
        response = self._request_with_retry(
            "GET",
            f"{self.base_url}/articles/me/all",
        )
        response.raise_for_status()
        return response.json()
    
    def get_my_organizations(self) -> List[Dict]:
        """Get list of user's organizations."""
        # Forem/DEV.to API does not reliably expose "list my orgs" for API keys.
        # We keep this method best-effort; callers should handle [].
        # Try different API endpoints for organizations
        endpoints = [
            f"{self.base_url}/organizations",
            f"{self.base_url}/organizations/users/me",
            f"{self.base_url}/users/me/organizations"
        ]
        
        for endpoint in endpoints:
            try:
                response = self._request_with_retry("GET", endpoint)
                response.raise_for_status()
                orgs = response.json()
                # Handle different response formats
                if isinstance(orgs, list):
                    return orgs
                elif isinstance(orgs, dict) and 'organizations' in orgs:
                    return orgs['organizations']
                elif isinstance(orgs, dict) and 'data' in orgs:
                    return orgs['data']
                return orgs
            except requests.exceptions.RequestException:
                continue
        
        return []
    
    def create_article(
        self,
        title: str,
        body_markdown: str,
        published: bool = False,
        tags: Optional[List[str]] = None,
        series: Optional[str] = None,
        canonical_url: Optional[str] = None,
        cover_image: Optional[str] = None,
        description: Optional[str] = None,
        organization_id: Optional[int] = None
    ) -> Dict:
        """
        Create a new article on DEV.to.
        
        Args:
            title: Article title
            body_markdown: Article content in markdown
            published: Whether to publish immediately (default: False = draft)
            tags: List of tags (max 4, must exist on DEV.to)
            series: Name of series (optional)
            canonical_url: Original URL if cross-posting
            cover_image: URL to cover image
            description: Article description/subtitle
            organization_id: ID if publishing to organization
        
        Returns:
            Response data from DEV.to API
        """
        article_data = {
            "article": {
                "title": title,
                "body_markdown": body_markdown,
                "published": published,
            }
        }
        
        if tags:
            # Sanitize tags and limit to 4 (DEV.to maximum)
            sanitized_tags = self.sanitize_tags(tags)
            article_data["article"]["tags"] = sanitized_tags[:4]
        
        if series:
            article_data["article"]["series"] = series
        
        if canonical_url:
            article_data["article"]["canonical_url"] = canonical_url
        
        if cover_image:
            article_data["article"]["main_image"] = cover_image
        
        if description:
            article_data["article"]["description"] = description
        
        if organization_id:
            article_data["article"]["organization_id"] = organization_id
        
        response = self._request_with_retry(
            "POST",
            f"{self.base_url}/articles",
            json=article_data,
        )
        response.raise_for_status()
        return response.json()
    
    def update_article(
        self,
        article_id: int,
        title: Optional[str] = None,
        body_markdown: Optional[str] = None,
        published: Optional[bool] = None,
        tags: Optional[List[str]] = None,
        series: Optional[str] = None,
        canonical_url: Optional[str] = None,
        cover_image: Optional[str] = None,
        description: Optional[str] = None,
        organization_id: Optional[int] = None
    ) -> Dict:
        """
        Update an existing article on DEV.to.
        
        Args:
            article_id: The ID of the article to update
            Other args: Same as create_article (only include fields to update)
        
        Returns:
            Response data from DEV.to API
        """
        article_data = {"article": {}}
        
        if title is not None:
            article_data["article"]["title"] = title
        
        if body_markdown is not None:
            article_data["article"]["body_markdown"] = body_markdown
        
        if published is not None:
            article_data["article"]["published"] = published
        
        if tags is not None:
            # Sanitize tags and limit to 4 (DEV.to maximum)
            sanitized_tags = self.sanitize_tags(tags)
            article_data["article"]["tags"] = sanitized_tags[:4]
        
        if series is not None:
            article_data["article"]["series"] = series
        
        if canonical_url is not None:
            article_data["article"]["canonical_url"] = canonical_url
        
        if cover_image is not None:
            article_data["article"]["main_image"] = cover_image
        
        if description is not None:
            article_data["article"]["description"] = description
        
        if organization_id is not None:
            article_data["article"]["organization_id"] = organization_id
        
        response = self._request_with_retry(
            "PUT",
            f"{self.base_url}/articles/{article_id}",
            json=article_data,
        )
        
        # Provide better error messages
        if not response.ok:
            error_msg = f"{response.status_code} {response.reason}"
            try:
                error_data = response.json()
                if isinstance(error_data, dict):
                    if 'error' in error_data:
                        error_msg += f": {error_data['error']}"
                    elif 'errors' in error_data:
                        error_msg += f": {error_data['errors']}"
                    elif 'message' in error_data:
                        error_msg += f": {error_data['message']}"
                    # Print full error data for debugging
                    print(f"  API Error Response: {error_data}")
            except ValueError:
                # If response is not JSON, include response text
                error_msg += f": {response.text[:200]}"
            
            # Create a custom exception with better message
            raise requests.exceptions.HTTPError(error_msg, response=response)
        
        return response.json()
    
    def get_article_by_id(self, article_id: int) -> Optional[Dict]:
        """Get a specific article by ID with full details."""
        try:
            response = requests.get(
                f"{self.base_url}/articles/{article_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None
    
    def find_article_by_title(self, title: str) -> Optional[Dict]:
        """Find an existing article by title."""
        articles = self.get_my_articles()
        for article in articles:
            if article["title"] == title:
                return article
        return None


def add_cache_busting_to_url(url: str) -> str:
    """
    Add a timestamp-based cache-busting parameter to a URL.
    This ensures DEV.to fetches the latest version of images.
    
    Args:
        url: The URL to add cache-busting to
        
    Returns:
        URL with ?v=<timestamp> parameter added
    """
    if not url:
        return url
    
    # Parse the URL
    parsed = urlparse(url)
    
    # Get existing query parameters
    query_params = parse_qs(parsed.query)
    
    # Add or update the version parameter with current timestamp
    timestamp = int(datetime.now().timestamp())
    query_params['v'] = [str(timestamp)]
    
    # Reconstruct the URL with updated query parameters
    new_query = urlencode(query_params, doseq=True)
    new_parsed = parsed._replace(query=new_query)
    
    return urlunparse(new_parsed)


def process_markdown_file(file_path: Path) -> tuple:
    """
    Process a markdown file with frontmatter.
    
    Returns:
        Tuple of (metadata dict, content string)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)
    
    metadata = post.metadata
    content = post.content
    
    return metadata, content


def normalize_tags(tags_value: Any) -> List[str]:
    """
    Normalize DEV.to tags from frontmatter into a list of strings.

    Frontmatter authors commonly write:
      - tags: tag1, tag2, tag3        (string)
      - tags: [tag1, tag2, tag3]      (list)
      - tags:
        - tag1
        - tag2
    """
    if tags_value is None:
        return []

    # Common case: a single comma-separated string.
    if isinstance(tags_value, str):
        raw = tags_value.strip()
        if not raw:
            return []
        parts = raw.split(",") if "," in raw else raw.split()
        return [p.strip().lstrip("#") for p in parts if p.strip().lstrip("#")]

    # List/tuple/set from YAML frontmatter.
    if isinstance(tags_value, (list, tuple, set)):
        out: List[str] = []
        for item in tags_value:
            if item is None:
                continue
            if isinstance(item, str):
                s = item.strip()
                if not s:
                    continue
                # If someone mixes "tag1, tag2" within a list item, split it too.
                parts = s.split(",") if "," in s else [s]
                out.extend([p.strip().lstrip("#") for p in parts if p.strip().lstrip("#")])
            else:
                out.append(str(item))
        return out

    # Fallback: coerce scalars (int/bool/etc.) to a single tag string.
    return [str(tags_value)]


def main():
    """Main execution function."""
    # Get DEV.to API key from environment
    api_key = os.environ.get("DEVTO_API_KEY")
    if not api_key:
        print("ERROR: DEVTO_API_KEY environment variable not set")
        sys.exit(1)
    
    # Initialize publisher
    publisher = DevToPublisher(api_key)
    
    # Get user info
    try:
        user_info = publisher.get_user_info()
        print(f"✓ Authenticated as: {user_info['name']} "
              f"(@{user_info['username']})")
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to authenticate with DEV.to: {e}")
        sys.exit(1)
    
    # Get user's organizations
    org_dict: Dict[str, int] = {}
    organizations = publisher.get_my_organizations()
    if isinstance(organizations, list) and organizations:
        org_dict = {
            org.get("slug"): org.get("id")
            for org in organizations
            if org.get("slug") and org.get("id")
        }
        print(f"✓ Loaded {len(organizations)} organizations")
    else:
        print(
            "Warning: Could not load organizations from API."
        )
        print(
            "  Continuing without organization lookup - will publish to personal "
            "account unless you set organization_id in frontmatter or provide "
            "DEVTO_ORG_SLUG/DEVTO_ORG_ID."
        )

    # Optional: provide organization slug->id mapping via environment variables
    # (useful when the API can't list organizations for the given API key).
    env_org_slug = (os.environ.get("DEVTO_ORG_SLUG") or "").strip()
    env_org_id_raw = (os.environ.get("DEVTO_ORG_ID") or "").strip()
    if env_org_slug and env_org_id_raw.isdigit():
        org_dict[env_org_slug] = int(env_org_id_raw)
        print(f"✓ Using organization mapping from env for slug: {env_org_slug}")
    
    # Determine which files to process
    # Check for files from environment variable (set by GitHub Actions)
    files_to_process = os.environ.get("FILES_TO_PUBLISH", "").strip()
    
    if files_to_process:
        # Process specific files from environment variable
        file_paths = [f.strip() for f in files_to_process.split('\n') if f.strip()]
        markdown_files = [Path(f) for f in file_paths if Path(f).exists() and f.endswith('.md')]
        if not markdown_files:
            print(f"ERROR: No valid markdown files found in provided list: {file_paths}")
            sys.exit(1)
        print(f"Processing {len(markdown_files)} specified file(s)")
    else:
        # Fallback: Find all markdown files in articles directory
        articles_dir = Path("articles")
        if not articles_dir.exists():
            print("ERROR: 'articles' directory not found")
            sys.exit(1)
        
        markdown_files = list(articles_dir.rglob("*.md"))
        if not markdown_files:
            print("No markdown files found in 'articles' directory")
            sys.exit(0)
        print(f"Processing all {len(markdown_files)} file(s) in articles directory")
    
    # Process each article
    success_count = 0
    delay_s = float(os.environ.get("DEVTO_DELAY_SECONDS", "3"))
    for md_file in markdown_files:
        print(f"\n📝 Processing: {md_file.name}")
        
        try:
            metadata, content = process_markdown_file(md_file)
            
            # Extract metadata with defaults
            title = metadata.get("title", md_file.stem)
            tags = normalize_tags(metadata.get("tags", []))
            published = metadata.get("published", False)
            series = metadata.get("series")
            canonical_url = metadata.get("canonical_url")
            cover_image = metadata.get("cover_image")
            description = metadata.get("description")
            organization_id = metadata.get("organization_id")
            organization_slug = metadata.get("organization")
            
            # Sanitize tags (DEV.to doesn't allow hyphens, spaces, or special chars)
            original_tags = tags.copy() if tags else []
            tags = publisher.sanitize_tags(tags) if tags else []
            if original_tags != tags:
                print(f"  Note: Tags sanitized from {original_tags} to {tags}")
            
            # Convert empty strings to None (empty strings in YAML frontmatter)
            if series == "":
                series = None
            if canonical_url == "":
                canonical_url = None
            if cover_image == "":
                cover_image = None
            if description == "":
                description = None
            
            # Add cache-busting timestamp to cover image URL
            if cover_image:
                original_cover_image = cover_image
                cover_image = add_cache_busting_to_url(cover_image)
                if cover_image != original_cover_image:
                    print(f"  Added cache-busting parameter to cover image URL")
            
            # Resolve organization ID if slug provided
            if organization_slug and organization_slug in org_dict:
                organization_id = org_dict[organization_slug]
            elif organization_slug:
                print(f"  Warning: Organization '{organization_slug}' not found. Publishing to personal account.")
                organization_id = None
            
            # Check if article already exists
            existing_article = publisher.find_article_by_title(title)
            
            if existing_article:
                art_id = existing_article['id']
                print(f"  Article exists (ID: {art_id}), updating...")
                
                # Fetch full article details to get organization information and published status
                full_article = publisher.get_article_by_id(art_id)
                if full_article:
                    # Preserve organization_id from existing article if it belongs to an organization
                    # This is critical - articles published to organizations must keep their organization_id
                    existing_org_id = None
                    if 'organization' in full_article:
                        org = full_article['organization']
                        if isinstance(org, dict) and 'id' in org:
                            existing_org_id = org['id']
                        elif isinstance(org, int):
                            existing_org_id = org
                    
                    if existing_org_id:
                        print(f"  Preserving organization_id: {existing_org_id} from existing article")
                        organization_id = existing_org_id
                    elif organization_id is None and organization_slug:
                        # Try to resolve organization if not already resolved
                        if organization_slug in org_dict:
                            organization_id = org_dict[organization_slug]
                            print(f"  Using organization_id: {organization_id} for slug: {organization_slug}")
                    
                    # Preserve published status if article is already published
                    # This prevents accidentally unpublishing articles when frontmatter has published: false
                    existing_published = full_article.get('published', False)
                    if existing_published:
                        if published:
                            print(f"  Article is already published, maintaining published status")
                        else:
                            # Article is published but frontmatter says false
                            # Preserve published status to avoid accidentally unpublishing
                            print(f"  Preserving published status: article is already published (frontmatter has published: false, but keeping it published)")
                            published = True
                    elif not existing_published and published:
                        print(f"  Publishing article (was draft, frontmatter has published: true)")
                else:
                    # Fallback: try to get org from the basic article data
                    existing_org_id = existing_article.get('organization', {}).get('id') if isinstance(existing_article.get('organization'), dict) else None
                    if existing_org_id:
                        print(f"  Preserving organization_id: {existing_org_id} from article list")
                        organization_id = existing_org_id
                    
                    # Preserve published status from basic article data
                    existing_published = existing_article.get('published', False)
                    if existing_published:
                        if published:
                            print(f"  Article is already published, maintaining published status")
                        else:
                            # Article is published but frontmatter says false - preserve status
                            print(f"  Preserving published status: article is already published (frontmatter has published: false, but keeping it published)")
                            published = True
                    elif not existing_published and published:
                        print(f"  Publishing article (was draft, frontmatter has published: true)")
                
                result = publisher.update_article(
                    article_id=existing_article["id"],
                    title=title,
                    body_markdown=content,
                    published=published,
                    tags=tags,
                    series=series,
                    canonical_url=canonical_url,
                    cover_image=cover_image,
                    description=description,
                    organization_id=organization_id
                )
                print(f"✓ Updated: {result['title']}")
                # Show detailed status information
                result_published = result.get('published', False)
                result_url = result.get('url', 'N/A')
                print(f"  Published Status: {'PUBLISHED' if result_published else 'DRAFT'}")
                print(f"  URL: {result_url}")
                if not result_published:
                    print(f"  ⚠️  WARNING: Article is still a DRAFT. It will not be publicly accessible until published.")
            else:
                print("  Creating new article...")
                result = publisher.create_article(
                    title=title,
                    body_markdown=content,
                    published=published,
                    tags=tags,
                    series=series,
                    canonical_url=canonical_url,
                    cover_image=cover_image,
                    description=description,
                    organization_id=organization_id
                )
                print(f"✓ Created: {result['title']}")
                # Show detailed status information
                result_published = result.get('published', False)
                result_url = result.get('url', 'N/A')
                print(f"  Published Status: {'PUBLISHED' if result_published else 'DRAFT'}")
                print(f"  URL: {result_url}")
                if not result_published:
                    print(f"  ⚠️  WARNING: Article is still a DRAFT. It will not be publicly accessible until published.")
                else:
                    print(f"  ✓ Article is PUBLISHED and publicly accessible")
            success_count += 1
            
        except Exception as e:
            print(f"✗ Failed to publish {md_file.name}: {e}")
            import traceback
            print(f"  Error details: {traceback.format_exc()}")
            continue
        finally:
            if delay_s > 0:
                time.sleep(delay_s)
    
    print(f"\n{'='*50}")
    print(f"Processed {success_count} of {len(markdown_files)} articles")
    
    if success_count < len(markdown_files):
        print(f"ERROR: {len(markdown_files) - success_count} article(s) failed to publish")
        sys.exit(1)


if __name__ == "__main__":
    main()
