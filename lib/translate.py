#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# translate.py - Morse code translator
#

from lib import beatcount
import RPi.GPIO as GPIO
import sys
import time

# Morse Code Dictionary
letters_to_morse = {
    "A" : ".-",
    "B" : "-...",
    "C" : "-.-.",
    "D" : "-..",
    "E" : ".",
    "F" : "..-.",
    "G" : "--.",
    "H" : "....",
    "I" : "..",
    "J" : ".---",
    "K" : "-.-",
    "L" : ".-..",
    "M" : "--",
    "N" : "-.",
    "O" : "---",
    "P" : ".--.",
    "Q" : "--.-",
    "R" : ".-.",
    "S" : "...",
    "T" : "-",
    "U" : "..-",
    "V" : "...-",
    "W" : ".--",
    "X" : "-..-",
    "Y" : "-.--",
    "Z" : "--..",
    "1" : ".----",
    "2" : "..---",
    "3" : "...--",
    "4" : "....-",
    "5" : ".....",
    "6" : "-....",
    "7" : "--...",
    "8" : "---..",
    "9" : "----.",
    "0" : "-----",
    "AA/New Line" : ".-.-",
    "AR/New Page" : ".-.-.",
    "AS/WAIT" : ".-...",
    "BT/New Paragraph" : "-...-",
    "HH/ERROR" : "........",
    "KN/OK, Named" : "-.--.",
    "SK/End Contact" : "...-.-",
    "SN/Understood" : "...-.",
    "SOS" : "...---...",
    " " : "/",
    "." : ".-.-.-",
    "," : "--..--",
    "?" : "..--..",
    "'" : ".----.",
    "!" : "-.-.--",
    "/" : "-..-.",
    "(" : "-.--.",
    ")" : "-.--.-",
    "&" : ".-...",
    ":" : "---...",
    ";" : "-.-.-.",
    "=" : "-...-",
    "+/ATTENTION" : ".-.-.",
    "-" : "-....-",
    "_" : "..--.-",
    "\"" : ".-..-.",
    "$" : "..-..-",
    "@" : ".--.-.",
    }

morse_to_letters = dict((v,k) for (k,v) in letters_to_morse.items())

def morse_to_text(verbose, gpio, period, max_bpm, dashduration):
    sleep_time = 1 / max_bpm  # Calculate minimum sleep duration possible to detect the maximum BPM
    debounce_delay = 60000 / max_bpm
    milliseconds_pressed = 0
    char_in_morse = ""  # Holds string of "-" and "."

    if not dashduration:
        print '\nThe duration of dashes and dots and between words and letters needs to be determined.', \
              '\nBegin tapping a tempo to set the duration of a dash (also space between letters).', \
              '\nTiming will begin upon the first buttom press and be measured for {} milliseconds.\n'.format(period)

        # Calculate the exact durations for a dot, dash, letter space, and word space
        count, duration_average = beatcount.beat_counter(verbose, gpio, period, max_bpm)
        print 'Done!'
        milliseconds_space_dash = duration_average
    else:
        milliseconds_space_dash = dashduration

    milliseconds_dot = milliseconds_space_dash / 3
    milliseconds_between_words = milliseconds_dot * 7

    # Since pressing a button for an exact period of time, accurate to milliseconds,
    # is difficult, ranges of acceptable durations are calcuated, with the point
    # exactly between the exact durations serving as the bounds of acceptable error.
    milliseconds_dash_error_high = (milliseconds_space_dash + milliseconds_between_words) / 2
    milliseconds_dot_error_high = (milliseconds_dot + milliseconds_space_dash) / 2

    # Present the exact durations for each unit
    print '\nDurations acquired (ms = milliseconds):'
    print 'Between words: {} ms'.format(milliseconds_between_words)
    print 'Between letters: {} ms'.format(milliseconds_space_dash)
    print 'Dash: {} ms'.format(milliseconds_space_dash)
    print 'Dot: {} ms'.format(milliseconds_dot)

    # Present the ranges of durations that are acceptable for translation
    print '\nA Dot will register when the pressed duration is between {} and {} ms'.format(debounce_delay, milliseconds_dot_error_high)
    print 'A Dash will register when the pressed duration is between {} and {} ms'.format(milliseconds_dot_error_high, milliseconds_dash_error_high)
    print 'A new letter will register when the unpressed duration is between between {} and {} ms'.format(milliseconds_dot_error_high, milliseconds_dash_error_high)
    print 'A new word will register when the unpressed duration is greater than {} ms'.format(milliseconds_dash_error_high)

    if not dashduration:
        print '\nWait 5 seconds before beginning Morse code...\n'
        time.sleep(5)
    else:
        print ''

    print 'Ready! Morse code translation will begin automatically.\n'

    while GPIO.input(gpio):  # while the button is not pressed
        time.sleep(sleep_time)

    while True:  
        #
        # Begin timing how long the button is pressed
        #
        button_duration = int(round(time.time()*1000))

        # Wait while the button is pressed
        # This times how long the button is pressed for, and excludes periods below the max_bpm
        # The second condition debounces the input, preventing registering of multiple presses
        while (GPIO.input(gpio) == False or
               int(round(time.time()*1000)) - button_duration < debounce_delay):
            time.sleep(sleep_time)

        milliseconds_pressed = int(round(time.time()*1000)) - button_duration
        if verbose:
            print 'Pressed {} ms'.format(milliseconds_pressed),

        # The duration of the press can only be translated to a dot or a dash
        # Holding a press for longer than milliseconds_dash_error_high will result in neither a dot or a dash
        if milliseconds_dot_error_high > milliseconds_pressed > 50:
            char_in_morse = char_in_morse + "."  # Append Dot to Morse code string
            sys.stdout.write('.')
        elif milliseconds_dash_error_high > milliseconds_pressed > milliseconds_dot_error_high:
            char_in_morse = char_in_morse + "-"  # Append Dash to Morse code string
            sys.stdout.write('-')
        sys.stdout.flush()

        #
        # Begin timing how long the button is unpressed
        #
        button_duration = int(round(time.time()*1000))

        # Wait for a button press or the wait time exceeds that of a space between letters
        while ((GPIO.input(gpio) or int(round(time.time()*1000)) - button_duration < debounce_delay) and
                int(round(time.time()*1000)) - button_duration <= milliseconds_dot_error_high):
            time.sleep(sleep_time)

        # If the unpressed duration exceeds that for a new letter,
        # issue a letter and clear char_in_morse, the Morse code-holding string
        if int(round(time.time()*1000)) - button_duration >= milliseconds_dot_error_high:
            if char_in_morse in morse_to_letters:
                sys.stdout.write(' [%s] ' % morse_to_letters[char_in_morse])
            else:
                sys.stdout.write(' [NA] ')
            char_in_morse = ""
            sys.stdout.flush()

        # Wait for a button press or the wait time exceeds that of a space between words
        while (GPIO.input(gpio) and
               int(round(time.time()*1000)) - button_duration <= milliseconds_dash_error_high):
            time.sleep(sleep_time)

        # If the unpressed duration exceeds that for a space, issue a space
        if int(round(time.time()*1000)) - button_duration >= milliseconds_dash_error_high:
            sys.stdout.write('[ ] ')
            sys.stdout.flush()

        # Wait while the button is unpressed
        # This is a catch if the letter has been translated and a word space has been inserted
        while GPIO.input(gpio):
            time.sleep(sleep_time)

        if verbose:
            print 'Unpressed {} ms'.format(int(round(time.time()*1000)) - button_duration)


def text_to_morse(dashduration):
    while True:
        print ''
        text_input = raw_input("Enter text to translate to Morse code: ")

        string_valid = True
        for letter in text_input:
            if letter.upper() not in letters_to_morse:
                string_valid = False
                
        if string_valid:
            total_duration = 0
            for letter in text_input:
                print '{}'.format(letters_to_morse[letter.upper()]),
                total_duration = total_duration + letter_duration(dashduration, letters_to_morse[letter.upper()])
            print '\nTime to transmit (dash = {} ms): {} ms'.format(dashduration, total_duration)
        else:
            print 'Invalid string. Only A-Z, 0-9, spaces, and certain symbols are allowed.',


def letter_duration(dashduration, morse_letter_code):
    total_duration = 0
    for unit in morse_letter_code:
        if unit == "-":
            total_duration = total_duration + dashduration
        elif unit == ".":
            total_duration = total_duration + (dashduration / 3)
        elif unit == "/":
            total_duration = total_duration + (dashduration / 3 * 7)

        # Add duration between letters
        first = True
        if first:
            first = False
        else: 
            total_duration = total_duration + dashduration

    return total_duration
