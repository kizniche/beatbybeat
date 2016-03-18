#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# lcd.py - LCD output library for beatbybeat
#

import smbus
import time


class LCDOutput():
    """
    Class to output to LCD, one letter at a time,
    and move the previous letters to the left and up
    
    """

    def __init__(self, o2c_address):
        # Define some device parameters
        # self.I2C_ADDR  = 0x25 # I2C device address
        self.I2C_ADDR  = int(o2c_address, 16) # I2C device address
        self.LCD_WIDTH = 16   # Maximum characters per line

        # Define some device constants
        self.LCD_CHR = 1 # Mode - Sending data
        self.LCD_CMD = 0 # Mode - Sending command

        self.LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
        self.LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
        # self.LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
        # self.LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

        self.LCD_BACKLIGHT  = 0x08  # On
        # self.LCD_BACKLIGHT = 0x00  # Off

        self.ENABLE = 0b00000100 # Enable bit

        # Timing constants
        self.E_PULSE = 0.0005
        self.E_DELAY = 0.0005

        #Open I2C interface
        #bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
        self.bus = smbus.SMBus(1) # Rev 2 Pi uses 1

        # Initialize list of 16 spaces
        self.letter_string = [" "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ",
                              " "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ",]
        
        self.lcd_init()

        self.lcd_string("Beatbybeat Morse", 1)
        self.lcd_string("Code Translator ", 2)

        time.sleep(3)


    def add_letter(self, letter):
        self.letter_string.append(letter)
        self.letter_string = self.letter_string[1:]

        self.lcd_string(''.join(self.letter_string[0:16]), 1)
        self.lcd_string(''.join(self.letter_string[16:32]) , 2)


    def lcd_init(self):
        # Initialise display
        self.lcd_byte(0x33,self.LCD_CMD) # 110011 Initialise
        self.lcd_byte(0x32,self.LCD_CMD) # 110010 Initialise
        self.lcd_byte(0x06,self.LCD_CMD) # 000110 Cursor move direction
        self.lcd_byte(0x0C,self.LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
        self.lcd_byte(0x28,self.LCD_CMD) # 101000 Data length, number of lines, font size
        self.lcd_byte(0x01,self.LCD_CMD) # 000001 Clear display
        time.sleep(self.E_DELAY)

    def lcd_clear(self):
        self.lcd_init()


    def lcd_byte(self, bits, mode):
        # Send byte to data pins
        # bits = the data
        # mode = 1 for data
        #        0 for command
        bits_high = mode | (bits & 0xF0) | self.LCD_BACKLIGHT
        bits_low = mode | ((bits<<4) & 0xF0) | self.LCD_BACKLIGHT
        # High bits
        self.bus.write_byte(self.I2C_ADDR, bits_high)
        self.lcd_toggle_enable(bits_high)
        # Low bits
        self.bus.write_byte(self.I2C_ADDR, bits_low)
        self.lcd_toggle_enable(bits_low)


    def lcd_toggle_enable(self, bits):
        # Toggle enable
        time.sleep(self.E_DELAY)
        self.bus.write_byte(self.I2C_ADDR, (bits | self.ENABLE))
        time.sleep(self.E_PULSE)
        self.bus.write_byte(self.I2C_ADDR,(bits & ~self.ENABLE))
        time.sleep(self.E_DELAY)


    def lcd_string(self, message, line):
        # Send string to display
        if line == 1:
            line = self.LCD_LINE_1
        elif line == 2:
            line = self.LCD_LINE_2
        message = message.ljust(self.LCD_WIDTH," ")
        self.lcd_byte(line, self.LCD_CMD)
        for i in range(self.LCD_WIDTH):   
            self.lcd_byte(ord(message[i]),self.LCD_CHR)
