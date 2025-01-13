from utils.core.config import load_config


def calculate_rating_score(rating):
    config = load_config()
    try:
        rating = float(rating) if isinstance(rating, str) else rating
        difference_from_baseline = rating - config["rating"]["baseline"]
        return max(
            round(difference_from_baseline * config["rating"]["multiplier"], 2), 0
        )
    except (ValueError, TypeError):
        return 0


def calculate_length_score(length):
    config = load_config()
    try:
        words = int(length) if isinstance(length, str) else length
        word_difference = abs(config["length"]["target"] - words)
        return (
            -(word_difference + (config["length"]["penalty_step"] - 1))
            // config["length"]["penalty_step"]
        )
    except (ValueError, TypeError):
        return 0


def calculate_book_score(book):
    rating_score = calculate_rating_score(book["rating"])
    length_score = calculate_length_score(book["length"])
    return round(rating_score + length_score, 2)


def calculate_scores(books):
    for book in books:
        book["score"] = calculate_book_score(book)
    return books
