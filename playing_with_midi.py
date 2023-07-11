#!/usr/bin/env python

import pygame.midi, time, random

pygame.midi.init()

midi_out = pygame.midi.Output(1,0)
midi_out.set_instrument(0)

major_scale = [2,2,1,2,2,2,1]
minor_scale = [2,1,2,2,1,2,2]

starting_note = 65
my_note = starting_note
for i in range(8):
    if i > 0:
        my_note = starting_note + sum(minor_scale[0:i])
    my_velocity = random.randint(80,127)
    midi_out.note_on(my_note,my_velocity)
    time.sleep(random.uniform(0.45,0.55))
    midi_out.note_off(my_note,my_velocity)