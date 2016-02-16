#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# beatcount.py - BPM counter
#

import RPi.GPIO as GPIO
import sys
import time

def beat_counter(verbose, gpio, period, maxbpm):
    sleep_time = 1 / maxbpm # Calculate minimum sleep duration possible to detect the maximum BPM
    debounce_delay = 60000 / maxbpm
    beat_count_bpm = beat_count_period = 1
    duration_average = 0
    first_beat = first_beat_average = True

    # Wait while the button is unpressed
    while GPIO.input(gpio):
        time.sleep(sleep_time)

    while True:
        if first_beat:
            # Wait while the button is unpressed
            while GPIO.input(gpio):
                time.sleep(sleep_time)
            time_between_beats = time_between_beatcount = int(round(time.time()*1000))

        if int(round(time.time()*1000)) - time_between_beatcount < period:
            if first_beat:
                if verbose:
                    print 'Beat {}, Time: {}'.format(beat_count_period, time_between_beats)
                else:
                    print '.',
                    sys.stdout.flush()
                beat_count_period += 1
                first_beat = False
            else:
                time_now = int(round(time.time()*1000))
                if verbose:
                    print 'Beat {}, Time: {}, Diff: {}, Average: {}'.format(beat_count_period, time_now, time_now - time_between_beats, duration_average)
                else:
                    print '.',
                    sys.stdout.flush()
                time_between_beats = time_now
                beat_count_period += 1

        # Wait while the button is pressed
        button_duration = int(round(time.time()*1000))
        while ((GPIO.input(gpio) == False or
               int(round(time.time()*1000)) - button_duration < debounce_delay) and
               int(round(time.time()*1000)) - time_between_beatcount < period):
            time.sleep(sleep_time)

        # Wait while the button is unpressed
        button_duration = int(round(time.time()*1000))
        while ((GPIO.input(gpio) or
                int(round(time.time()*1000)) - button_duration < debounce_delay) and
                int(round(time.time()*1000)) - time_between_beatcount < period):
            time.sleep(sleep_time)

        if int(round(time.time()*1000)) - time_between_beatcount < period:
            if first_beat_average:
                duration_average = int(round(time.time()*1000)) - time_between_beats
                first_beat_average = False
            else:
                duration_average = ((int(round(time.time()*1000)) - time_between_beats) + duration_average) / 2

        if int(round(time.time()*1000)) - time_between_beatcount > period:
            count = beat_count_period - beat_count_bpm
            print 'Done!'
            return count, duration_average
