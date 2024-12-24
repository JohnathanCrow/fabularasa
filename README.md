# Fabula Rasa
![screenshot01](https://github.com/user-attachments/assets/fe63a8b7-426f-43c7-bb14-7154b7af2843)

A book club app that uses an algorithm to select the best candidate for the next read, based on rating, target length, and whether the member who selected has had recently selected books. Required fields are title or ISBN (more reliable), wordcount, and member. The rest will be pulled automatically if not entered manually.

## Installation
#### Windows
- Download the latest release and run

## Usage
#### Selection
- Add title/ISBN, author, wordcount, and member who suggested book
- Click 'Add Book' / press 'Enter' to add it to the database of available books
- Click 'Select Book' to run the algorithm and select the next book

#### Book List
- View available and previously selected books in tables
- Edit book information, remove entires, and add entries to the database directly
- Click 'Save Changes' to save edits

#### Configuration
- Rating Baseline sets the star rating that equals 0 points 
  lower and higher subtracts or adds points)
- Rating Multiplier is the factor to multiply by 
  (10 is 1 point per 0.1 rating / 3 stars = 30 points)
- Target Wordcount sets the ideal number of words that equals 0 points
  (lower and higher than target wordcount will subtracts points)
- Penalty Step is how many words outside target to apply a 1 point penalty
  (every x number of words outside of target subtracts 1 point)
- Penalty 1, 2, and 3 subtracts points based on who selected recent books
  (1 being the most recent, 2 the second most, 3 the third most)
- Click 'Save Changes' to save edits
