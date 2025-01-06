# Fabula Rasa
![screenshot_home](https://github.com/user-attachments/assets/a09de5f6-1544-4ec4-b41d-0cf6a9462697)

A book club app that uses a simple algorithm to select the best candidate for the next read, based on rating, target length, and who suggested recently selected books. 

## Installation
#### Windows
- [Download](https://github.com/JohnathanCrow/fabularasa/releases) the exe of the latest release and run

## Usage
#### Home
- Add book title/ISBN, author, word count, and member
- Click 'Add' or press 'Enter' to add it to the available books
- Select a planned read date in the calendar
- Click 'Select' to run the selector

#### Database
- View available and previously selected books in a table view
- Edit, add, or remove books to the table manually
- Click 'Save Changes' to save edits

#### Config
- Adjust the algorithm settings

- Rating Baseline sets the star rating that equals 0 penalty
  (lower and higher ratings subtract or add points)
- Rating Multiplier is the factor to multiply by
  (10 is 1 point per 0.1 rating / 3 stars = 30 points)
- Target Wordcount sets the number of words that equals 0 points
  (lower and higher than target wordcount will subtracts points)
- Penalty Step is how many words outside target to apply a 1 point penalty
  (every x number of words outside of target subtracts 1 point)
- Penalty 1, 2, and 3 subtracts points based on who selected recent books
  (1 being the most recent, 2 the second most, 3 the third most)
  
 #### Tips
- Required fields are title/ISBN and word count
- Use [this](https://www.howlongtoread.org) for book word counts
- Author will be pulled automatically and member will be skipped if not entered
- Use solo by omitting member field, and setting member penalties to 0
- Read date will default to next Monday if not changed
