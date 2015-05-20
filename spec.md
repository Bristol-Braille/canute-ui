# UI Spec

This doc is an abbreviated software spec for the UI

## Todo

* chapters

## bugs


# buttons

each button can click, double click and long click

## left side

* library_mode
* prev_page / menu up
* next_page / menu down
* menu

## right hand

select menu choices

# menus

description is n-1 cells in width
nth cell shows a standard pin matrix - (all 6 pins raised)

n is height in lines

* prev_page click: menu moves n positions higher
* next_page click: moves n positions lower 
* prev_page long click: first position
* next_page long click: last position, still showing 4

menu exited by choosing a button (on the right hand side)
menu exited with the menu button

# modes

## read mode

used to navigate book

buttons work as follows:

prev_page click: move up by one page
next_page click: move down by one page
prev_page long click: beginning
next_page long click: end
prev_page double click: beginning of previous chapter
next_page double click: beginning of next chapter

## library mode (sub class of menu)

used to select a book

selected using the library mode button

when a book is selected, show last viewable position

# power up

show last position in either library or book
