from resource_manager import CONFIG

HARDWARE = CONFIG["hardware"]

if HARDWARE == "rpi5":
    from rpi_lib.rpi5 import turn_light, buzz
elif HARDWARE == "rpi3":
    from rpi_lib.rpi3 import turn_light, buzz
else:
    from rpi_lib.rpi_interaction_mock import turn_light, buzz



def turn_light(state: bool):
    '''
    Turn the light on or off

    Parameters:
    state (bool): The state of the light
    '''
    turn_light(state)
   

def buzz(duration:int):
    '''
    Buzz the buzzer for a certain duration

    Parameters:
    duration (int): The duration of the buzz in seconds
    '''
    buzz(duration)