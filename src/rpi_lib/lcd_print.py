from rpi_lcd import LCD
from resource_manager import CONFIG

lcd_bus_address = CONFIG["lcd_screen_address"] if "lcd_screen_address" in CONFIG else False
lcd = False
if lcd_bus_address:
    #convert string "0x27" to hex 0x27
    address = int(lcd_bus_address, 16)
    lcd = LCD(address=address, rows=2, width=16)

def print_lcd(text:str):
    if lcd:
        lcd.text("Seed Eater V2.1", 1)
        lcd.text(text, 2)
    else:
        print(text)