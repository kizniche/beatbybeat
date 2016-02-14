# BeatByBeat

Python BPM counter and Morse code translator, for use with a telegraph (push-button) connected to a Raspberry Pi.

### Morse Code

Each Morse code symbol represents a character (A-Z, 0-9, symbols, and prosigns) and is represented by a unique sequence of dots and dashes. The duration of a dash is three times the duration of a dot. Each dot or dash is followed by a short silence, equal to the dot duration. Characters are separated by a space equal to three dots (one dash) and words are separated by a space equal to seven dots.

A calibration is required to determine the duration of a dash (and for the space between letters). All other durations are calculated from this duration, and an error is applied to produce acceptable ranges for a button is pressed and when the button is not pressed.

### Features

* Translate from Morse code to text (requires input device)
* Calculate beats per minute from tapping (requires input device)
* Translate from text to Morse code
* Calculate how long it would take to transmit Morse code from the input text

### Screenshots

Morse code to text (from telegraph as an input device):
<a href="http://kylegabriel.com/projects/wp-content/uploads/sites/3/2016/02/beatbybeat-Morse-code-translator-04.png" target="_blank"><img src="http://kylegabriel.com/projects/wp-content/uploads/sites/3/2016/02/beatbybeat-Morse-code-translator-04.png"></a>

Text to Morse code:
<a href="http://kylegabriel.com/projects/wp-content/uploads/sites/3/2016/02/beatbybeat-Morse-code-translator-06.png" target="_blank"><img src="http://kylegabriel.com/projects/wp-content/uploads/sites/3/2016/02/beatbybeat-Morse-code-translator-06.png"></a>

### Wiring Schematic

[Raspberry Pi GROUND] ----- [Telegraph or Push-Button] ----- [Rapsberry Pi GPIO]

Connect a capacitor to each lead of the button to lessen button bounce (debounce).
An internal pullup resistor is activated in software, but another resistor (10k should be sufficient) may be connected in series to prevent excess current from damaging your device, should the internal reisistor fail to activate.

### Command Line Options

./beatbybeat --help
