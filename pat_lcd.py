import time
from os import path
import shutil
import importlib.util


def init_dependencies(submodule_path):
    dependencies = ['lcddriver.py', 'i2c_lib.py']
    for module in dependencies:
        if not path.exists(module) and path.exists('{}/{}'.format(submodule_path, module)):
            shutil.copyfile('{}/{}'.format(submodule_path, module), './')


init_dependencies('./lcd')
lcddriver = __import__('lcddriver.py')
display = lcddriver.lcd()

while True:
    print("Writing to LCD")
    display.lcd_display_string("Hello, this is", 1)
    display.lcd_display_string("a test", 2)
    time.sleep(2)
    display.lcd_clear()
    time.sleep(2)