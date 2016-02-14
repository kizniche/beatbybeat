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

    beat_counter = parser.add_argument_group('Beat counter')
    beat_counter.add_argument('-b', '--bpmcount', action='store_true',
                              help="Start program to count beats (bpm)")

    beat_counter.add_argument('-m','--maxbpm', metavar='MAXBPM', type=int,
                              help='Set maximum detectable BPM (lower number improves accuracy, higher numbers may register erroneous taps, below 1000 should be accurate), default: 800',
                              default=800,
                              required=False)

    beat_counter.add_argument('-p','--period', metavar='PERIOD', type=int,
                              help='Period of time between BPM calculations (milliseconds), default: 5000',
                              default=5000,
                              required=False)

    morse_translator = parser.add_argument_group('Morse code translator')
    morse_translator.add_argument('-mt', '--morsetotext', action='store_true',
                              help="Translate Morse code to text")

    morse_translator.add_argument('-tm', '--texttomorse', action='store_true',
                              help="Translate text to Morse code")

    misc_options = parser.add_argument_group('Miscelaneous')
    misc_options.add_argument('-g','--gpio', metavar='GPIO', type=int,
                              help='GPIO pin connected to the telegraph (using BCM numbering)')

    misc_options.add_argument('-v', '--verbose', action='store_true',
                              help="Print more information to the terminal")

    args = parser.parse_args()

    ########################################
    #                                      #
    #           Setup Options              #
    #                                      #
    ########################################

    if not (args.bpmcount or args.morsetotext or args.texttomorse):
        parser.error('No action requested, add --bpmcount or --morsetotext or --texttomorse')
    elif sum(map(bool, [args.bpmcount, args.morsetotext, args.texttomorse])) != 1:
        parser.error('Can only select one: --bpmcount (-b), --morsetotext (-mt), or --texttomorse (-tm)')
    elif args.bpmcount:
        if not args.gpio:
            parser.error('Need to specify GPIO pin with --gpio')
        else:
            print 'Beats per minute (BPM) counter',
    elif args.morsetotext:
        if not args.gpio:
            parser.error('Need to specify GPIO pin with --gpio')
        else:
            print 'Morse code to text translator',
    elif args.texttomorse:
        print 'Text to Morse code translator (use only A-Z, 0-9, spaces, and symbols /?\'!@$&()_-+=,.;:")',

    if args.verbose:
        print '(Verbose)'
    else:
        print ''

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
    #             Beat Counter             #
    #                                      #
    ########################################

    if args.bpmcount:
        print 'Tempo calculation period: {} milliseconds, Max BPM: {} BPM'.format(args.period, args.maxbpm)
        beatcount.beat_counter(args.verbose, args.gpio, args.period, args.maxbpm)

    ########################################
    #                                      #
    #    Morse Code to Text Translator     #
    #                                      #
    ########################################

    if args.morsetotext:
        print 'Tempo calculation period: {} milliseconds, Max BPM: {} BPM'.format(args.period, args.maxbpm)
        translate.morse_to_text(args.verbose, args.gpio, args.period, args.maxbpm)

    ########################################
    #                                      #
    #    Text to Morse Code Translator     #
    #                                      #
    ########################################

    if args.texttomorse:
        translate.text_to_morse()


if __name__ == "__main__":
    menu()
    sys.exit(0)
