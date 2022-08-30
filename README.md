# vocal\_melody

Generate CSV or MIDI file of vocal melody for karaoke system.

## input CSV file records

`timestamp, frequency`

`timestamp` is in seconds, and `frequency` is in Hz.
This format is the output format of [MELODIA](https://www.upf.edu/web/mtg/melodia).

## output CSV file records

`pitch, start, end`

`pitch` is MIDI note number, `start` and `end` is in seconds.

