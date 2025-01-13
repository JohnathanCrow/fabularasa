from typing import Any, Dict, Optional

import requests
from bs4 import BeautifulSoup
from PyQt6.QtGui import QPixmap


class GoodreadsClient:

    BASE_URL = "https://www.goodreads.com"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

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

        if not title:
            return None

        return {
            "title": title.text.strip(),
            "author": author.text.strip() if author else "Unknown Author",
            "rating": float(rating.text.strip()) if rating else 0.0,
            "isbn": isbn or None,
        }

    def get_cover(self, title: str, isbn: Optional[str] = None) -> Optional[QPixmap]:
        book_url = self._get_book_page_url(title, isbn)
        if not book_url:
            return None

        try:
            return self.extract_cover(book_url)
        except Exception as e:
            print(f"Error fetching cover: {e}")
            return None

    def extract_cover(self, book_url):
        response = self.session.get(book_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        img = soup.select_one("div.BookCover__image img.ResponsiveImage")
        if not img or not (src := img.get("src")):
            return None

        image_response = self.session.get(src)
        image_response.raise_for_status()

        pixmap = QPixmap()
        return pixmap if pixmap.loadFromData(image_response.content) else None
