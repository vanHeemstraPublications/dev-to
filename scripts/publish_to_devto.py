#!/usr/bin/env python3
"""
Script to publish markdown articles to DEV.to using the DEV.to API.
Supports frontmatter for metadata (title, tags, cover image, series, etc.)

DEV.to API Documentation: https://developers.forem.com/api/v1
"""

import os
import sys
import requests
import frontmatter
from pathlib import Path
from typing import Dict, List, Optional


class DevToPublisher:
    """Handles publishing articles to DEV.to via their API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://dev.to/api"
        self.headers = {
            "api-key": api_key,
            "Content-Type": "application/json"
        }
    
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
        response = requests.get(
            f"{self.base_url}/users/me",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_my_articles(self) -> List[Dict]:
        """Get list of user's published articles."""
        response = requests.get(
            f"{self.base_url}/articles/me/all",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_my_organizations(self) -> List[Dict]:
        """Get list of user's organizations."""
        # Try different API endpoints for organizations
        endpoints = [
            f"{self.base_url}/organizations",
            f"{self.base_url}/organizations/users/me",
            f"{self.base_url}/users/me/organizations"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, headers=self.headers)
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
        
        # If all endpoints fail, raise the last error
        raise requests.exceptions.RequestException("Could not fetch organizations from any endpoint")
    
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
        
        response = requests.post(
            f"{self.base_url}/articles",
            headers=self.headers,
            json=article_data
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
        
        response = requests.put(
            f"{self.base_url}/articles/{article_id}",
            headers=self.headers,
            json=article_data
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
    try:
        organizations = publisher.get_my_organizations()
        # Handle different organization response formats
        if isinstance(organizations, list):
            org_dict = {org.get('slug'): org.get('id') for org in organizations if org.get('slug') and org.get('id')}
            print(f"✓ Loaded {len(organizations)} organizations")
        else:
            print(f"Warning: Unexpected organizations response format: {type(organizations)}")
            org_dict = {}
    except requests.exceptions.RequestException as e:
        print(f"Warning: Could not load organizations: {e}")
        print("  Continuing without organization lookup - will use organization_id from existing articles if available")
        org_dict = {}
    
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
        
        markdown_files = list(articles_dir.glob("*.md"))
        if not markdown_files:
            print("No markdown files found in 'articles' directory")
            sys.exit(0)
        print(f"Processing all {len(markdown_files)} file(s) in articles directory")
    
    # Process each article
    success_count = 0
    for md_file in markdown_files:
        print(f"\n📝 Processing: {md_file.name}")
        
        try:
            metadata, content = process_markdown_file(md_file)
            
            # Extract metadata with defaults
            title = metadata.get("title", md_file.stem)
            tags = metadata.get("tags", [])
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
            
            print(f"  URL: {result['url']}")
            status = 'Published' if result.get('published') else 'Draft'
            print(f"  Status: {status}")
            success_count += 1
            
        except Exception as e:
            print(f"✗ Failed to publish {md_file.name}: {e}")
            import traceback
            print(f"  Error details: {traceback.format_exc()}")
            continue
    
    print(f"\n{'='*50}")
    print(f"Processed {success_count} of {len(markdown_files)} articles")
    
    if success_count < len(markdown_files):
        print(f"ERROR: {len(markdown_files) - success_count} article(s) failed to publish")
        sys.exit(1)


if __name__ == "__main__":
    main()
