#fonctionnel
#https://docs.circuitpython.org/projects/neopixel/en/latest/
import board
import neopixel
import time
import random

# Create a NeoPixel object on pin D21 with 12 pixels
pixels = neopixel.NeoPixel(board.D21, 12, auto_write=False)
while True:
    for i in range(len(pixels)):
        pixels[i] = (random.randint(0, 9), random.randint(0, 9), random.randint(0, 9))  # Set random color for each pixel
        pixels.show()  # Update the pixels to show the new color
        time.sleep(0.1)  # Wait before changing colors again