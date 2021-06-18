import board
import neopixel
import time

pixels = neopixel.NeoPixel(board.D12, 24)
for p in range(0, 23):
    pixels[p] = (120, 120, 0)