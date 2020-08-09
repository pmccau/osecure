import lcddriver
import time

display = lcddriver.lcd()

while True:
    print("Writing to LCD")
    display.lcd_display_string("Hello, this is", 1)
    display.lcd_display_string("a test", 2)
    time.sleep(2)
    display.lcd_clear()
    time.sleep(2)