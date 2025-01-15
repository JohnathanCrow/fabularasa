def estimate_word_count(page_count: int) -> int:
    """
    Estimates word count based on page count using standard 275 words per page.
    Rounds to nearest 1000 words.
    """
    if not page_count:
        return 0
        
    word_count = page_count * 275
    return round(word_count / 1000) * 1000

def clean_page_count(page_text: str) -> int:
    """
    Extracts page count from scraped text.
    Example input: "568 pages, Kindle Edition"
    Returns: 568
    """
    if not page_text:
        return 0
        
    try:
        # Extract first number from string
        number = ''.join(c for c in page_text.split()[0] if c.isdigit())
        return int(number) if number else 0
    except (ValueError, IndexError):
        return 0