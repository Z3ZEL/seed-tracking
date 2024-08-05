import gpiod
import time
from threading import Thread

chip = gpiod.Chip('gpiochip4')
led_line = chip.get_line(18)
led_line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)

buzzer_line = chip.get_line(15)
buzzer_line.request(consumer="buzzer_control", type=gpiod.LINE_REQ_DIR_OUT)


# buzzer = GPIO.PWM(15, 440)
def turn_light(state: bool):
       led_line.set_value(1 if state else 0)
def _buzz(duration:int):
    frequency = 440
    period = 1.0 / frequency
    end_time = time.time() + duration
    
    while time.time() < end_time:
        buzzer_line.set_value(1)  # Turn buzzer on
        time.sleep(period / 2)
        buzzer_line.set_value(0)  # Turn buzzer off
        time.sleep(period / 2)

def buzz(duration:int):
    t = Thread(target=_buzz, args=(duration,))
    t.start()