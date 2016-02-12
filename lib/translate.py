#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# translate.py - Morse code translator
#

import RPi.GPIO as GPIO
import time

def morse_translator(verbose, gpio, period, max_bpm):
    print '\nTap a tempo to identify the duration between letters (spaces).', \
          'Timing will begin upon the first buttom press and be measured for 5 seconds.\n'
    
    miliseconds_space = detect_bpm(verbose, gpio, period, max_bpm)
    print '\nDetected rates (ms = milliseconds): Space: {} ms ({} BPM), Dash: {} ms ({} BPM), Dot: {} ms ({} BPM)'.format(
            miliseconds_space, 60000 / miliseconds_space,
            miliseconds_space * 2 / 3, 60000 / (miliseconds_space * 2 / 3),
            miliseconds_space / 3, 60000 / (miliseconds_space / 3))
    print 'Stop tapping and wait 5 seconds before beginning Morse code...\n'
    time.sleep(5)
    
    print 'Begin Morse code and translation will take place automatically.', \
          'A new letter will begin to be interpreted if the duration between taps is equal to or longer then {} ms ({} BPM).\n'.format(miliseconds_space, 60000 / miliseconds_space)


def detect_bpm(verbose, gpio, period, max_bpm):
    sleep_time = 1 / max_bpm # Calculate minimum sleep duration possible to detect the maximum BPM
    beat_count_period = 0
    duration_average = 0
    first_beat = True

    # Wait until the button is pressed for the first time
    while GPIO.input(gpio):
        time.sleep(0.01)

    start_time = time_between_beatcount = int(round(time.time()*1000))
    end_time = 0
    detected_milliseconds = 0
    print 'Beat number {}, time now: {}'.format(beat_count_period, start_time)
    beat_count_period += 1

    while not detected_milliseconds:
        # Duration between beats must be greater than or equal to the duration of max BPM in milliseconds
        if int(round(time.time()*1000)) - time_between_beatcount >= 60000 / max_bpm:
            if GPIO.input(gpio) == False:
                time_now = int(round(time.time()*1000))
                if verbose:
                    print 'Beat number {}, time now: {}, time diff: {}'.format(beat_count_period, time_now, time_now - time_between_beatcount)

                if first_beat:
                    duration_average = int(round(time.time()*1000)) - time_between_beatcount
                    first_beat = False
                else:
                    duration_average = ((int(round(time.time()*1000)) - time_between_beatcount) + duration_average) / 2
                print 'Average: {}'.format(duration_average)

                time_between_beatcount = time_now
                beat_count_period += 1
                while GPIO.input(gpio) == False:
                    time.sleep(sleep_time)
        if int(round(time.time()*1000)) - start_time > period:
            detected_milliseconds = duration_average
        time.sleep(sleep_time)

    return detected_milliseconds
