#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# beatcount.py - BPM counter
#

import RPi.GPIO as GPIO
import time

def beat_counter(verbose, gpio, period, max_bpm):
    sleep_time = 1 / max_bpm # Calculate minimum sleep duration possible to detect the maximum BPM
    beat_count_bpm = beat_count_period = 1
    duration_average = 0
    first_beat = first_beat_average = True

    print '\nBegin tapping a tempo to identify the duration between beats.', \
          '\nCalculations will only be performed while there is tapping.', \
          '\nTiming will begin upon the first buttom press and be measured every {} milliseconds.\n'.format(period)

    while True:
        if first_beat:
            # Wait until the button is pressed for the first time
            while GPIO.input(gpio):
                time.sleep(0.01)

            time_between_beats = time_between_beatcount = int(round(time.time()*1000))

            print 'Beat number {}, time now: {}'.format(beat_count_period, time_between_beats)
            beat_count_period += 1
            first_beat = False

        # Duration between beats must be greater than or equal to the duration of max BPM in milliseconds
        if int(round(time.time()*1000)) - time_between_beats >= 60000 / max_bpm:
            if GPIO.input(gpio) == False:
                time_now = int(round(time.time()*1000))

                if first_beat_average:
                    duration_average = int(round(time.time()*1000)) - time_between_beatcount
                    first_beat_average = False
                else:
                    duration_average = ((int(round(time.time()*1000)) - time_between_beats) + duration_average) / 2
                if verbose:
                    print 'Beat number {}, time now: {}, time diff: {}, Average: {}'.format(beat_count_period, time_now, time_now - time_between_beats, duration_average)

                time_between_beats = time_now
                beat_count_period += 1
                while GPIO.input(gpio) == False:
                    time.sleep(sleep_time)

        if int(round(time.time()*1000)) - time_between_beatcount > period:
            count = beat_count_period - beat_count_bpm
            print '\nCalculated from total number of beats over time: {} beats per {} ms = {} BPM'.format(count, period, count * (60 / (period / 1000)))
            if duration_average:
                print 'Calculated from average duration between beats: {} ms per beat = {} BPM\n'.format(duration_average, 60000 / duration_average)
            else:
                print ''
            time_between_beatcount = int(round(time.time()*1000))
            beat_count_bpm = beat_count_period = 1
            duration_average = 0
            first_beat = first_beat_average = True

        time.sleep(sleep_time)
