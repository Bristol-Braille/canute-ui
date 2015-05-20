#!/usr/bin/env python
"""
for each character, create a png that represents the pins being up or down
"""
from PIL import Image, ImageDraw

pin_or = 7
offset = 2
pin_r = pin_or - offset
rows = 3
cols = 2
im_size = (2*cols*pin_or,2*rows*pin_or)
total = 2 ** (rows * cols)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (100, 100, 100)


def binary(x):
    """returns a list of 6 1s or 0s that represent a binary number"""
    return [int(i) for i in format(x,'#08b')[2:]]

def circle(draw,x,y,r,colour):
    """draws a circle"""
    coords=[x-r,y-r,x+r,y+r]
    draw.ellipse(coords,fill=colour)

if __name__ == '__main__':
    for num in range(total):
        #create an image
        im = Image.new("RGB", im_size, "white")
        #get the draw object
        draw = ImageDraw.Draw(im)
        b = binary(num)
        b.reverse()
        for pin in range(rows*cols):
            row = pin % rows
            col = pin / rows 
            print b, row, col
            
            circle(draw, pin_or + col*2*pin_or, pin_or + row*2*pin_or, pin_or, GREY)

            if b[pin]:
                circle(draw, offset + pin_r + col*2*(pin_r+offset), offset + pin_r + row*2*(pin_r+offset), pin_r, BLACK)
            else:
                circle(draw, offset + pin_r + col*2*(pin_r+offset), offset + pin_r + row*2*(pin_r+offset), pin_r, WHITE)

        #save the image
        im.save("%02d.png" % num, "PNG")

