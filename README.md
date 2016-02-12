# BeatByBeat

Python BPM counter and Morse code translator, for use with a telegraph (push-button) connected to a Raspberry Pi.

### Wiring schematic

[Raspberry Pi GROUND] ----- [Telegraph or Push-Button] ----- [Rapsberry Pi GPIO]

### Command line options

./beatbybeat --help

### Morse Code

Each Morse code symbol represents either a text character (letter or numeral) or a prosign and is represented by a unique sequence of dots and dashes. The duration of a dash is three times the duration of a dot. Each dot or dash is followed by a short silence, equal to the dot duration. The letters of a word are separated by a space equal to three dots (one dash), and the words are separated by a space equal to seven dots.
