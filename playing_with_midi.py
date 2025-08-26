#!/usr/bin/env python

import pygame.midi, time, random

pygame.midi.init()

midi_out = pygame.midi.Output(2,0)
midi_out.set_instrument(0)

major_scale = [2,2,1,2,2,2,1]
minor_scale = [2,1,2,2,1,2,2]

starting_note = 60
#my_note = starting_note
#for i in range(8):
#    if i > 0:
#        my_note = starting_note + sum(mino_scale[0:i])
#    my_velocity = random.randint(80,127)
#    midi_out.note_on(my_note,my_velocity)
#    time.sleep(random.uniform(0.45,0.55))
#    midi_out.note_off(my_note,my_velocity)

my_str = "O3MBT120L8C+DEFGAB>C"

sharps = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
flats = ['C', 'D-', 'D', 'E-', 'E', 'F', 'G-', 'G', 'A-', 'A', 'B-', 'B']
all_notes = sharps + flats
midi_notes = list(range(60, 72))

notes = {k: v for k, v in zip(sharps, midi_notes)}
notes.update({k: v for k, v in zip(flats, midi_notes)})

def build_list(my_str):
    mylist = []
    mynum = []
    for i in my_str:
        if i.isdigit():
            mynum.append(i)
        elif i == "#" or i == "+":
            mylist[-1] = mylist[-1] + "#"
        elif i == "-":
            mylist[-1] = mylist[-1] + "-"
        elif mylist and mylist[-1] == "M":
            mylist[-1] = mylist[-1] + i
        else:
            if mynum:
                mylist.append("".join(mynum))
                mynum = []
            mylist.append(i)
    return mylist

notes_to_parse = build_list(my_str)

for i in ['C','D','E', 'F','G','A','B']:
    mynote = notes[i]
    midi_out.note_on(mynote, 96)
    time.sleep(1)
    midi_out.note_off(mynote, 96)
