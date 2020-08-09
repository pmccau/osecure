import RPi.GPIO as GPIO
import Keypad
import datetime, time
import lcddriver

class osecure_actions:
    """ Class to define all valid actions, states
    """

    # Actions
    ARM = "ARM"
    DISARM = "DISARM"
    GO = "GO"
    ALERT = "ALERT"

""" Operation:
 - Enter your code to arm or disarm
 1. Code received
 2. Is correct? If not, blink 3 times, display 'invalid code', go back to start
 3. Correct code entered:
    a. Is armed currently:
        i. Toggle switch is in up position (on): Begin blinking, display 'Switch off to disarm'
        ii. Toggle switch is in down position (off): Begin blinking, display 'Switch up, then down to disarm'
    b. Is disarmed currently
        i. Toggle switch is on: Begin blinking, display 'Switch down, then up to arm'
        ii. Toggle switch is off: Begin blinking, display 'Switch up to arm'
 4. Just armed: turn on red light, turn off blue light
 5. Just disarmed: turn on blue light, turn off red light
 6. Time limit reached, go back to start
"""

class osecure_system:

    def __init__( self):

        # General config
        GPIO.setmode(GPIO.BOARD)

        # Keypad configuration
        self.ROWS = 4
        self.COLS = 3
        self.KEYS = ['1', '2', '3',
                '4', '5', '6',
                '7', '8', '9',
                '*', '0', '#']
        self.ROWS_PINS = [12, 16, 18, 22]
        self.COLS_PINS = [19, 15, 13, 11]
        self.keypad = Keypad.Keypad(self.KEYS, self.ROWS_PINS, self.COLS_PINS, self.ROWS, self.COLS)
        self.keypad.setDebounceTime(50)
        self.last_key_pressed_time = -1
        self.key_code_entered = ''
        self.key_press_time_threshold = datetime.timedelta(seconds=5)

        # Toggle switch configuration
        self.TOGGLE_SWITCH_INPUT = 32
        self.TOGGLE_SWITCH_OUTPUT = 36
        GPIO.setup(self.TOGGLE_SWITCH_INPUT, GPIO.IN)
        GPIO.setup(self.TOGGLE_SWITCH_OUTPUT, GPIO.OUT)
        GPIO.output(self.TOGGLE_SWITCH_OUTPUT, GPIO.HIGH)

        # LCD screen configuration
        self.display = lcddriver.lcd()

        # Light-GPIO configuration
        self.WHITE_LED = 21
        self.RED_LED = 31
        self.BLUE_LED = 29
        self.led_lights = [self.WHITE_LED, self.RED_LED, self.BLUE_LED]
        for led in self.led_lights:
            GPIO.setup(led, GPIO.OUT)

        # State change-related stuff
        self.last_state_change = -1
        self.state_change_validity_timestamp = -1
        self.STATE_CHANGE_WINDOW_TOLERANCE = datetime.timedelta(seconds=30)
        self.is_armed = False


    def update_state(self, action):
        """ Update the state of the system
        :param action:
        :return:
        """
        if action == osecure_actions.ARM:
            if osecure_actions.state_change_in_progress:
                pass
        elif action == osecure_actions.DISARM:
            pass
        elif action == osecure_actions.GO:
            pass


    def is_within_action_window(self):
        """ Makes sure that the change is happening within the allowed window (ex. 30 sec)
        """
        return self.STATE_CHANGE_WINDOW_TOLERANCE > (datetime.datetime.now() - self.state_change_validity_timestamp)


    def start_action_window(self):
        """ This should begin a countdown during which time a valid GO signal
        will change the state. If no signal received, it should expire and switch to
        invalid
        :return:
        """
        self.state_change_validity_timestamp = datetime.datetime.now()


    def arm_system(self):
        """ This should arm the system, then pass off to update_outputs
        """
        self.is_armed = True
        GPIO.output(self.BLUE_LED, GPIO.HIGH)
        GPIO.output(self.RED_LED, GPIO.LOW)
        self.display.lcd_clear()
        self.display.lcd_display_string("SYSTEM STATUS", 1)
        self.display.lcd_display_string("ARMED", 2)


    def disarm_system(self):
        self.is_armed = False
        GPIO.output(self.RED_LED, GPIO.HIGH)
        GPIO.output(self.BLUE_LED, GPIO.LOW)
        self.display.lcd_display_string("SYSTEM STATUS", 1)
        self.display.lcd_display_string("DISARMED", 2)


    def get_toggle_switch_state(self):
        return GPIO.input(self.TOGGLE_SWITCH)


    def validate_key_code(self, code):
        pass


    def present_state_change(self):
        self.display.lcd_clear()
        if self.is_armed:
            if self.get_toggle_switch_state():
                self.display.lcd_display_string("TOGGLE SWITCH", 1)
                self.display.lcd_display_string("TO DISARM", 2)
            # else:
            #     self.display.lcd_display_string("SWITCH OUT OF", 1)
            #     self.display.lcd_display_string("POSITION", 2)
            #     self.present_state_change()
        else:
            if not self.get_toggle_switch_state():
                self.display.lcd_display_string("TOGGLE SWITCH", 1)
                self.display.lcd_display_string("TO ARM", 2)
            # else:
            #     self.display.lcd_display_string("SWITCH OUT OF", 1)
            #     self.display.lcd_display_string("POSITION", 2)
            #     self.present_state_change()


    def blink_state_change_lights(self, sleep_interval):
        """ Blink the red and blue lights, then sleep for some seconds
        """
        indicators = [self.BLUE_LED, self.RED_LED]
        for i in range(len(indicators)):
            GPIO.output(indicators[i], GPIO.HIGH)
            GPIO.output(indicators[(i + 1) % len(indicators)], GPIO.LOW)
            time.sleep(sleep_interval)


    def invalid_entry(self):
        """ Present output for invalid entry, then go back to current state
        """
        self.key_code_entered = ''
        self.display.lcd_clear()
        self.display.lcd_display_string("INVALID CODE", 1)
        time.sleep(2)
        if self.is_armed:
            self.arm_system()
        else:
            self.disarm_system()


    def listen_for_actions(self):
        """ Busy wait listener for keyboard activity
        """
        while True:
            key_pressed = self.keypad.getKey()

            # If key press detected
            if key_pressed != self.keypad.NULL:

                # Indicate input received
                GPIO.output(self.WHITE_LED, GPIO.HIGH)
                key_press_time = datetime.datetime.now()

                # If this is the first time a key has been pressed, or it's within the window
                # since last time a key was pressed, add it to the current code. Otherwise, make
                # the current code just this key
                if self.key_press_time_threshold <= (key_press_time - self.last_key_pressed_time) or \
                        self.last_key_pressed_time == -1:
                    self.key_code_entered += key_pressed
                else:
                    self.key_code_entered = key_pressed
                self.last_key_pressed_time = key_press_time

                # If #, validate the code against expected
                if key_pressed == '#':
                    if self.validate_key_code(self.key_code_entered[:-1]):
                        # Start action window, deliver output
                        self.start_action_window()
                        self.present_state_change()
                    else:
                        self.invalid_entry()

                time.sleep(.02)
                self.clear_all_leds()


    def clear_all_leds(self):
        """ Kill all the lights that are currently on
        """
        for led in self.led_lights:
            GPIO.output(led, GPIO.LOW)
            
            
if __name__ == '__main__':
    print("Starting...")
    try:
        osecure_system.listen_for_actions()
    except KeyboardInterrupt:
        GPIO.cleanup()