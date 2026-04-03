import lgpio as GPIO
import time

# Define GPIO pins for LCD
LCD_RS = 26
LCD_E = 19
LCD_D4 = 13
LCD_D5 = 6
LCD_D6 = 5
LCD_D7 = 11

# LCD constants
LCD_WIDTH = 16
LCD_CMD = 0  # Mode - Sending command
LCD_CHR = 1  # Mode - Sending data
LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# Open GPIO chip (use 0 for default Raspberry Pi GPIO)
h = GPIO.gpiochip_open(0)

# Configure pins as output
for pin in [LCD_RS, LCD_E, LCD_D4, LCD_D5, LCD_D6, LCD_D7]:
    GPIO.gpio_claim_output(h, pin)

def lcd_init():
    """Initialize the LCD."""
    lcd_byte(0x33, LCD_CMD)  # Initialize
    lcd_byte(0x32, LCD_CMD)  # Initialize
    lcd_byte(0x28, LCD_CMD)  # 2 line, 5x7 matrix
    lcd_byte(0x0C, LCD_CMD)  # Display on, cursor off
    lcd_byte(0x06, LCD_CMD)  # Shift cursor right
    lcd_byte(0x01, LCD_CMD)  # Clear display
    time.sleep(E_DELAY)

def lcd_byte(bits, mode):
    """Send byte to data pins."""
    GPIO.gpio_write(h, LCD_RS, mode)

    # High bits
    GPIO.gpio_write(h, LCD_D4, 1 if bits & 0x10 else 0)
    GPIO.gpio_write(h, LCD_D5, 1 if bits & 0x20 else 0)
    GPIO.gpio_write(h, LCD_D6, 1 if bits & 0x40 else 0)
    GPIO.gpio_write(h, LCD_D7, 1 if bits & 0x80 else 0)
    lcd_toggle_enable()

    # Low bits
    GPIO.gpio_write(h, LCD_D4, 1 if bits & 0x01 else 0)
    GPIO.gpio_write(h, LCD_D5, 1 if bits & 0x02 else 0)
    GPIO.gpio_write(h, LCD_D6, 1 if bits & 0x04 else 0)
    GPIO.gpio_write(h, LCD_D7, 1 if bits & 0x08 else 0)
    lcd_toggle_enable()

def lcd_toggle_enable():
    """Toggle enable pin."""
    time.sleep(E_DELAY)
    GPIO.gpio_write(h, LCD_E, 1)
    time.sleep(E_PULSE)
    GPIO.gpio_write(h, LCD_E, 0)
    time.sleep(E_DELAY)

def lcd_string(message, line):
    """Send string to display."""
    message = message.ljust(LCD_WIDTH, " ")
    lcd_byte(line, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)

# Initialize and display message
lcd_init()
lcd_string("Hello, Pi 5!", LCD_LINE_1)
lcd_string("Using lgpio!", LCD_LINE_2)

time.sleep(5)

lcd_string("It works!", LCD_LINE_1)
lcd_string("Success!", LCD_LINE_2)

time.sleep(5)

# Cleanup
GPIO.gpiochip_close(h)
