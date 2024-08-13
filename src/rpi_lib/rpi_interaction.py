from resource_manager import CONFIG

HARDWARE = CONFIG["hardware"]

if HARDWARE == "rpi5":
    from rpi_lib.rpi5 import turn_light as tl, buzz as b
    from rpi_lib.lcd_print import print_lcd as pl
elif HARDWARE == "rpi3":
    from rpi_lib.rpi3 import turn_light as tl, buzz as b
    from rpi_lib.lcd_print import print_lcd as pl
else:
    from rpi_lib.rpi_interaction_mock import turn_light as tl, buzz as b, print_lcd as pl



def turn_light(state: bool):
    '''
    Turn the light on or off

    Parameters:
    state (bool): The state of the light
    '''
    tl(state)
   

def buzz(duration:int):
    '''
    Buzz the buzzer for a certain duration

    Parameters:
    duration (int): The duration of the buzz in seconds
    '''
    b(duration)

def print_lcd(text:str):
    '''
    Print a text on the lcd

    Parameters:
    text (str): The text to print
    '''
    pl(text)