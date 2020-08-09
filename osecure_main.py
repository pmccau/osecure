import RPi.GPIO as GPIO
import Keypad
import time
ROWS = 4
COLS = 3
keys = [ '1', '2', '3',
         '4', '5', '6',
         '7', '8', '9',
         '*', '0', '#' ]
rowsPins = [12, 16, 18, 22]
colsPins = [19, 15, 13, 11]
toggleSwitchPin = 32

WHITE_LED = 21
RED_LED = 31
BLUE_LED = 29
led_lights = [WHITE_LED, RED_LED, BLUE_LED]

def loop():
    # Init from LED
    GPIO.setmode(GPIO.BOARD)
    # GPIO.setwarnings(False)
    
    # Init LED lights
    GPIO.setup(WHITE_LED, GPIO.OUT)
    GPIO.setup(RED_LED, GPIO.OUT)
    GPIO.setup(BLUE_LED, GPIO.OUT)
    
    GPIO.setup(toggleSwitchPin, GPIO.IN)
    #GPIO.output(21, GPIO.HIGH)
    #print("LED on!")
    #time.sleep(10)
    keypad = Keypad.Keypad(keys, rowsPins, colsPins, ROWS, COLS) # create Keypad obj
    keypad.setDebounceTime(50)
    while(True):
        
        
#         if GPIO.input(toggleSwitchPin):
#             print("Toggled!")
#         else:
#             print("Not toggled!")
        
        
        
        key = keypad.getKey()
        if key != keypad.NULL:
            GPIO.output(WHITE_LED, GPIO.HIGH)
            print("Pressed a key: {}".format(key))
            if key == '#' or key == '*':
                GPIO.output(RED_LED, GPIO.HIGH)
            else:
                GPIO.output(BLUE_LED, GPIO.HIGH)
                
            time.sleep(.05)
            clear_all_leds()
            

def clear_all_leds():
    for led in led_lights:
        GPIO.output(led, GPIO.LOW)
            
            
if __name__ == '__main__':
    print("Starting...")
    try:
        loop()
    except KeyboardInterrupt:
        GPIO.cleanup()