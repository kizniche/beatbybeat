#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# beatbybeat.py - BPM counter and Morse code translator
#

from lib import beatcount
from lib import translate
import argparse
import os
import RPi.GPIO as GPIO
import sys


def menu():
    parser = argparse.ArgumentParser(description='Beat counter (bpm) and '
                                                 'Morse code translator')

    beat_counter = parser.add_argument_group('Beat counter')
    beat_counter.add_argument('-b', '--bpmcount', action='store_true',
                              help="Start program to count beats (bpm)")

    beat_counter.add_argument('-m', '--maxbpm', metavar='MAXBPM', type=int,
                              help='Set maximum detectable BPM (lower number '
                                   'improves accuracy, higher numbers may '
                                   'register erroneous taps, below 2000 '
                                   'should be accurate), default: 2000',
                              default=2000,
                              required=False)

    beat_counter.add_argument('-p', '--period', metavar='PERIOD', type=int,
                              help='Period of time between BPM calculations '
                                   '(milliseconds), default: 5000',
                              default=5000,
                              required=False)

    morse_translator = parser.add_argument_group('Morse code translator')
    morse_translator.add_argument('-mt', '--morsetotext', action='store_true',
                              help="Translate Morse code to text")

    morse_translator.add_argument('-tm', '--texttomorse', action='store_true',
                              help="Translate text to Morse code")

    morse_translator.add_argument('-t', '--textonly', action='store_true',
                              help="Show only translated letters (Morse to "
                                   "text translation only)")

    morse_translator.add_argument('-d', '--dashduration', metavar='DASHDURATION',
                                  type=int,
                              help='Duration of a dash (Morse-to-text '
                                   'default: none, Text-to-Morse default: '
                                   '300 ms). If set with -mt the tempo '
                                   'detection will be overridden.',
                              default=0,
                              required=False)

    misc_options = parser.add_argument_group('Miscelaneous')
    misc_options.add_argument('-g', '--gpio', metavar='GPIO', type=int,
                              help='GPIO pin connected to the telegraph '
                                   '(using BCM numbering)')

    misc_options.add_argument('-l', '--lcd', metavar='I2CADDRESS', type=str,
                              help='Specify the I2C address of 2x16 '
                                   'character LCD (I2C backpack) to '
                                   'output to. ex. "0x25"',
                              default='0',
                              required=False)

    misc_options.add_argument('-v', '--verbose', action='store_true',
                              help="Print more information to the terminal")

    args = parser.parse_args()

    if os.geteuid() and not args.texttomorse:
        print "Script must be ran as root to access GPIO"
        sys.exit(0)

    ########################################
    #                                      #
    #           Setup Options              #
    #                                      #
    ########################################

    if not (args.bpmcount or args.morsetotext or args.texttomorse):
        parser.error('No action requested, add --bpmcount or --morsetotext or '
                     '--texttomorse')
    elif sum(map(bool, [args.bpmcount, args.morsetotext, args.texttomorse])) != 1:
        parser.error('Can only select one: --bpmcount (-b), --morsetotext '
                     '(-mt), or --texttomorse (-tm)')
    elif args.bpmcount:
        if not args.gpio:
            parser.error('Need to specify GPIO pin with --gpio')
        else:
            print 'Beats per minute (BPM) counter',
    elif args.morsetotext:
        if not args.gpio:
            parser.error('Need to specify GPIO pin with --gpio')
        else:
            print 'Morse code to text translator',
    elif args.texttomorse:
        print 'Text to Morse code translator (use only A-Z, 0-9, spaces, ' \
              'and symbols /?\'!@$&()_-+=,.;:")',

    if args.verbose:
        print '(Verbose)'
    else:
        print ''

    ########################################
    #                                      #
    #             Setup GPIO               #
    #                                      #
    ########################################

    if args.gpio:
        print 'Setting up GPIO {}:'.format(args.gpio),
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(args.gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        except:
            print 'Fail'
        else:
            print 'Success'

    ########################################
    #                                      #
    #             Beat Counter             #
    #                                      #
    ########################################

    if args.bpmcount:
        print 'Tempo calculation period: {} milliseconds, Max BPM: {} BPM, ' \
              'Debounce Delay: {} ms'.format(
                args.period, args.maxbpm, 60000 / args.maxbpm)
        print '\nBegin tapping a tempo to identify the duration between beats.', \
              '\nCalculations will only be performed while there is tapping.', \
              '\nTiming will begin upon the first buttom press and be ' \
              'measured every {} milliseconds.\n'.format(args.period)
        while True:
            count, duration_average = beatcount.beat_counter(
                args.verbose, args.gpio, args.period, args.maxbpm)
            print '\nCalculated from total number of beats over time: {} ' \
                  'beats per {} ms = {} BPM'.format(
                    count, args.period, count * (60 / (args.period / 1000)))
            print 'Calculated from average duration between beats: {} ms ' \
                  'per beat = {} BPM\n'.format(
                    duration_average, 60000 / duration_average)

    ########################################
    #                                      #
    #    Morse Code to Text Translator     #
    #                                      #
    ########################################

    if args.morsetotext:
        if args.dashduration == 0:
            dashduration = 300
        else:
            dashduration = args.dashduration
        if dashduration / 3 < 60000 / args.maxbpm:
            parser.error('--dashduration too low. Increase -d or degrease -b')
        print 'Tempo calculation period: {} milliseconds, Max BPM: {} BPM, ' \
              'Debounce Delay: {} ms'.format(
                args.period, args.maxbpm, 60000 / args.maxbpm)
        translate.morse_to_text(args.verbose, args.textonly, args.gpio,
                                args.period, args.maxbpm, args.dashduration,
                                args.lcd)

    ########################################
    #                                      #
    #    Text to Morse Code Translator     #
    #                                      #
    ########################################

    if args.texttomorse:
        dashduration = args.dashduration
        if not dashduration:
            dashduration = 300  # Default dash time (milliseconds)
        print 'Dash Duration: {} ms'.format(dashduration)
        translate.text_to_morse(dashduration)


def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)


def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = the data
  # mode = 1 for data
  #        0 for command
  bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
  bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT
  # High bits
  bus.write_byte(I2C_ADDR, bits_high)
  lcd_toggle_enable(bits_high)
  # Low bits
  bus.write_byte(I2C_ADDR, bits_low)
  lcd_toggle_enable(bits_low)


def lcd_toggle_enable(bits):
  # Toggle enable
  time.sleep(E_DELAY)
  bus.write_byte(I2C_ADDR, (bits | ENABLE))
  time.sleep(E_PULSE)
  bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
  time.sleep(E_DELAY)


def lcd_string(message,line):
  # Send string to display
  message = message.ljust(LCD_WIDTH," ")
  lcd_byte(line, LCD_CMD)
  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)



if __name__ == "__main__":
    menu()
    sys.exit(0)
