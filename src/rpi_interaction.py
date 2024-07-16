import RPi.GPIO as GPIO
import time
from threading import Thread

GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.OUT)
GPIO.setup(15,GPIO.OUT)
buzzer = GPIO.PWM(15, 440)
def turn_light(state: bool):
    GPIO.output(18,GPIO.HIGH if state else GPIO.LOW)
def _buzz(duration:int):
    
    buzzer.start(50)
    time.sleep(duration)
    buzzer.stop()
def buzz(duration:int):
    t = Thread(target=_buzz, args=(duration,))
    t.start()