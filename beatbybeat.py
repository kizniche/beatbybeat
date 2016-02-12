#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# beatbybeat.py - BPM counter and Morse code translator
#

from lib import beatcount
from lib import translate
import argparse
import RPi.GPIO as GPIO
import sys


def menu():
    # max_bpm = 1200
    # bpm_period_milliseconds = 5000
    # verbose = False
    # gpio_pin = 23

    parser = argparse.ArgumentParser(description='Beat counter (bpm) and Morse code translator')

    beat_counter = parser.add_argument_group('Beat counter controls')
    beat_counter.add_argument('-c', '--count', action='store_true',
                              help="Start program to count beats (bpm)")

    beat_counter.add_argument('-m','--maxbpm', metavar='MAXBPM', type=int,
                              help='Set maximum detectable BPM (lower number improves accuracy, below 2000 should be accurate), default: 1200',
                              default=2000,
                              required=False)

    beat_counter.add_argument('-p','--period', metavar='PERIOD', type=int,
                              help='Period of time between BPM calculations (milliseconds), default: 5000',
                              default=5000,
                              required=False)

    morse_translator = parser.add_argument_group('Beat counter controls')
    morse_translator.add_argument('-t', '--translate', action='store_true',
                              help="Start program to translate Morse code")


    misc_options = parser.add_argument_group('Misc.')
    misc_options.add_argument('-g','--gpio', metavar='GPIO', type=int,
                              help='Pin connected to the telegraph (using BCM numbering)',
                              required=True)

    misc_options.add_argument('-v', '--verbose', action='store_true',
                              help="Print more information to the terminal")

    args = parser.parse_args()

    ########################################
    #                                      #
    #           Setup Options              #
    #                                      #
    ########################################

    if not (args.count or args.translate):
        parser.error('No action requested, add --count or --translate')
    elif args.count and args.translate:
        parser.error('Cannot select both --count and --translate, only select one')
    elif args.count:
        print 'Starting mode: Beats per minute (BPM) counter'
    elif args.translate:
        print 'Starting mode: Morse code translator'

    if args.verbose:
        print 'Verbose enabled'

    ########################################
    #                                      #
    #             Setup GPIO               #
    #                                      #
    ########################################

    if args.gpio:
        print 'Setting up GPIO {}:'.format(args.gpio),
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(args.gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        except:
            print 'Fail'
        else:
            print 'Success'

    ########################################
    #                                      #
    #        Beat Counter Options          #
    #                                      #
    ########################################

    if args.count:
        max_bpm = args.maxbpm
        period = args.period
        print 'BPM calculation period: {} milliseconds, Max BPM: {} BPM'.format(period, max_bpm)
        beatcount.beat_counter(args.gpio, args.verbose, period, max_bpm)

    ########################################
    #                                      #
    #    Morse Code Translator Options     #
    #                                      #
    ########################################

    if args.translate:
        translate.morse_translator()


if __name__ == "__main__":
    menu()
    sys.exit(0)
