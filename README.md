# BeatByBeat

Python BPM counter and Morse code translator, for use with a telegraph (push-button) connected to a Raspberry Pi.

<a href="http://kylegabriel.com/projects/wp-content/uploads/sites/3/2016/02/beatbybeat-Morse-code-translator-04.png" target="_blank"><img src="http://kylegabriel.com/projects/wp-content/uploads/sites/3/2016/02/beatbybeat-Morse-code-translator-04.png"></a>

### Morse Code

Each Morse code symbol represents a character (A-Z, 0-9) and is represented by a unique sequence of dots and dashes. The duration of a dash is three times the duration of a dot. Each dot or dash is followed by a short silence, equal to the dot duration. Characters are separated by a space equal to three dots (one dash) and words are separated by a space equal to seven dots.

A calibration is required to determine the duration of a dash (and for the space between letters). All other durations are calculated from this duration, and an error is applied to produce acceptable ranges for a button is pressed and when the button is not pressed.

### Wiring Schematic

[Raspberry Pi GROUND] ----- [Telegraph or Push-Button] ----- [Rapsberry Pi GPIO]

### Command Line Options

./beatbybeat --help
