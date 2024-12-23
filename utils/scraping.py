"""Module for interacting with Goodreads."""
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
from PyQt6.QtGui import QPixmap

class GoodreadsClient:
    """Client for interacting with Goodreads website."""
    
    BASE_URL = "https://www.goodreads.com"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def _is_isbn(self, query: str) -> bool:
        """Check if query is an ISBN number."""
        return query.isdigit() and len(query) == 13

    def _get_book_page_url(self, query: str) -> Optional[str]:
        """Get the book's detail page URL from search results or ISBN."""
        if self._is_isbn(query):
            return f"{self.BASE_URL}/book/isbn/{query}"
            
        search_url = f"{self.BASE_URL}/search?q={query.replace(' ', '+')}"
        
        try:
            response = self.session.get(search_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            book_link = soup.select_one("a.bookTitle")
            if not book_link or not (book_url := book_link.get("href")):
                return None
                
            return f"{self.BASE_URL}{book_url}"
        except Exception as e:
            print(f"Error getting book page URL: {e}")
            return None

    def get_book_info(self, query: str) -> Optional[Dict[str, Any]]:
        """Get book information by title or ISBN."""
        book_url = self._get_book_page_url(query)
        if not book_url:
            return None
            
        try:
            response = self.session.get(book_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            title = soup.select_one("h1[data-testid='bookTitle']")
            author = soup.select_one("span.ContributorLink__name")
            rating = soup.select_one("div.RatingStatistics__rating")
            
            if not title:
                return None
                
            return {
                "title": title.text.strip(),
                "author": author.text.strip() if author else "Unknown Author",
                "rating": float(rating.text.strip()) if rating else 0.0
            }
        except Exception as e:
            print(f"Error fetching book info: {e}")
            return None

    def get_cover(self, title: str) -> Optional[QPixmap]:
        """Get book cover image as QPixmap."""
        book_url = self._get_book_page_url(title)
        if not book_url:
            return None
            
        try:
            response = self.session.get(book_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            img = soup.select_one("div.BookCover__image img.ResponsiveImage")
            if not img or not (src := img.get("src")):
                return None
                
            image_response = self.session.get(src)
            image_response.raise_for_status()
            
            pixmap = QPixmap()
            if not pixmap.loadFromData(image_response.content):
                return None
                
            return pixmap
        except Exception as e:
            print(f"Error fetching cover: {e}")
            return None