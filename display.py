import RPi.GPIO as GPIO
from RPLCD.gpio import CharLCD
import sys

lcd_screen = CharLCD( 

    #Cambiar con pines correctos
    numbering_mode=GPIO.BCM,
    cols=16, rows=2, pin_rs=26, pin_e=19,
    pins_data=[13, 6, 5, 11]

)

def display_message(going_to_rain, going_to_snow, temperature):

   
    
    lcd_screen.clear()

    if going_to_rain:
        lcd_screen.write_string("Ta med paraply!")
    elif going_to_snow: 
        lcd_screen.write_string("Sätt på jackan!")

    lcd_screen.cursor_pos = (1, 0)
    
    if temperature is not None:
        lcd_screen.write_string(f"Det är {temperature}°C")
    else:
        lcd_screen.write_string("Temp saknas")

if __name__ == "__main__":

    going_to_rain = sys.argv[1].lower() == "true" # Detta är för att göra om det till en boolean efter att ha fått det som en string
    going_to_snow = sys.argv[2].lower() == "true"
    temperature = sys.argv[3]

    display_message(going_to_rain, going_to_snow, temperature)


#meddelande för LCD skärm "Ta med paraply!" "Det är 10°C"
                                   #16 char            #11 char     

#meddelande för LCD skärm "Ta på dig jacka!" "Det är 2°C"
                                    #16 char            #10-11 char