from rpi_lcd import LCD
from resource_manager import CONFIG
import threading
import psutil

lcd_bus_address = CONFIG["lcd_screen_address"] if "lcd_screen_address" in CONFIG else False
lcd = False
if lcd_bus_address:
    #convert string "0x27" to hex 0x27
    address = int(lcd_bus_address, 16)
    lcd = LCD(address=address, rows=2, width=16)

def print_lcd(text:str, line=2):
    if lcd:
        lcd.text(text, line)
    else:
        print(text)
def lcd_thread():
    while True:
        print_lcd("Temp : " + str(psutil.sensors_temperatures()["cpu_thermal"][0].current) + " C", line=1)
        threading.Event().wait(5)
if lcd:
    #create a thread to print something on the lcd screen every 5 seconds
    threading.Thread(target=lcd_thread).start()
