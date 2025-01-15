from typing import Any, Dict, Optional
import os
from pathlib import Path
import time
import re
import requests
from bs4 import BeautifulSoup
from PyQt6.QtGui import QPixmap
from PIL import Image
from io import BytesIO


from utils.core.word_count import clean_page_count, estimate_word_count
from utils.core.paths import get_base_dir

class GoodreadsClient:

    BASE_URL = "https://www.goodreads.com"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    # year
    CACHE_MAX_AGE = 365 * 24 * 60 * 60  

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.cache_dir = Path(get_base_dir()) / "cache" / "covers"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        # Run cleanup on initialization
        self.cleanup_cache()

    def _is_isbn(self, query: str) -> bool:
        return query.isdigit() and len(query) == 13

    def _get_book_page_url(
        self, query: str, isbn: Optional[str] = None
    ) -> Optional[str]:
        # First try ISBN if provided
        if isbn and self._is_isbn(isbn):
            return f"{self.BASE_URL}/book/isbn/{isbn}"

        # Then try query as ISBN
        if self._is_isbn(query):
            return f"{self.BASE_URL}/book/isbn/{query}"

        # Fall back to title search
        search_url = f"{self.BASE_URL}/search?q={query.replace(' ', '+')}"

        try:
            return self.create_book_url(search_url)
        except Exception as e:
            print(f"Error getting book page URL: {e}")
            return None

    def create_book_url(self, search_url):
        response = self.session.get(search_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        book_link = soup.select_one("a.bookTitle")
        if not book_link or not (book_url := book_link.get("href")):
            return None

        return f"{self.BASE_URL}{book_url}"

    def get_book_info(
        self, query: str, isbn: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        book_url = self._get_book_page_url(query, isbn)
        if not book_url:
            return None

        try:
            return self.extract_book_info(book_url, isbn)
        except Exception as e:
            print(f"Error fetching book info: {e}")
            return None

    def extract_book_info(self, book_url, isbn):
        response = self.session.get(book_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.select_one("h1[data-testid='bookTitle']")
        author = soup.select_one("span.ContributorLink__name")
        rating = soup.select_one("div.RatingStatistics__rating")
        pages = soup.select_one("p[data-testid='pagesFormat']")

        if not title:
            return None

        # Calculate estimated word count if page count is available
        page_count = clean_page_count(pages.text) if pages else 0
        word_count = estimate_word_count(page_count) if page_count else 0

        return {
            "title": title.text.strip(),
            "author": author.text.strip() if author else "Unknown Author",
            "rating": float(rating.text.strip()) if rating else 0.0,
            "isbn": isbn or None,
            "length": word_count,  # Add estimated word count
        }

    def _clean_filename(self, title: str, author: str, isbn: Optional[str] = None) -> str:
        """Generate a clean filename based on title, author, and optionally ISBN."""
        # Remove special characters and whitespace
        clean_title = re.sub(r'[^\w\s-]', '', title.lower())
        clean_author = re.sub(r'[^\w\s-]', '', author.lower())
        
        # Only include ISBN in filename if it's a valid string and not "N/A"
        if isbn and isbn.strip() and isbn != "N/A":
            return f"{clean_title}_{clean_author}_{isbn}".replace(' ', '_')
        return f"{clean_title}_{clean_author}".replace(' ', '_')

    def _get_cache_path(self, title: str, author: str, isbn: Optional[str] = None) -> Path:
        """Get the cache path for the cover image."""
        filename = self._clean_filename(title, author, isbn) + ".jpg"
        return self.cache_dir / filename

    def _load_cached_cover(self, title: str, author: str, isbn: Optional[str] = None) -> Optional[QPixmap]:
        """Load the cached cover image using the correct file path."""
        cache_path = self._get_cache_path(title, author, isbn)
        if cache_path.exists():
            # Update access time when loading from cache
            os.utime(cache_path, None)
            pixmap = QPixmap()
            if pixmap.load(str(cache_path)):
                return pixmap
        return None


    def _save_cover_to_cache(self, title: str, author: str, image_data: bytes, isbn: Optional[str] = None) -> bool:
        try:
            # Open the image using Pillow
            image = Image.open(BytesIO(image_data))

            # Resize the image to 400x600
            resized_image = image.resize((400, 600), Image.Resampling.LANCZOS)

            # Save the image with the appropriate filename
            cache_path = self._get_cache_path(title, author, isbn)
            resized_image.save(cache_path, format='JPEG')
            print(f"Saved cover to cache: {cache_path}")
            return True
        except Exception as e:
            print(f"Error saving resized cover to cache: {e}")
            return False

        
    def cleanup_cache(self):
        """Remove cached covers that haven't been accessed in CACHE_MAX_AGE seconds."""
        try:
            current_time = time.time()
            removed = 0
            for cache_file in self.cache_dir.glob("*.jpg"):
                # Get last access time of the file
                last_access = os.path.getatime(cache_file)
                if current_time - last_access > self.CACHE_MAX_AGE:
                    cache_file.unlink()
                    removed += 1
            if removed > 0:
                print(f"Removed {removed} old covers from cache")
        except Exception as e:
            print(f"Error during cache cleanup: {e}")

    def get_cover(self, title: str, author: str, isbn: Optional[str] = None) -> Optional[QPixmap]:
        # First try title cache
        print(f"Checking title cache for: {title}")
        if cached_cover := self._load_cached_cover(title, author, isbn):
            print(f"Found cover in title cache for: {title}")
            return cached_cover

        print("No cached cover found, fetching from web...")
        # If not in cache, fetch from web
        book_url = self._get_book_page_url(title, isbn)
        if not book_url:
            return None

        try:
            return self.extract_cover(book_url, title, author, isbn)
        except Exception as e:
            print(f"Error fetching cover: {e}")
            return None


    def extract_cover(self, book_url: str, title: str, author: str, isbn: Optional[str] = None) -> Optional[QPixmap]:
        response = self.session.get(book_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        img = soup.select_one("div.BookCover__image img.ResponsiveImage")
        if not img or not (src := img.get("src")):
            return None

        image_response = self.session.get(src)
        image_response.raise_for_status()
        image_data = image_response.content

        # Create pixmap from image data
        pixmap = QPixmap()
        if not pixmap.loadFromData(image_data):
            return None

        # Cache the cover with the appropriate filename
        self._save_cover_to_cache(title, author, image_data, isbn)

        return pixmap

