#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# beatbybeat - beat counter and translator
#

import getopt
import RPi.GPIO as GPIO
import sys
import time

global_bpm_period_milliseconds = 5000

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Displays the program usage
def usage():
    print "beatbybeat.py: beat counter and translator"
    print "               Run as root.\n"
    print "Usage:  beatbybeat.py [OPTION]...\n"
    print "Options:"
    print "    -h, --help"
    print "           Display this help and exit"
    print "    -m, --max-bpm"
    print "           Set maximum BPM (lower number improves accuracy), default: 700"
    print "    -p, --period"
    print "           Period of time between BPM calculations (milliseconds), default: 5000"
    print "    -v, --verbose"
    print "           enables log output to the console\n"
    print "Examples: beatbybeat.py"
    print "          beatbybeat.py -m 1000 -p 3000"
    print "          beatbybeat.py -v\n"

def menu():
    max_bpm = 700
    bpm_period_milliseconds = 5000
    verbose = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hm:p:v', ["help", "max-bpm=", "period=", "verbose"])
    except getopt.GetoptError as err:
        print(err)  # will print "option -a not recognized"
        usage()
        return 2
    for opt, arg in opts:
        if opt in ("-h", "--help"):
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
    print 'BPM calculation period: {} milliseconds, max BPM: {} bpm, verbose: {}'.format(bpm_period_milliseconds, max_bpm, verbose)
    beat_counter(verbose, bpm_period_milliseconds, max_bpm)
    return 1

def beat_counter(verbose, bpm_period_milliseconds, max_bpm):
    beat_count_bpm = beat_count_total = beat_count_period = 0
    time_between_beats = time_between_beatcount = int(round(time.time()*1000))
    while True:
        if int(round(time.time()*1000)) - time_between_beats > 20:
            if GPIO.input(23) == False:
                time_now = int(round(time.time()*1000))
                if verbose:
                    print 'Beat {} Now: {} Diff: {}'.format(beat_count_period, time_now, time_now - time_between_beats)
                time_between_beats = time_now
                beat_count_period += 1

                while GPIO.input(23) == False:
                    time.sleep(0.0005)

        if int(round(time.time()*1000)) - time_between_beatcount > bpm_period_milliseconds:
            bpm_count(beat_count_period - beat_count_bpm, bpm_period_milliseconds)
            time_between_beatcount = int(round(time.time()*1000))
            beat_count_bpm = beat_count_period

        time.sleep(0.0005)

def bpm_count(count, bpm_period_milliseconds):
    print '{} ounts per {} seconds, BPM: {}'.format(count, bpm_period_milliseconds / 1000, count * (60 / (bpm_period_milliseconds / 1000)))

menu()
