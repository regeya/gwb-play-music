#!/usr/bin/env python
# an attempt to write a GW-BASIC-style "play" statement

import pygame
from pygame.locals import *
from pygame.mixer import Sound, get_init, pre_init
import time
import re
import struct
import string
from array import array
from time import sleep

class PlayStatement:
    """an attempt to write a GW-BASIC style PLAY, complete with square-wave audio"""
    bits = 16
    tempo = 120
    a3 = 440
    octave = 3 # default to 3
    sample_rate = 44100
    max_sample = 2**(bits - 1) - 1 # for example, if 16 bits, highest positive number is 2**(15) -1 or 32767
    default_volume = 15
    current_volume = default_volume
    top_amp = 16384
    volumes = [0]*16
    volume_factor = 1 / 10 ** (2/20.0)
    modifier = 0
    stac = False
    notelen = 4
    duration = 0
    major_notes = "cdefgab"
    starting_note = -9
    intervals = [2, 2, 1, 2, 2, 2, 1]
    notes_range={}
    note = starting_note
    statement = ""

    def __init__(self):
        note = self.starting_note
        amp = self.top_amp
        for i, j in zip(self.major_notes, self.intervals):
            self.notes_range[i] = note
            note += j
        for i in range(15,0,-1):
            self.volumes[i] = int(amp)
            amp *= self.volume_factor
        pygame.mixer.pre_init(self.sample_rate, -self.bits, 1)
        pygame.init()
        self.array = []

    def build_samples(self, frequency):
        period = int(round(self.sample_rate / frequency))
        samples = array("h", [0] * period)
        amplitude = 2 ** (15) - 1
        for time in range(period):
            if time < period / 2:
                samples[time] = amplitude
            else:
                samples[time] = -amplitude
        return samples

    def play_note(self, i, sharp):
        frequency = self.a3 * (2 ** ((self.notes_range[i]+self.modifier+sharp)/12.0))
        return self.build_samples(frequency)

    def parse_string(self, play_string):
        tokenized = [f for f in re.findall("([a-z]|[0-9]+|[#+-><])", play_string) if f]
        myarray = []
        for j, i in enumerate(tokenized):
            try:
                k = tokenized[j+1]
            except:
                k = None
            sharp = 0
            if i == ">":
                self.modifier += 12
            elif i == "<":
                self.modifier -= 12
            elif i in ("n", "l"):
                self.stac = False
            elif i == "s":
                self.stac = True
            elif i == "t":
                self.tempo = int(k)
            elif i == "q":
                if int(k) == 1:
                    self.env = 1
                else:
                    self.env = 0
            elif i == "v":
                print(k)
                self.current_vol = int(k)
                self.current_volume = int(k) * self.vol_steps
                print(self.current_volume)
            elif i == "o":
                self.modifier = (int(k) - self.octave) * 12
            elif i == "p":
                if k:
                    self.notelen = int(k)
                    f = 60.0/(self.tempo*(self.notelen/4.0))
                    print(f)
                    time.sleep(f)
            elif i in self.major_notes:
                if k:
                    if k == "#" or k == "+":
                        sharp = 1
                    elif k == "-":
                        sharp = -1
                    elif k.isdigit():
                        self.notelen = int(k)
                x = self.play_note(i, sharp)
                print (i, k)
                sound = pygame.sndarray.make_sound(x)
                sound.play(-1)
                time.sleep(60.0 / (self.tempo * (self.notelen / 4.0)))
                sound.stop()
                self.notelen = 4

    def sound(self):
         self.parse_string(self.statement)

m = ["E8 E8 F8 G8 G8 F8 E8 D8 C8 C8 E8 E8 E8 D12 D4",
     "E8 E8 F8 C8 G8 F8 E8 D8 C8 C8 D8 E8 D8 C12 C4",
     "D8 D8 E8 C8 D8 E12 F12 E8 C8 D8 E12 F12 E8 D8 C8 D8 P8",
     "E8 E8 F8 G8 G8 F8 E8 D8 C8 C8 D8 E8 D8 C12 C4"]

for i in m:
    play = PlayStatement()
    play.statement = i.lower()
    play.sound()
