import librosa
import argparse
import pretty_midi
import math
import numpy as np
from typing import List
from itertools import groupby


class Note:
    def __init__(self, pitch, start, end):
        self.pitch = pitch
        self.start = start
        self.end = end

    def duration(self):
        return self.end - self.start

    def __str__(self):
        return f'{self.pitch},{self.start},{self.end}'


parser = argparse.ArgumentParser()
short_sound_group = parser.add_mutually_exclusive_group()
parser.add_argument('input', type=str)
parser.add_argument(
    '--min_freq', help='minimum frequency to output', default=250, type=int)
parser.add_argument(
    '--max_freq', help='maximum frequency to output', default=700, type=int)
short_sound_group.add_argument(
    '--drop', help='the sound shorter than this value in second will be dropped',
    default=None, type=float)
short_sound_group.add_argument(
    '--merge', help='the sound shorter than this value in second will be merged to adjecent sound',
    default=None, type=float)
parser.add_argument('-o', '--output_csv', help='output CSV file name',
                    default='out.csv', type=str)
parser.add_argument('--output_midi', help='output MIDI file name',
                    default=None, type=str)

args = parser.parse_args()

# parse file
f0: List[float] = []
times: List[float] = []
with open(args.input, 'r') as f:
    for line in f:
        line = line.strip()
        time, hz = line.split(',')
        hz = float(hz)
        if (args.min_freq < hz) and (hz < args.max_freq):
            f0.append(hz)
            times.append(float(time))
        else:
            f0.append(np.nan)
            times.append(float(time))
f0 = np.array(f0)

# create Note with time information
midi_list = np.round(librosa.hz_to_midi(f0))
note_list: List[Note] = []
start = 0
last_note = 0
for m, t in zip(midi_list, times):
    if math.isnan(m):
        if not math.isnan(last_note):
            note_list.append(Note(last_note, start, t))
        last_note = math.nan
    elif m != last_note:
        if not math.isnan(last_note) > 0:
            note_list.append(Note(last_note, start, t))
        start = t
        last_note = m

# drop short sound
if args.drop is not None:
    new_note_list = []
    for note in note_list:
        if note.duration() >= args.drop:
            new_note_list.append(note)
    note_list = new_note_list

# merge short sound
if args.merge is not None:
    new_note_list = []
    for i, note in enumerate(note_list):
        if note.duration() <= args.merge:
            if i == len(note_list) - 1:
                continue
            next_note = note_list[i+1]
            if next_note.start == note.end:
                next_note.start = note.start
        else:
            new_note_list.append(note)
    note_list = new_note_list

# generate CSV file
with open(args.output_csv, mode='w') as fp:
    for note in note_list:
        fp.write(str(note) + '\n')

# generate MIDI file
if args.output_midi is not None:
    midi = pretty_midi.PrettyMIDI()
    piano_program = pretty_midi.instrument_name_to_program('Electric Piano 1')
    piano = pretty_midi.Instrument(program=piano_program)
    for note in note_list:
        print(
            f'pitch: {note.pitch}, start: {note.start}, length: {note.duration()}')
        midi_note = pretty_midi.Note(
            velocity=100, pitch=int(note.pitch), start=note.start, end=note.end)
        piano.notes.append(midi_note)
    
    midi.instruments.append(piano)
    midi.write(args.output_csv)
