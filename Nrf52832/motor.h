#ifndef MOTOR_H
#define MOTOR_H

#include <stdint.h>
#include <stdbool.h>

void motor_init(void);
void motor_forward(void);
void motor_backward(void);
void motor_stop(void);

#endif // MOTOR_H