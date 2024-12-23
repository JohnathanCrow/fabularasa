# Fabula Rasa
![screenshot01](https://github.com/user-attachments/assets/7c701536-c48f-4433-a120-1505202a1641)

A book club app that uses an algorithm to select the best candidate for the next read, based on rating, target length, and whether the member who selected has had recently selected books. Required fields are title or ISBN (more reliable) and wordcount, the rest will be pulled automatically if not entered manually.

## Installation
#### Windows
- Download the latest release and run

## Usage
#### Selection
- Add book titles/ISBN13, author, wordcount, and member who suggested
- Click 'Add Book' / press 'Enter' to add it to the database of available books
- Click 'Select Book' to run the selector

#### Book List
- View available and previously selected books in a table view
- Edit book information, remove books, add books to the database directly
- Click 'Save Changes' to save edits

#### Configuration
- Adjust the algorithm settings
- Rating baseline sets the star rating that equals 0 points (lower and higher subtracts or adds points)
- Rating multiplier is the factor to multiply by (e.g., 10 is 1 point per 0.1 rating / 3 stars = 30 points)
- Target wordcount sets the ideal number of words that equals 0 points (lower and higher subtracts points)
- Penalty step is how many words to apply a 1 point pentalty (every X number of words outside of target subtracts 1 point)
- Penalty 1, 2, and 3 subtracts points based on which member selected recent books (1 being the most recent)