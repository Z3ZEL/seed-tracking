from rpi_lcd import LCD
from resource_manager import CONFIG
import threading
import psutil, time

lcd_bus_address = CONFIG["lcd_screen_address"] if "lcd_screen_address" in CONFIG else False
lcd = False
if lcd_bus_address:
    #convert string "0x27" to hex 0x27
    address = int(lcd_bus_address, 16)
    lcd = LCD(address=address, rows=2, width=16)

lines = ["", ""]
def print_lcd(text:str, line:int=2):
    global lines
    lines[line-1] = text
    if lcd:
        lcd.text(lines[0], 1)
        lcd.text(lines[1], 2)
    else:
        print(text)
def lcd_thread():
    while True:
        string = "Temp : " + str(psutil.sensors_temperatures()["cpu_thermal"][0].current) + " C"
        #truncate to 16 characters
        string = string[:16]
        print_lcd(string , line=1)
        time.sleep(5)
if lcd:
    #create a thread to print something on the lcd screen every 5 seconds
    threading.Thread(target=lcd_thread).start()
