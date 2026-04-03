#ifndef LCD_H
#define LCD_H

#include <stdbool.h>
#include <stdint.h>

// === LCD pin assignments ===
#define LCD_RS     3
#define LCD_E      4
#define LCD_D4     28
#define LCD_D5     29
#define LCD_D6     30
#define LCD_D7     31


// === API ===
void lcd_init(void);
void lcd_print(const char *str);
void lcd_clear(void);
void lcd_set_cursor(uint8_t row, uint8_t col);
void lcd_start_scroll(const char *text);
void lcd_stop_scroll(void);

#endif // LCD_H