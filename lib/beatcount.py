#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# beatcount.py - BPM counter
#

import RPi.GPIO as GPIO
import time

def beat_counter(gpio_pin, verbose, bpm_period_milliseconds, max_bpm):
    sleep_time = 1 / max_bpm # Calculate minimum sleep duration possible to detect the maximum BPM
    beat_count_bpm = beat_count_total = beat_count_period = 0
    time_between_beats = time_between_beatcount = int(round(time.time()*1000))
    while True:
        # Duration between beats must be greater than or equal to the duration of max BPM in milliseconds
        if int(round(time.time()*1000)) - time_between_beats >= 60000 / max_bpm:
            if GPIO.input(gpio_pin) == False:
                time_now = int(round(time.time()*1000))
                if verbose:
                    print 'Beat: {}, time now: {}, time diff: {}'.format(beat_count_period, time_now, time_now - time_between_beats)
                time_between_beats = time_now
                beat_count_period += 1
                while GPIO.input(gpio_pin) == False:
                    time.sleep(sleep_time)
        if int(round(time.time()*1000)) - time_between_beatcount > bpm_period_milliseconds:
            bpm_count(beat_count_period - beat_count_bpm, bpm_period_milliseconds)
            time_between_beatcount = int(round(time.time()*1000))
            beat_count_bpm = beat_count_period
        time.sleep(sleep_time)


# Calculate BPM from number of beats over a period of time
def bpm_count(count, bpm_period_milliseconds):
    print '{} beats per {} seconds = {} BPM'.format(count, bpm_period_milliseconds / 1000, count * (60 / (bpm_period_milliseconds / 1000)))
