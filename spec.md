# UI Spec

Engineering requirements derived from business level [specification](http://bootsa.bristolbraille.co.uk/projects/canute/wiki/UI_Development)

# outstanding questions

* are chordal button presses necessary?

# file formats

The software shall include a function to translate the following formats into the proprietary Canute binary file:

* BRF
* PEF

# book management

The library system shall be able to:

* Select books from the on-board store and USB flash drive
* Copy books from a USB flash drive into library
* Deleting books from an on-board store

[copying and selecting books](library_spec.md)

# profiles

The software should be able to read user profiles held on a USB flash drive, overriding local settings.

# buttons

* each button can click and long click.
* Multiple button presses at once can be handled?
* allow easy configuration of mapping buttons to functions
* a button press can interrupt a page being loaded, for example to skip 2 pages
* user receives tactile feedback that a button press has been received

## necessary functions

* library mode
* menu mode
* prev page
* next page
* make menu selection
* select a book
* shutdown
* home
* end
* next chapter
* prev chapter

# menus

* menu exited by choosing a button (on the right hand side)
* menu exited with the menu button

# modes

## read mode

* used to navigate book
* Should include a function to identify the current book and current position in a book
* Shall include a text based search function (via external USB keyboard)
* Shall include a function to navigate by page number (to match physical book?), index, special markers (bookmarks, chapters, etc)
* allow partial page update for continuous reading

## library mode (sub class of menu)

* used to select a book
* Shall include a function for multiple user specific libraries
* selected using the library mode button
* when a book is selected, show last viewed position

# power up

* notify user the machine is ready
* show last position in either library or book (not menu)

# power down

* shutdown from menu
* user knows that the machine is off
