#!/usr/bin/env python3
"""
Script to publish markdown articles to DEV.to using the DEV.to API.
Supports frontmatter for metadata (title, tags, cover image, series, etc.)

DEV.to API Documentation: https://developers.forem.com/api/v1
"""

import os
import sys
import json
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
            # DEV.to allows max 4 tags
            article_data["article"]["tags"] = tags[:4]
        
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
        description: Optional[str] = None
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
            article_data["article"]["tags"] = tags[:4]
        
        if series is not None:
            article_data["article"]["series"] = series
        
        if canonical_url is not None:
            article_data["article"]["canonical_url"] = canonical_url
        
        if cover_image is not None:
            article_data["article"]["main_image"] = cover_image
        
        if description is not None:
            article_data["article"]["description"] = description
        
        response = requests.put(
            f"{self.base_url}/articles/{article_id}",
            headers=self.headers,
            json=article_data
        )
        response.raise_for_status()
        return response.json()
    
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
        print(f"✓ Authenticated as: {user_info['name']} (@{user_info['username']})")
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to authenticate with DEV.to: {e}")
        sys.exit(1)
    
    # Find all markdown files in articles directory
    articles_dir = Path("articles")
    if not articles_dir.exists():
        print("ERROR: 'articles' directory not found")
        sys.exit(1)
    
    markdown_files = list(articles_dir.glob("*.md"))
    if not markdown_files:
        print("No markdown files found in 'articles' directory")
        sys.exit(0)
    
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
            
            # Check if article already exists
            existing_article = publisher.find_article_by_title(title)
            
            if existing_article:
                print(f"  Article exists (ID: {existing_article['id']}), updating...")
                result = publisher.update_article(
                    article_id=existing_article["id"],
                    title=title,
                    body_markdown=content,
                    published=published,
                    tags=tags,
                    series=series,
                    canonical_url=canonical_url,
                    cover_image=cover_image,
                    description=description
                )
                print(f"✓ Updated: {result['title']}")
            else:
                print(f"  Creating new article...")
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
            print(f"  Status: {'Published' if result.get('published') else 'Draft'}")
            success_count += 1
            
        except Exception as e:
            print(f"✗ Failed to publish {md_file.name}: {e}")
            continue
    
    print(f"\n{'='*50}")
    print(f"Processed {success_count} of {len(markdown_files)} articles")
    
    if success_count < len(markdown_files):
        sys.exit(1)


if __name__ == "__main__":
    main()
