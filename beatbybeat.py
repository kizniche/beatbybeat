#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# beatbybeat.py - BPM counter and Morse code translator
#

import getopt
import RPi.GPIO as GPIO
import sys
import time

# Displays the program usage
def usage():
    print "beatbybeat.py: beat counter and translator"
    print "               Run as root.\n"
    print "Usage:  beatbybeat.py [OPTION]...\n"
    print "Options:"
    print "    -g, --gpio [pin]"
    print "           Pin connected to the telegraph (using BCM numbering), default: 23"
    print "    -h, --help"
    print "           Display this help and exit"
    print "    -m, --max-bpm [bpm]"
    print "           Set maximum detectable BPM (lower number improves accuracy, below 2000 should be accurate), default: 1200"
    print "    -p, --period [period]"
    print "           Period of time between BPM calculations (milliseconds), default: 5000"
    print "    -v, --verbose"
    print "           Output each button press to the console\n"
    print "Examples: beatbybeat.py"
    print "          beatbybeat.py -m 1000 -p 3000"
    print "          beatbybeat.py -v\n"

def menu():
    max_bpm = 1200
    bpm_period_milliseconds = 5000
    verbose = False
    gpio_pin = 23
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'g:hm:p:v', ["gpio=", "help", "max-bpm=", "period=", "verbose"])
    except getopt.GetoptError as err:
        print(err)  # will print "option -a not recognized"
        usage()
        return 2
    for opt, arg in opts:
        if opt in ("-g", "--gpio"):
            gpio_pin = arg
        elif opt in ("-h", "--help"):
            usage()
            return 0
        elif opt in ("-m", "--max-bpm"):
            max_bpm = arg
        elif opt in ("-p", "--period"):
            bpm_period_milliseconds = arg
        elif opt in ("-v", "--verbose"):
            verbose = True
        else:
            assert False, "Fail"
    print 'BPM calculation period: {} milliseconds, max: {} BPM, verbose: {}'.format(bpm_period_milliseconds, max_bpm, verbose)
    beat_counter(gpio_pin, verbose, bpm_period_milliseconds, max_bpm)
    return 1

# Count the number of beats
def beat_counter(gpio_pin, verbose, bpm_period_milliseconds, max_bpm):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
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

menu()
