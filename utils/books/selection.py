from utils.core.config import load_config
from utils.core.db import get_db

from .scoring import calculate_book_score, calculate_scores


def get_selected_books():
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM books 
            WHERE read_date IS NOT NULL AND read_date != ''
            ORDER BY read_date DESC
            """
        )
        return [dict(row) for row in cursor.fetchall()]


def get_member_penalties(books=None):
    if books is None:
        books = get_selected_books()

    config = load_config()
    penalties = {}
    recent_selections = books[:3]

    for i, book in enumerate(recent_selections):
        member = book["member"]
        if i == 0:
            penalties[member] = config["member_penalties"]["last_selection"]
        elif i == 1:
            penalties[member] = config["member_penalties"]["second_last"]
        else:
            penalties[member] = config["member_penalties"]["third_last"]

    return penalties


def get_tag_adjustments(books=None):
    if books is None:
        books = get_selected_books()

    config = load_config()
    adjustments = {}
    recent_selections = books[:3]

    for i, book in enumerate(recent_selections):
        if not book.get("tags"):
            continue
            
        tags = [tag.strip() for tag in book["tags"].split(",")]
        adjustment = (
            config["tag_adjustments"]["last_selection"] if i == 0
            else config["tag_adjustments"]["second_last"] if i == 1 else config["tag_adjustments"]["third_last"]
        )
        
        for tag in tags:
            if tag in adjustments:
                adjustments[tag] = max(adjustments[tag], adjustment)
            else:
                adjustments[tag] = adjustment

    return adjustments


def adjust_scores(books, selected_books=None):
    if selected_books is None:
        selected_books = get_selected_books()

    penalties = get_member_penalties(selected_books)
    tag_adjustments = get_tag_adjustments(selected_books)

    adjusted_books = []
    for book in books:
        adjusted_book = dict(book)
        member = adjusted_book["member"]
        adjusted_book["score"] = float(adjusted_book["score"])

        # Apply member penalties
        if member in penalties:
            penalty = penalties[member]
            adjusted_book["score"] += penalty

        # Apply tag adjustments
        if book.get("tags"):
            book_tags = [tag.strip() for tag in book["tags"].split(",")]
            for tag in book_tags:
                if tag in tag_adjustments:
                    adjusted_book["score"] += tag_adjustments[tag]

        adjusted_books.append(adjusted_book)

    return adjusted_books


def select_top_choice(books):
    if not books:
        return None

    # Get already selected books and create a set of their titles
    selected_books = get_selected_books()
    selected_titles = {book["title"].lower().strip() for book in selected_books}

    # Filter out any books that have already been selected
    available_books = [
        book
        for book in books
        if book["title"].lower().strip() not in selected_titles
        and not book.get("read_date")
    ]

    if not available_books:
        return None

    # Calculate adjusted scores for remaining books
    adjusted_books = adjust_scores(available_books, selected_books)
    return max(adjusted_books, key=lambda book: book["score"])