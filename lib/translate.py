#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# translate.py - Morse code translator
#

import RPi.GPIO as GPIO
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
    }

morse_to_letters = dict((v,k) for (k,v) in letters_to_morse.items())

def morse_translator(verbose, gpio, period, max_bpm):
    print '\nA tempo needs to be set to determine the duration of dashes and dots and between words and letters.', \
          '\nBegin tapping a tempo to set the duration between letters.', \
          '\nTiming will begin upon the first buttom press and be measured for {} milliseconds.\n'.format(period)

    milliseconds_dot = milliseconds_space_dash / 3
    milliseconds_dot_error_high = (milliseconds_dot + milliseconds_space_dash) / 2

    milliseconds_space_dash = detect_bpm(verbose, gpio, period, max_bpm)
    milliseconds_dash_error_high = (milliseconds_space_dash + milliseconds_between_words) / 2

    milliseconds_between_words = milliseconds_dot * 7
    print '\nDurations acquired (ms = milliseconds):'
    print 'Between words: {} ms'.format(milliseconds_between_words)
    print 'Between letters: {} ms'.format(milliseconds_space_dash)
    print 'Dash: {} ms'.format(milliseconds_space_dash)
    print 'Dot: {} ms'.format(milliseconds_dot)
    print '\nWait 5 seconds before beginning Morse code...\n'
    time.sleep(5)
    
    print 'Ready! Morse code translation will begin automatically.'
    print 'A new letter will begin when the duration between dashes or dots is greater than or equal to {} ms.'.format(milliseconds_space_dash)
    print 'A new word will begin when the duration between dashes or dots is greater than or equal to {} ms.\n'.format(milliseconds_between_words)

    sleep_time = 1 / max_bpm  # Calculate minimum sleep duration possible to detect the maximum BPM
    milliseconds_pressed = 0
    milliseconds_unpressed = 0
    unpressed_char = [] # Determines if there is a new letter or space
    char_in_morse = [] # Holds "-" and "."

    while GPIO.input(gpio): # Wait while the button is not pressed (i.e. wait for the first press)
        time.sleep(0.01)

    while True:
        time_pressed = int(round(time.time()*1000)) # Begin timing how long the button is pressed

        # Duration between beats must be greater than or equal to the duration of max BPM in milliseconds
        # This is used to prevent "accidental" taps (~20 milliseconds)
        if int(round(time.time()*1000)) - time_pressed >= 60000 / max_bpm:

            if GPIO.input(gpio) == False: # The button is pressed
                milliseconds_pressed = int(round(time.time()*1000)) - time_pressed # How long was the button was pressed

                if milliseconds_dot_error_high > milliseconds_pressed > 60000 / max_bpm: # If within error of dot duration, append dot
                    char_in_morse = char_in_morse + "."
                    print '.',
                elif milliseconds_dash_error_high > milliseconds_pressed > milliseconds_dot_error_high: # append dash
                    char_in_morse = char_in_morse + "-"
                    print '-',

                time_pressed = int(round(time.time()*1000)) # Begin timing how long the button is unpressed

                while GPIO.input(gpio) == False: # Wait while the button is pressed
                    time.sleep(sleep_time)

                milliseconds_unpressed = int(round(time.time()*1000)) - time_pressed # How long was the button was unpressed

                if milliseconds_dash_error_high > milliseconds_unpressed > milliseconds_dot_error_high:
                    unpressed_char = "letter"
                else:
                    unpressed_char = "space"


        time.sleep(sleep_time)


def detect_bpm(verbose, gpio, period, max_bpm):
    sleep_time = 1 / max_bpm  # Calculate minimum sleep duration possible to detect the maximum BPM
    beat_count_period = 1
    duration_total = 0
    detected_milliseconds = 0
    first_beat = True

    # Wait until the button is pressed for the first time
    while GPIO.input(gpio):
        time.sleep(0.01)

    start_time = time_between_beatcount = int(round(time.time()*1000))
    print 'Beat number {}, time now: {}'.format(beat_count_period, start_time)

    while not detected_milliseconds:
        # Duration between beats must be greater than or equal to the duration of max BPM in milliseconds
        if int(round(time.time()*1000)) - time_between_beatcount >= 60000 / max_bpm:
            if GPIO.input(gpio) == False:
                time_now = int(round(time.time()*1000))
                beat_count_period += 1

                if first_beat:
                    duration_total = int(round(time.time()*1000)) - time_between_beatcount
                    first_beat = False
                else:
                    duration_total = (int(round(time.time()*1000)) - time_between_beatcount) + duration_total
                if verbose:
                    print 'Beat number {}, Time: {}, Diff: {} ms, Average: {} ms'.format(beat_count_period, time_now, time_now - time_between_beatcount, duration_total / (beat_count_period - 1))

                time_between_beatcount = time_now
                while GPIO.input(gpio) == False:
                    time.sleep(sleep_time)

        if int(round(time.time()*1000)) - start_time > period:
            detected_milliseconds = duration_total / (beat_count_period - 1)
        time.sleep(sleep_time)

    return detected_milliseconds
