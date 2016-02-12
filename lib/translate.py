#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# translate.py - Morse code translator
#

import RPi.GPIO as GPIO
import time

def morse_translator(verbose, gpio, period, max_bpm):
    print '\nA tempo needs to be set to determine to the duration of spaces, dashes, and dots.', \
          '\nTap a tempo to identify the duration between letters (spaces).', \
          '\nTiming will begin upon the first buttom press and be measured for {} milliseconds.\n'.format(period)
    
    milliseconds_space_dash = detect_bpm(verbose, gpio, period, max_bpm)
    milliseconds_dot = milliseconds_space_dash / 3
    print '\nTempo acquired (ms = milliseconds, BPM = beats per minute):'
    print 'Space: {} ms ({} BPM)'.format(milliseconds_space_dash, 60000 / milliseconds_space_dash)
    print 'Dash: {} ms ({} BPM)'.format(milliseconds_space_dash, 60000 / milliseconds_space_dash)
    print 'Dot: {} ms ({} BPM)'.format(milliseconds_dot, 60000 / milliseconds_dot)
    print '\nWait 5 seconds before beginning Morse code...\n'
    time.sleep(5)
    
    print 'Morse code translation will begin when you make your first .', \
          '\nA new letter will begin to be interpreted when the duration between taps is greater than or equal to {} ms ({} BPM).\n'.format(milliseconds_space_dash, 60000 / milliseconds_space_dash)


def detect_bpm(verbose, gpio, period, max_bpm):
    sleep_time = 1 / max_bpm  # Calculate minimum sleep duration possible to detect the maximum BPM
    beat_count_period = 1
    duration_average = 0
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
                    duration_average = int(round(time.time()*1000)) - time_between_beatcount
                    first_beat = False
                else:
                    duration_average = ((int(round(time.time()*1000)) - time_between_beatcount) + duration_average) / 2
                if verbose:
                    print 'Beat number {}, time now: {}, time diff: {}, Average: {}'.format(beat_count_period, time_now, time_now - time_between_beatcount, duration_average)

                time_between_beatcount = time_now
                beat_count_period += 1
                while GPIO.input(gpio) == False:
                    time.sleep(sleep_time)

        if int(round(time.time()*1000)) - start_time > period:
            detected_milliseconds = duration_average
        time.sleep(sleep_time)

    return detected_milliseconds
