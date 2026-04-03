#include "motor.h"
#include "nrf_gpio.h"

// Pin definitions (modify if needed)
#define IN1_PIN 6
#define IN2_PIN 5

void motor_init(void) {
    nrf_gpio_cfg_output(IN1_PIN);
    nrf_gpio_cfg_output(IN2_PIN);
    motor_stop();  // Ensure motor is stopped on init
}

void motor_forward(void) {
    nrf_gpio_pin_set(IN1_PIN);
    nrf_gpio_pin_clear(IN2_PIN);
}

void motor_backward(void) {
    nrf_gpio_pin_clear(IN1_PIN);
    nrf_gpio_pin_set(IN2_PIN);
}

void motor_stop(void) {
    nrf_gpio_pin_clear(IN1_PIN);
    nrf_gpio_pin_clear(IN2_PIN);
}