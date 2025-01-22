# Fabula Rasa
![screenshot_home](https://github.com/JohnathanCrow/fabularasa/blob/main/screenshot.png)

A book club app that uses a simple algorithm to select the best candidate for the next read, based on rating, target length, and who suggested recently selected books. Or just use it solo.

## Installation

#### Windows

- [Download](https://github.com/JohnathanCrow/fabularasa/releases) the latest release and run
- Data is stored in '%appdata%/Roaming/FabulaRasa'


## Usage

#### Header

- Manage profiles with the user icon in the top left
	- Each profile has a separate calendar, database, and config
- Manage data export and import with the disc icon in the in the top left
	- Export as CSV or MD
	- Backup and restore profiles
- Manage misc options with the gear icon in the top left
	- Input regional store addresses for Amazon and Kobo
	- Clear the book cover image cache
		
#### Home

- Add books
	- Add book title/ISBN, author, tags, word count, and member
		- Title/ISBN is the only required field
		- ISBN is preferable to get the correct edition/cover
	- Info will be pulled automatically and member will be skipped if not entered
	- Word count can't be scraped, but will make an estimate based on page count
	- Use [this](https://www.howlongtoread.org) for book word counts
	- Tags must be seperated with a comma (e.g. 'Fiction, Literary')
	- Click 'Add' or press 'Enter' to add it to the available books
	- All fields can be added/edited later
- Select books
	- Select a planned read date in the calendar
		- Planned read date will default to next Monday if not changed
		- Dates with planned read dates will be coloured blue
	- Click 'Select' to run the selector
- Navigate through selected books with the icons in the top right of the selected book panel
	- In order: earliest, previous, current, next, latest

#### Database

- Manage available and previously selected books in a table view
	- Edit, add, or remove books to the available books table manually
	- Edit books in the selected books table manually
- Tags
	- Tags can be added, edited, or deleted by double clicking the tag field
	- Click 'Save' to save tag changes
- Click 'Save' to save book changes

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
	- Tag 1, 2, and 3 subtracts or adds points based on genre of recently selected books
      (1 being the most recent, 2 the second most, 3 the third most)
- Click 'Save' to save config changes

#### Notes

- Cover scraping will take a moment when adding a book, but selected book navigation will be faster once cached
