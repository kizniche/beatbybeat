#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# translate.py - Morse code translator
#

import RPi.GPIO as GPIO
import time

def morse_translator(verbose, gpio, period, max_bpm):
    print '\nA tempo needs to be set to determine the duration of dashes and dots and between words and letters.', \
          '\nBegin tapping a tempo to set the duration between letters.', \
          '\nTiming will begin upon the first buttom press and be measured for {} milliseconds.\n'.format(period)
    
    milliseconds_space_dash = detect_bpm(verbose, gpio, period, max_bpm)
    milliseconds_dot = milliseconds_space_dash / 3
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
    beat_count_period += 1

    while not detected_milliseconds:
        # Duration between beats must be greater than or equal to the duration of max BPM in milliseconds
        if int(round(time.time()*1000)) - time_between_beatcount >= 60000 / max_bpm:
            if GPIO.input(gpio) == False:
                time_now = int(round(time.time()*1000))

                if first_beat:
                    duration_total = int(round(time.time()*1000)) - time_between_beatcount
                    first_beat = False
                else:
                    duration_total = (int(round(time.time()*1000)) - time_between_beatcount) + duration_total
                if verbose:
                    print 'Beat number {}, Time: {}, Diff: {} ms, Average: {} ms'.format(beat_count_period, time_now, time_now - time_between_beatcount, duration_total / (beat_count_period - 1))

                time_between_beatcount = time_now
                beat_count_period += 1
                while GPIO.input(gpio) == False:
                    time.sleep(sleep_time)

        if int(round(time.time()*1000)) - start_time > period:
            detected_milliseconds = duration_total / (beat_count_period - 2)
        time.sleep(sleep_time)

    return detected_milliseconds
