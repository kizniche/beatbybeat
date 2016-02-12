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
    parser = argparse.ArgumentParser(description='Beat counter (bpm) and Morse code translator')

    beat_counter = parser.add_argument_group('Beat counter controls')
    beat_counter.add_argument('-c', '--count', action='store_true',
                              help="Start program to count beats (bpm)")

    beat_counter.add_argument('-m','--maxbpm', metavar='MAXBPM', type=int,
                              help='Set maximum detectable BPM (lower number improves accuracy, higher numbers may register erroneous taps, below 1000 should be accurate), default: 500',
                              default=500,
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
        print 'Starting mode: Beats per minute (BPM) counter',
    elif args.translate:
        print 'Starting mode: Morse code translator',

    print '(Verbose {})'.format(args.verbose)

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
    #         Start Beat Counter           #
    #                                      #
    ########################################

    if args.count:
        print 'BPM calculation period: {} milliseconds, Max BPM: {} BPM'.format(args.period, args.maxbpm)
        beatcount.beat_counter(args.verbose, args.gpio, args.period, args.maxbpm)

    ########################################
    #                                      #
    #      Start Morse Code Translator     #
    #                                      #
    ########################################

    if args.translate:
        print 'BPM calculation period: {} milliseconds, Max BPM: {} BPM'.format(args.period, args.maxbpm)
        translate.morse_translator(args.verbose, args.gpio, args.period, args.maxbpm)


if __name__ == "__main__":
    menu()
    sys.exit(0)
