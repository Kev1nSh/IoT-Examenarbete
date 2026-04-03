import RPi.GPIO as GPIO
import time




# 1x H-bridge motor driver [L293D],
# 2x DC motor,

# Vi ställer in GPIO-pinnarna för att styra båda motorn
# Allt nedanför.

MOTORS = {
    "motor1": {"IN1": 17, "IN2": 27, "ENA": 22},
    "motor2": {"IN1": 23, "IN2": 24, "ENA": 25},
}

GPIO.setmode(GPIO.BCM)

for motor, pins in MOTORS.items():
    GPIO.setup(pins["IN1"], GPIO.OUT)
    GPIO.setup(pins["IN2"], GPIO.OUT)
    GPIO.setup(pins["ENA"], GPIO.OUT)

# Vi skapar en PWM-kanal för att styra hastigheten på båda motorerna
pwm1 = GPIO.PWM(MOTORS["motor1"]["ENA"], 1000)
pwm2 = GPIO.PWM(MOTORS["motor2"]["ENA"], 1000)

pwm1.start(50) # Vi startar med 50% hastighet
pwm2.start(50) 

def move_motor(motor, direction = "up", speed = 50, duration = 5):
    """Styr en motor i en viss riktning och hastighet."""
    
    pins = MOTORS[motor]

    if direction == "up":
        GPIO.output(pins["IN1"], GPIO.HIGH)
        GPIO.output(pins["IN2"], GPIO.LOW)
    
    elif direction == "down":
        GPIO.output(pins["IN1"], GPIO.LOW)
        GPIO.output(pins["IN2"], GPIO.HIGH)
    
    else:
        stop_motor(motor) 
        return
    
    if motor == "motor1":
        pwm1.ChangeDutyCycle(speed)

    elif motor == "motor2":
        pwm2.ChangeDutyCycle(speed)
    
    time.sleep(duration)
    stop_motor(motor)

def stop_motor(motor):
    """Stannar motor"""
    pins = MOTORS[motor]
    GPIO.output(pins["IN1"], GPIO.LOW)
    GPIO.output(pins["IN2"], GPIO.LOW)

def roll_all_down(speed = 50):
    """Rullar ner båda rullgardinerna."""
    move_motor("motor1", "down", speed, 5)
    move_motor("motor2", "down", speed, 5)

def roll_all_up(speed = 50):
    """Rullar upp båda rullgardinerna."""
    move_motor("motor1", "up", speed, 5)
    move_motor("motor2", "up", speed, 5)

if __name__ == "__main__":

    try:
        roll_all_down(75)
        time.sleep(2)
        roll_all_up(50)
        GPIO.cleanup()

    except KeyboardInterrupt:
        for motor in MOTORS:
            stop_motor(motor)
        GPIO.cleanup()
        print("Test avslutades")

