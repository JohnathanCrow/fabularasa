import sqlite3
from datetime import datetime
from flask import Flask, render_template, jsonify, send_file, Response
from pathlib import Path
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_db_path():
    # For Render deployment, use the DATABASE_URL environment variable
    if database_url := os.getenv('DATABASE_URL'):
        return database_url
    
    # Local development fallback
    if os.name == 'nt':  # Windows
        return Path(os.getenv('APPDATA')) / 'FabulaRasa' / 'profiles' / 'default' / 'books.db'
    elif os.name == 'darwin':  # macOS
        return Path.home() / 'Library' / 'Application Support' / 'FabulaRasa' / 'profiles' / 'default' / 'books.db'
    else:  # Linux/Unix
        return Path.home() / '.FabulaRasa' / 'profiles' / 'default' / 'books.db'

def init_db():
    """Initialize the database with required schema"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create books table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT,
            tags TEXT,
            length INTEGER NOT NULL,
            rating REAL NOT NULL DEFAULT 0,
            member TEXT NOT NULL,
            score REAL NOT NULL DEFAULT 0,
            date_added TEXT NOT NULL,
            read_date TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def get_goodreads_cover(title, author, isbn=None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # Try ISBN first if available
    if isbn:
        url = f"https://www.goodreads.com/book/isbn/{isbn}"
        response = requests.get(url, headers=headers)
        if response.ok:
            soup = BeautifulSoup(response.text, "html.parser")
            img = soup.select_one("div.BookCover__image img.ResponsiveImage")
            if img and (src := img.get("src")):
                return requests.get(src, headers=headers).content

    # Fall back to search by title and author
    search_query = f"{title} {author}".replace(" ", "+")
    search_url = f"https://www.goodreads.com/search?q={search_query}"
    
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        book_link = soup.select_one("a.bookTitle")
        if book_link and (book_url := book_link.get("href")):
            book_url = f"https://www.goodreads.com{book_url}"
            
            response = requests.get(book_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            img = soup.select_one("div.BookCover__image img.ResponsiveImage")
            if img and (src := img.get("src")):
                cover_response = requests.get(src, headers=headers)
                cover_response.raise_for_status()
                return cover_response.content
    except Exception as e:
        print(f"Error fetching cover: {e}")
    
    return None

@app.route('/')
def home():
    return render_template('web.html')

@app.route('/events')
def events():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, author, isbn, length, member, read_date, tags
        FROM books 
        WHERE read_date IS NOT NULL AND read_date != ''
        ORDER BY read_date DESC
    """)
    
    events_list = []
    for row in cursor.fetchall():
        events_list.append({
            'title': row[0],
            'author': row[1],
            'isbn': row[2],
            'length': row[3],
            'member': row[4],
            'start': row[5],
            'tags': row[6]
        })
    conn.close()
    return jsonify(events_list)

@app.route('/cover/<isbn>')
def get_cover(isbn):
    # Get book details from database
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, author 
        FROM books 
        WHERE isbn = ?
    """, (isbn,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return '', 404
        
    title, author = result
    
    # Try to get cover from Goodreads
    if cover_data := get_goodreads_cover(title, author, isbn):
        return Response(cover_data, mimetype='image/jpeg')
    
    return '', 404

@app.route('/static/no_cover.png')
def get_placeholder():
    static_dir = Path(__file__).parent / 'static'
    return send_file(static_dir / 'no_cover.png', mimetype='image/png')

# Initialize the database when the app starts
init_db()

if __name__ == '__main__':
    # Ensure the static directory exists
    static_dir = Path(__file__).parent / 'static'
    static_dir.mkdir(exist_ok=True)
    
    # Copy the no_cover.png from assets if it doesn't exist
    placeholder = static_dir / 'no_cover.png'
    if not placeholder.exists():
        assets_dir = Path(__file__).parent.parent / 'assets'
        if (assets_dir / 'no_cover.png').exists():
            from shutil import copy2
            copy2(assets_dir / 'no_cover.png', placeholder)
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)