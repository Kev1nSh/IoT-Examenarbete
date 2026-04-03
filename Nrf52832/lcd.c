#include "lcd.h"
#include "nrf_gpio.h"
#include "app_timer.h"
#include <string.h>

APP_TIMER_DEF(m_lcd_scroll_timer);

#define LCD_WIDTH 16
#define BASE_SCROLL_INTERVAL_MS 250
#define EXTRA_SCROLL_TIME_MS 30

static char scroll_buffer[128] = {0};
static int scroll_pos = 0;
static int scroll_total = 0;
static bool scrolling_enabled = false;
static bool scroll_needed = false;
static bool pause_active = false;
static int pause_counter = 0;
static int pause_ticks_needed_start = 10;
static int pause_ticks_needed_end = 10;    // ~1 sec pause after full scroll
static uint32_t current_scroll_interval = APP_TIMER_TICKS(BASE_SCROLL_INTERVAL_MS);

static void lcd_pulse_enable(void) {
    nrf_gpio_pin_set(LCD_E);
    __NOP(); __NOP();
    nrf_gpio_pin_clear(LCD_E);
    __NOP(); __NOP();
}

static void lcd_write_nibble(uint8_t nibble) {
    nrf_gpio_pin_write(LCD_D4, (nibble >> 0) & 0x01);
    nrf_gpio_pin_write(LCD_D5, (nibble >> 1) & 0x01);
    nrf_gpio_pin_write(LCD_D6, (nibble >> 2) & 0x01);
    nrf_gpio_pin_write(LCD_D7, (nibble >> 3) & 0x01);
    lcd_pulse_enable();
}

static void lcd_write_byte(uint8_t data, bool is_data) {
    nrf_gpio_pin_write(LCD_RS, is_data);
    lcd_write_nibble(data >> 4);
    lcd_write_nibble(data & 0x0F);
    for (volatile int i = 0; i < 4000; i++) __NOP();
}

static void lcd_scroll_handler(void *p_context);

void lcd_init(void) {
    nrf_gpio_cfg_output(LCD_RS);
    nrf_gpio_cfg_output(LCD_E);
    nrf_gpio_cfg_output(LCD_D4);
    nrf_gpio_cfg_output(LCD_D5);
    nrf_gpio_cfg_output(LCD_D6);
    nrf_gpio_cfg_output(LCD_D7);

    for (volatile int i = 0; i < 500000; i++) __NOP();

    lcd_write_nibble(0x03);
    for (volatile int i = 0; i < 50000; i++) __NOP();
    lcd_write_nibble(0x03);
    for (volatile int i = 0; i < 15000; i++) __NOP();
    lcd_write_nibble(0x03);
    for (volatile int i = 0; i < 15000; i++) __NOP();
    lcd_write_nibble(0x02);

    lcd_write_byte(0x28, false);
    lcd_write_byte(0x0C, false);
    lcd_write_byte(0x06, false);
    lcd_clear();

    app_timer_create(&m_lcd_scroll_timer, APP_TIMER_MODE_REPEATED, lcd_scroll_handler);
}

void lcd_clear(void) {
    lcd_write_byte(0x01, false);
    for (volatile int i = 0; i < 60000; i++) __NOP();
}

void lcd_set_cursor(uint8_t row, uint8_t col) {
    uint8_t addr = (row == 0) ? col : (0x40 + col);
    lcd_write_byte(0x80 | addr, false);
}

void lcd_print(const char *str) {
    while (*str) {
        lcd_write_byte(*str++, true);
    }
}

static void lcd_scroll_handler(void *p_context) {

    lcd_clear();
    lcd_set_cursor(0, 0);

    // --- Always print the current frame ---
    for (int i = 0; i < LCD_WIDTH; i++) {
        char c = ' ';
        if ((scroll_pos + i) < scroll_total) {
            c = scroll_buffer[scroll_pos + i];
        }
        lcd_write_byte(c, true);
    }

    if (scroll_needed) {
        if (pause_active) {
            pause_counter++;
            if (pause_counter >= pause_ticks_needed_start) {
                pause_active = false;
                pause_counter = 0;
                scroll_pos++;  // After pause, scroll next
            }
            // else: still paused, keep showing
        }
        else {
            scroll_pos++;
        }

        if (scroll_pos > (scroll_total - LCD_WIDTH)) {
            scroll_pos = 0;
            pause_active = true;
            pause_counter = 0;
        }
    }
}

void lcd_start_scroll(const char *text) {
    memset(scroll_buffer, 0, sizeof(scroll_buffer));
    snprintf(scroll_buffer, sizeof(scroll_buffer), "%s", text);

    scroll_total = strlen(text);
    scrolling_enabled = true;
    scroll_pos = 0;
    pause_counter = 0;
    pause_active = true;  // <- first pause after showing first frame

    if (scroll_total <= LCD_WIDTH) {
        scroll_needed = false;
    } else {
        scroll_needed = true;
    }

    // Dynamic scroll interval calculation
    uint32_t extra_time = 0;
    if (scroll_total > LCD_WIDTH) {
        extra_time = (scroll_total - LCD_WIDTH) * EXTRA_SCROLL_TIME_MS;
    }
    current_scroll_interval = APP_TIMER_TICKS(BASE_SCROLL_INTERVAL_MS + extra_time);

    app_timer_start(m_lcd_scroll_timer, current_scroll_interval, NULL);
}

void lcd_stop_scroll(void) {
    scrolling_enabled = false;
    app_timer_stop(m_lcd_scroll_timer);
}