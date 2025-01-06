"""Module for book selection and scoring."""
from datetime import datetime
from utils.config import load_config
from utils.db import get_db

def calculate_rating_score(rating):
    """Calculate score component based on book rating."""
    config = load_config()
    try:
        rating = float(rating) if isinstance(rating, str) else rating
        difference_from_baseline = rating - config["rating"]["baseline"]
        return max(round(difference_from_baseline * config["rating"]["multiplier"], 2), 0)
    except (ValueError, TypeError):
        return 0

def calculate_length_score(length):
    """Calculate score component based on word count."""
    config = load_config()
    try:
        words = int(length) if isinstance(length, str) else length
        word_difference = abs(config["length"]["target"] - words)
        thousands_difference = -(word_difference + (config["length"]["penalty_step"] - 1)) // config["length"]["penalty_step"]
        return thousands_difference
    except (ValueError, TypeError):
        return 0

def calculate_book_score(book):
    """Calculate total score for a single book."""
    rating_score = calculate_rating_score(book["rating"])
    length_score = calculate_length_score(book["length"])
    total_score = round(rating_score + length_score, 2)
    return total_score

def calculate_scores(books):
    """Calculate and add scores for a list of books."""
    for book in books:
        book["score"] = calculate_book_score(book)
    return books

def get_selected_books():
    """Get list of selected books ordered by read date."""
    conn = get_db()
    try:
        cursor = conn.execute(
            """
            SELECT * FROM books 
            WHERE read_date IS NOT NULL AND read_date != ''
            ORDER BY read_date DESC
            """
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_member_penalties(books=None):
    """Calculate penalties for members based on their recent selections."""
    if books is None:
        books = get_selected_books()
    
    config = load_config()
    penalties = {}
    recent_selections = books[:3]  # Get 3 most recent selections
    
    for i, book in enumerate(recent_selections):
        member = book["member"]
        if i == 0:
            penalties[member] = config["member_penalties"]["last_selection"]
        elif i == 1:
            penalties[member] = config["member_penalties"]["second_last"]
        else:
            penalties[member] = config["member_penalties"]["third_last"]
    
    return penalties

def adjust_scores(books, selected_books=None):
    """Adjust book scores based on member selection history."""
    if selected_books is None:
        selected_books = get_selected_books()
        
    penalties = get_member_penalties(selected_books)
    
    adjusted_books = []
    for book in books:
        adjusted_book = dict(book)
        member = adjusted_book["member"]
        adjusted_book["score"] = float(adjusted_book["score"])
        
        if member in penalties:
            penalty = penalties[member]
            adjusted_book["score"] += penalty
            
        adjusted_books.append(adjusted_book)
        
    return adjusted_books

def select_top_choice(books):
    """Select the book with the highest score that hasn't been selected before."""
    if not books:
        return None
    
    # Get all books and filter out ones that have been selected
    selected_books = get_selected_books()
    selected_titles = {book['title'] for book in selected_books}
    available_books = [book for book in books if book['title'] not in selected_titles]
    
    if not available_books:
        return None
    
    adjusted_books = adjust_scores(available_books, selected_books)
    return max(adjusted_books, key=lambda book: book['score'])