def clean_isbn(isbn):
    return "".join(c for c in isbn.strip() if c.isdigit() or c.upper() == "X")


def is_valid_isbn_10(isbn):
    """
    Validate ISBN-10.
    Last digit can be 'X' which represents 10.
    """
    if len(isbn) != 10:
        return False

    # Check if first 9 characters are digits
    if not isbn[:9].isdigit():
        return False

    # Check if last character is digit or 'X'
    if not (isbn[9].isdigit() or isbn[9].upper() == "X"):
        return False

    total = sum(int(isbn[i]) * (10 - i) for i in range(9))
    # Handle last digit, 'X' equals 10
    total += 10 if isbn[9].upper() == "X" else int(isbn[9])
    return total % 11 == 0


def is_valid_isbn_13(isbn):
    """
    Validate ISBN-13.
    Must be 13 digits, no 'X' allowed.
    """
    if len(isbn) != 13 or not isbn.isdigit():
        return False

    total = sum(
        int(isbn[i]) if i % 2 == 0 else int(isbn[i]) * 3 for i in range(12)
    )
    check_digit = (10 - (total % 10)) % 10
    return check_digit == int(isbn[12])


def convert_isbn_10_to_13(isbn10):
    """Convert ISBN-10 to ISBN-13 format."""
    if not is_valid_isbn_10(isbn10):
        return None

    # Remove check digit from ISBN-10
    isbn = f"978{isbn10[:9]}"

    total = sum(
        int(isbn[i]) if i % 2 == 0 else int(isbn[i]) * 3 for i in range(12)
    )
    check_digit = (10 - (total % 10)) % 10
    return isbn + str(check_digit)


def validate_isbn(isbn):
    """
    Validate and standardize ISBN input.
    Returns None if invalid, or normalized ISBN-13 if valid.
    """
    if not isbn:
        return None

    # Clean the ISBN of any hyphens or spaces
    cleaned_isbn = clean_isbn(isbn)

    # Check for ISBN-10
    if len(cleaned_isbn) == 10:
        if is_valid_isbn_10(cleaned_isbn):
            return convert_isbn_10_to_13(cleaned_isbn)
        return None

    # Check for ISBN-13
    if len(cleaned_isbn) == 13:
        return cleaned_isbn if is_valid_isbn_13(cleaned_isbn) else None
    return None
