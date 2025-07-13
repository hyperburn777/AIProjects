#!/usr/bin/env python3
"""
AP News Scraper
Scrapes the top news stories from https://apnews.com/
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import sys
from typing import List, Dict, Optional
import re

class APNewsScraper:
    def __init__(self):
        self.base_url = "https://apnews.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse the webpage content."""
        try:
            print(f"Fetching content from {url}...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def extract_story_info(self, article_element) -> Optional[Dict]:
        """Extract story information from an article element."""
        try:
            # Look for headline
            headline_elem = article_element.find(['h1', 'h2', 'h3', 'h4'], class_=re.compile(r'headline|title'))
            if not headline_elem:
                headline_elem = article_element.find(['h1', 'h2', 'h3', 'h4'])
            
            if not headline_elem:
                return None
            
            headline = headline_elem.get_text(strip=True)
            if not headline:
                return None
            
            # Look for link
            link_elem = article_element.find('a', href=True)
            link = link_elem['href'] if link_elem else None
            if link and not link.startswith('http'):
                link = self.base_url + link
            
            # Look for summary/description
            summary_elem = article_element.find(['p', 'div'], class_=re.compile(r'summary|description|excerpt'))
            if not summary_elem:
                summary_elem = article_element.find('p')
            
            summary = summary_elem.get_text(strip=True) if summary_elem else ""
            
            # Look for timestamp
            time_elem = article_element.find(['time', 'span'], class_=re.compile(r'time|date|timestamp'))
            timestamp = time_elem.get_text(strip=True) if time_elem else ""
            
            # Look for category/tag
            category_elem = article_element.find(['span', 'div'], class_=re.compile(r'category|tag|section'))
            category = category_elem.get_text(strip=True) if category_elem else ""
            
            return {
                'headline': headline,
                'summary': summary,
                'link': link,
                'timestamp': timestamp,
                'category': category
            }
        except Exception as e:
            print(f"Error extracting story info: {e}")
            return None
    
    def get_full_article_text(self, article_url: str) -> str:
        """Fetch and extract the full article text from the article page."""
        if not article_url:
            return ""
        
        try:
            print(f"Fetching full article from: {article_url}")
            soup = self.get_page_content(article_url)
            if not soup:
                return ""
            
            # Try multiple selectors to find article content
            content_selectors = [
                '[class*="article-body"]',
                '[class*="story-body"]',
                '[class*="content-body"]',
                'article p',
                '.article-content p',
                '.story-content p'
            ]
            
            article_text = []
            
            for selector in content_selectors:
                paragraphs = soup.select(selector)
                if paragraphs:
                    print(f"Found {len(paragraphs)} paragraphs with selector: {selector}")
                    break
            
            if not paragraphs:
                # Fallback: look for any paragraph in the main content area
                paragraphs = soup.find_all('p')
            
            for p in paragraphs:
                # Get text while preserving spacing around links
                text = p.get_text(separator=' ', strip=True)
                if text and len(text) > 50:  # Only include substantial paragraphs
                    # Clean up multiple spaces but preserve paragraph breaks
                    text = re.sub(r'\s+', ' ', text)
                    article_text.append(text)
            
            # Join with double newlines to preserve paragraph spacing
            return '\n\n'.join(article_text)
            
        except Exception as e:
            print(f"Error fetching full article: {e}")
            return ""
    
    def scrape_top_stories(self, max_stories: int = 5) -> List[Dict]:
        """Scrape top stories from AP News homepage with full article text."""
        soup = self.get_page_content(self.base_url)
        if not soup:
            return []
        
        stories = []
        
        # Try multiple selectors to find articles
        selectors = [
            'article',
            '[class*="story"]',
            '[class*="article"]',
            '[class*="card"]',
            'div[class*="feed"] > div',
            'div[class*="content"] > div'
        ]
        
        for selector in selectors:
            articles = soup.select(selector)
            if articles:
                print(f"Found {len(articles)} potential articles with selector: {selector}")
                break
        
        if not articles:
            print("No articles found with any selector. Trying fallback approach...")
            # Fallback: look for any div with text that might be a headline
            articles = soup.find_all(['div', 'article'], class_=True)
        
        for article in articles:
            if len(stories) >= max_stories:
                break
            
            story_info = self.extract_story_info(article)
            if story_info and story_info['headline']:
                # Avoid duplicates
                if not any(s['headline'] == story_info['headline'] for s in stories):
                    # Get full article text if we have a link
                    if story_info['link']:
                        print(f"\nGetting full article for: {story_info['headline'][:50]}...")
                        full_text = self.get_full_article_text(story_info['link'])
                        story_info['full_text'] = full_text
                    else:
                        story_info['full_text'] = ""
                    
                    stories.append(story_info)
                    
                    # Add a small delay to be respectful to the server
                    time.sleep(1)
        
        return stories[:max_stories]
    
    def scrape_section(self, section_url: str, max_stories: int = 10) -> List[Dict]:
        """Scrape stories from a specific section."""
        full_url = self.base_url + section_url if not section_url.startswith('http') else section_url
        soup = self.get_page_content(full_url)
        if not soup:
            return []
        
        stories = []
        articles = soup.select('article, [class*="story"], [class*="article"]')
        
        for article in articles:
            if len(stories) >= max_stories:
                break
            
            story_info = self.extract_story_info(article)
            if story_info and story_info['headline']:
                if not any(s['headline'] == story_info['headline'] for s in stories):
                    stories.append(story_info)
        
        return stories[:max_stories]
    
    def save_to_json(self, stories: List[Dict], folder_path: str = "", filename: Optional[str] = None):
        """Save stories to a JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ap_news_stories_{timestamp}.json"
        
        if folder_path:
            import os
            filepath = os.path.join(folder_path, filename)
        else:
            filepath = filename
        
        data = {
            'scraped_at': datetime.now().isoformat(),
            'source': 'AP News',
            'url': self.base_url,
            'stories': stories
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Stories saved to {filepath}")
        except Exception as e:
            print(f"Error saving to file: {e}")
    
    def save_to_txt(self, stories: List[Dict], folder_path: str = "", filename: Optional[str] = None):
        """Save stories to a simple text file for easy reading."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ap_news_stories_{timestamp}.txt"
        
        if folder_path:
            import os
            filepath = os.path.join(folder_path, filename)
        else:
            filepath = filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("TOP STORIES FROM AP NEWS\n")
                f.write(f"Scraped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total stories: {len(stories)}\n")
                f.write("=" * 80 + "\n\n")
                
                for i, story in enumerate(stories, 1):
                    f.write(f"{i:2d}. {story['headline']}\n")
                    
                    if story['category']:
                        f.write(f"    Category: {story['category']}\n")
                    if story['timestamp']:
                        f.write(f"    Time: {story['timestamp']}\n")
                    if story['summary']:
                        # Truncate long summaries
                        summary = story['summary'][:200] + "..." if len(story['summary']) > 200 else story['summary']
                        f.write(f"    Summary: {summary}\n")
                    if story['link']:
                        f.write(f"    Link: {story['link']}\n")
                    
                    f.write("\n")
            
            print(f"Stories saved to {filepath}")
        except Exception as e:
            print(f"Error saving to text file: {e}")
    
    def save_stories_to_separate_files(self, stories: List[Dict]) -> str:
        """Save each story to a separate file within the top_stories folder."""
        import os
        
        folder_name = "top_stories"
        
        try:
            # Create the folder
            os.makedirs(folder_name, exist_ok=True)
            print(f"Using folder: {folder_name}")
            
            for i, story in enumerate(stories, 1):
                # Create a safe filename from the headline
                safe_headline = re.sub(r'[<>:"/\\|?*]', '_', story['headline'])
                safe_headline = safe_headline[:100]  # Limit length
                filename = f"{i:02d}_{safe_headline}.txt"
                filepath = os.path.join(folder_name, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("=" * 80 + "\n")
                    f.write(f"STORY {i} OF {len(stories)}\n")
                    f.write("=" * 80 + "\n\n")
                    
                    f.write(f"HEADLINE: {story['headline']}\n")
                    f.write("-" * 80 + "\n\n")
                    
                    if story['category']:
                        f.write(f"Category: {story['category']}\n")
                    if story['timestamp']:
                        f.write(f"Published: {story['timestamp']}\n")
                    if story['link']:
                        f.write(f"Source: {story['link']}\n")
                    
                    f.write("\n" + "=" * 80 + "\n")
                    f.write("FULL ARTICLE TEXT\n")
                    f.write("=" * 80 + "\n\n")
                    
                    if story.get('full_text'):
                        f.write(story['full_text'])
                    elif story.get('summary'):
                        f.write(story['summary'])
                    else:
                        f.write("No article text available.\n")
                    
                    f.write("\n\n" + "=" * 80 + "\n")
                    f.write(f"End of Story {i}\n")
                    f.write("=" * 80 + "\n")
                
                print(f"Saved story {i}: {filename}")
            
            return folder_name
            
        except Exception as e:
            print(f"Error saving stories to separate files: {e}")
            return ""
    
    def print_stories(self, stories: List[Dict], show_details: bool = True):
        """Print stories in a formatted way."""
        if not stories:
            print("No stories found.")
            return
        
        print(f"\n{'='*80}")
        print(f"TOP STORIES FROM AP NEWS")
        print(f"Scraped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total stories: {len(stories)}")
        print(f"{'='*80}\n")
        
        for i, story in enumerate(stories, 1):
            print(f"{i:2d}. {story['headline']}")
            
            if show_details:
                if story['category']:
                    print(f"    Category: {story['category']}")
                if story['timestamp']:
                    print(f"    Time: {story['timestamp']}")
                if story['summary']:
                    # Truncate long summaries
                    summary = story['summary'][:150] + "..." if len(story['summary']) > 150 else story['summary']
                    print(f"    Summary: {summary}")
                if story['link']:
                    print(f"    Link: {story['link']}")
            
            print()

def main():
    """Main function to run the scraper."""
    print("AP News Scraper")
    print("=" * 50)
    
    # Clear the top_stories folder if it exists
    import os
    top_stories_folder = "top_stories"
    if os.path.exists(top_stories_folder):
        for filename in os.listdir(top_stories_folder):
            file_path = os.path.join(top_stories_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    import shutil
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    
    scraper = APNewsScraper()
    
    try:
        # Scrape top stories with full article text
        print("Scraping top 5 stories from AP News with full article text...")
        stories = scraper.scrape_top_stories(max_stories=5)
        
        if stories:
            # Print stories
            scraper.print_stories(stories, show_details=True)
            
            # Save each story to separate files in top_stories folder
            folder_name = scraper.save_stories_to_separate_files(stories)
            
            # Save to JSON in the same folder
            if folder_name:
                scraper.save_to_json(stories, folder_name)
            
            print(f"\nSuccessfully scraped {len(stories)} stories!")
            print("Files saved:")
            print(f"- All files saved in: {folder_name}/")
            print("  - Individual story files (01_, 02_, etc.)")
            print("  - JSON file: ap_news_stories_[timestamp].json")
        else:
            print("No stories were found. The website structure might have changed.")
            
    except KeyboardInterrupt:
        print("\nScraping interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import requests
        import bs4
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please install required packages:")
        print("pip install requests beautifulsoup4")
        sys.exit(1)
    
    sys.exit(main())
