#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# translate.py - Morse code translator
#

import RPi.GPIO as GPIO
import sys
import time

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
    "+" : ".-.-.",
    "-" : "-....-",
    "_" : "..--.-",
    "\"" : ".-..-.",
    "$" : "..-..-",
    "@" : ".--.-.",
    }

morse_to_letters = dict((v,k) for (k,v) in letters_to_morse.items())

def morse_to_text(verbose, gpio, period, max_bpm):
    print '\nA tempo needs to be set to determine the duration of dashes and dots and between words and letters.', \
          '\nBegin tapping a tempo to set the duration between letters.', \
          '\nTiming will begin upon the first buttom press and be measured for {} milliseconds.\n'.format(period)

    milliseconds_space_dash = detect_bpm(verbose, gpio, period, max_bpm)
    milliseconds_dot = milliseconds_space_dash / 3
    milliseconds_between_words = milliseconds_dot * 7

    milliseconds_dash_error_high = (milliseconds_space_dash + milliseconds_between_words) / 2
    milliseconds_dot_error_high = (milliseconds_dot + milliseconds_space_dash) / 2

    print '\nDurations acquired (ms = milliseconds):'
    print 'Between words: {} ms'.format(milliseconds_between_words)
    print 'Between letters: {} ms'.format(milliseconds_space_dash)
    print 'Dash: {} ms'.format(milliseconds_space_dash)
    print 'Dot: {} ms'.format(milliseconds_dot)
    
    print '\nA Dot will register when the pressed duration is between {} and {} ms'.format(60000 / max_bpm, milliseconds_dot_error_high)
    print 'A Dash will register when the pressed duration is between {} and {} ms'.format(milliseconds_dot_error_high, milliseconds_dash_error_high)
    print 'A new letter will register when the unpressed duration is between between {} and {} ms'.format(milliseconds_dot_error_high, milliseconds_dash_error_high)
    print 'A new word will register when the unpressed duration is greater than {} ms'.format(milliseconds_dash_error_high)

    print '\nWait 5 seconds before beginning Morse code...\n'

    time.sleep(5)

    print 'Ready! Morse code translation will begin automatically.\n'

    sleep_time = 1 / max_bpm  # Calculate minimum sleep duration possible to detect the maximum BPM
    milliseconds_pressed = 0
    milliseconds_unpressed = 0
    unpressed_char = [] # Determines if there is a new letter or space
    char_in_morse = "" # Holds "-" and "."

    while GPIO.input(gpio): # while the button is not pressed
            time.sleep(0.01)

    while True:  
        time_pressed = int(round(time.time()*1000)) # Begin timing how long the button is pressed
        
        while GPIO.input(gpio) == False or int(round(time.time()*1000)) - time_pressed < 60000 / max_bpm: # while the button is pressed
            time.sleep(sleep_time)

        milliseconds_pressed = int(round(time.time()*1000)) - time_pressed # How long was the button was pressed
        
        if verbose:
            print 'Pressed {} ms'.format(milliseconds_pressed),
        if milliseconds_dot_error_high > milliseconds_pressed > 50: # If within error of dot duration, append dot
            char_in_morse = char_in_morse + "."
            print '.',
        elif milliseconds_dash_error_high > milliseconds_pressed > milliseconds_dot_error_high: # append dash
            char_in_morse = char_in_morse + "-"
            print '-',
        else:
            if verbose:
                print ''
        sys.stdout.flush()

        time_pressed = int(round(time.time()*1000)) # Begin timing how long the button is unpressed

        while GPIO.input(gpio) or int(round(time.time()*1000)) - time_pressed < 60000 / max_bpm: # while the button is not pressed
            time.sleep(0.01)

        milliseconds_unpressed = int(round(time.time()*1000)) - time_pressed # How long was the button was unpressed
        if verbose:
            print 'Unpressed {} ms'.format(milliseconds_unpressed)

        if milliseconds_dash_error_high > milliseconds_unpressed > milliseconds_dot_error_high:
            # unpressed_char = "letter"
            if char_in_morse in morse_to_letters:
                print '[{}]'.format(morse_to_letters[char_in_morse]),
            else:
                print '[NA]',
            char_in_morse = ""
        elif milliseconds_unpressed > milliseconds_dash_error_high:
            # unpressed_char = "space"
            if char_in_morse in morse_to_letters:
                print '[{}]'.format(morse_to_letters[char_in_morse]),
            else:
                print '[NA]',
            print '[ ]',
            char_in_morse = ""
        sys.stdout.flush()


def text_to_morse():
    while True:
        text_input = raw_input("Enter text (A-Z, 0-9, spaces) to translate to Morse code: ")

        string_valid = True
        for letter in text_input:
            if letter.upper() not in letters_to_morse:
                string_valid = False
                
        if string_valid:
            for letter in text_input:
                print '{}'.format(letters_to_morse[letter.upper()]),
        else:
            print 'Invalid string. Only A-Z, 0-9, and spaces are allowed.',

        print '\n'


def detect_bpm(verbose, gpio, period, max_bpm):
    sleep_time = 1 / max_bpm  # Calculate minimum sleep duration possible to detect the maximum BPM
    beat_count_period = 1
    duration_total = 0
    detected_milliseconds = 0
    first_beat = True

    # Wait until the button is pressed for the first time
    while GPIO.input(gpio): # While button is not pressed
        time.sleep(0.01)

    start_time = time_between_beatcount = int(round(time.time()*1000))
    if verbose:
        print 'Beat number {}, Time: {}'.format(beat_count_period, start_time)
    else:
        print '.',
        sys.stdout.flush()

    while not detected_milliseconds:
        # Duration between beats must be greater than or equal to the duration of max BPM in milliseconds
        if int(round(time.time()*1000)) - time_between_beatcount >= 60000 / max_bpm:

            if GPIO.input(gpio) == False: # If button is pressed
                time_now = int(round(time.time()*1000))
                beat_count_period += 1

                if first_beat:
                    duration_total = int(round(time.time()*1000)) - time_between_beatcount
                    first_beat = False
                else:
                    duration_total = (int(round(time.time()*1000)) - time_between_beatcount) + duration_total
                if verbose:
                    print 'Beat number {}, Time: {}, Diff: {} ms, Average: {} ms'.format(beat_count_period, time_now, time_now - time_between_beatcount, duration_total / (beat_count_period - 1))
                else:
                    print '.',
                    sys.stdout.flush()

                time_between_beatcount = time_now
                while GPIO.input(gpio) == False:
                    time.sleep(sleep_time)

        if int(round(time.time()*1000)) - start_time > period:
            detected_milliseconds = duration_total / (beat_count_period - 1)
        time.sleep(sleep_time)

    if not verbose:
        print 'Done!'

    return detected_milliseconds
