import board
import neopixel
import time

while True:
    print('Setting lights')
    pixels = neopixel.NeoPixel(board.D12, 24)
    for p in range(0, 23):
        pixels[p] = (0, 0, 0)
    for p in range(0, 23, 2):
        pixels[p] = (255, 255, 255)
    time.sleep(30)
