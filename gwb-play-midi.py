#!/usr/bin/env python
# an attempt to write a GW-BASIC-style "play" statement

import pygame
import re
from array import array
from time import sleep
from datetime import datetime
from pygame.locals import *
from pygame.mixer import Sound, get_init, pre_init
from collections import deque


class Note(Sound):
    def __init__(self, frequency, volume=0.1):
        self.frequency = frequency
        Sound.__init__(self, self.build_samples())
        self.set_volume(volume)

    def build_samples(self):
        period = int(round(get_init()[0] / self.frequency))
        samples = array("h", [0] * period)
        amplitude = 2 ** (abs(get_init()[1]) - 1) - 1
        for time in range(period):
            if time < period / 2:
                samples[time] = amplitude
            else:
                samples[time] = -amplitude
        return samples


class PlayStatement:
    """an attempt to write a GW-BASIC style PLAY, complete with square-wave audio"""

    bits = 16
    tempo = 120
    a4 = 1760
    octave = 4  # default to 4
    sample_rate = 44100
    max_sample = (
        2 ** (bits - 1) - 1
    )  # for example, if 16 bits, highest positive number is 2**(15) -1 or 32767
    default_volume = 9
    top_amp = int(max_sample)
    volumes = [0] * 16
    volume_factor = 1 / 10 ** (2 / 20.0)
    note_dur = 7 / 8.0
    modifier = 0
    default_notelen = 4
    current_notelen = default_notelen
    notelen = current_notelen
    duration = 0
    major_notes = "cdefgab"
    starting_note = -9
    intervals = [2, 2, 1, 2, 2, 2, 1]
    notes_range = {}
    note = starting_note
    statement = ""
    mybuffer = []

    def __init__(self):
        self.channel = 0
        note = self.starting_note
        amp = self.top_amp
        for i, j in zip(self.major_notes, self.intervals):
            self.notes_range[i] = note
            note += j
        for i in range(15, 0, -1):
            self.volumes[i] = int(amp)
            amp *= self.volume_factor
        self.current_volume = self.volumes[self.default_volume]
        pygame.mixer.init(
            frequency=self.sample_rate, size=-self.bits, channels=1, allowedchanges=0
        )
        self.array = []

    def build_samples(self, frequency):
        period = int(self.sample_rate / frequency)
        samples = array("h", [0] * period)
        amplitude = self.current_volume
        for time in range(period):
            if time < period / 2:
                samples[time] = amplitude
            else:
                samples[time] = -amplitude
        return samples

    def play_note(self, i, sharp):
        frequency = self.a4 * (
            2 ** ((self.notes_range[i] + self.modifier + sharp) / 12.0)
        )
        return self.build_samples(frequency)

    def parse_string(self, play_string):
        self.mybuffer = []
        timecode = 0
        split_str = [f for f in re.findall("([a-z]|[0-9]+|[#+-><])", play_string) if f]
        myarray = []
        for i, j in zip(split_str, split_str[1:]):
            sharp = 0
            if i == ">":
                self.modifier += 12
            if i == "l":
                if j.isdigit():
                    self.current_notelen = int(j)
            elif i == "<":
                self.modifier -= 12
            elif i == "m":
                if j == "l":
                    self.note_dur = 1.0
                elif j == "n":
                    self.note_dur = 0.875
                elif j == "s":
                    self.note_dur = 0.75
            elif i == "t":
                self.tempo = int(j)
            elif i == "q":
                if int(j) == 1:
                    self.env = 1
                else:
                    self.env = 0
            elif i == "v":
                if int(j) > 9:
                    self.current_volume = self.volumes[9]
                else:
                    self.current_volume = self.volumes[int(j)]
            elif i == "o":
                self.modifier = (int(j) - self.octave) * 12
            elif i == "p":
                if j:
                    self.notelen = int(j)
                    f = 60.0 / (self.tempo * (self.notelen / 4.0))
                    self.mybuffer.append(
                        [
                            self.channel,
                            0,
                            self.current_volume,
                            int((timecode + f) * 1000),
                        ]
                    )
                    timecode += f
            elif i in self.major_notes:
                dotted = False
                try:
                    print(tokenized, i, j)
                    if j:
                        if j == "#" or j == "+":
                            sharp = 1
                        elif j == "-":
                            sharp = -1
                        elif j.isdigit():
                            self.notelen = int(j)
                except:
                    print("Queue exhausted and so am I")
                try:
                    if j == ".":
                        dotted = True
                except:
                    print("disconnect the dots")
                frequency = self.a4 * (
                    2 ** ((self.notes_range[i] + self.modifier + sharp) / 12.0)
                )
                self.mybuffer.append(
                    [self.channel, frequency, self.current_volume, int(timecode * 1000)]
                )
                my_duration = 60.0 / (self.tempo * (self.notelen / 4.0))
                if dotted:
                    my_duration = my_duration * (3 / 2.0)
                cur_duration = my_duration * self.note_dur
                cur_pause = my_duration - cur_duration
                timecode += cur_duration
                self.mybuffer.append(
                    [self.channel, 0, self.current_volume, int(timecode * 1000)]
                )
                timecode += cur_pause
            self.notelen = self.current_notelen

    def sound(self):
        self.parse_string(self.statement)
        return self.mybuffer


# m = ["o2l6p6p6go3el12p12dl6ecl3fl12fl24edl12eagal6dl3gl12gl24fel12fco2bo3f",
#     "o2l6p6p6p6p6p6cal12p12gl6ago3l3cl12cl24o2bal12bo3edel6o2al3o3d",
#     "o1l1ccc"]

# music = ["o4 e-8 p8","o3 <b-16 a-16 b-16 >d-16","o2 <g8 >e-8"]

# lines = [["mb","mb","mb"],
# ["v11 t120 o3 e-8 >e-8","v12 t120 o2 p4","v12 t120 o2 e-4"],
# ["o4 <f8 >e-8","o2 p4","o2 e-4"],
# ["o4 <g8 >e-8","o2 p4","o2 p4"],
# ["o4 <a-8 >e-8","o2 p4","o2 c4"],
# ["o4 <b-8 >e-8","o2 p4","o2 c4"],
# ["o4 c8 e-8","o2 p4","o2 p4"],
# ["o4 <b-16 >e-16 d16 c16","o2 p4","o1 g4"],
# ["o4 <b-16 >g16 f16 e-16","o2 p4","o1 a-4"],
# ["o4 d16 c16 <b-16 a-16","o2 p4","o1 b-4"],
# ["o3 g16 a-16 b-16 g16","o2 p4","o1 e-4"],
# ["o3 e-16 g16 b-16 >e-16","o2 p4","o1 g4"],
# ["o4 <f16 a16 >c16 e-16","o2 p4","o1 a4"],
# ["o4 d16 c16 d16 f16","o2 b-8 >b-8","o1 b-4"],
# ["o4 e-16 d16 e-16 g16","o3 c8 b-8","o1 b-4"],
# ["o4 f16 e-16 f16 a-16","o3 d8 b-8","o1 p4"],
# ["o4 g16 f16 g16 b-16","o3 e-8 b-8","o1 b-4"],
# ["o4 d16 c16 d16 b-16","o3 f8 b-8","o1 b-4"],
# ["o4 e-16 d16 e-16 b-16","o3 g8 b-8","o1 p4"],
# ["o4 d8 f8","o3 f16 b-16 a16 g16","o1 b-4"],
# ["o4 b-8 d8","o3 f16 >d16 c16 <b-16","o1 >d4"],
# ["o4 c8 a8","o3 a16 g16 f16 e-16","o2 f4"],
# ["o4 b-8 d8","o3 d16 e-16 f16 d16","o2 b-4"],
# ["o4 f8 d8","o3 <b-16 >d16 f16 b-16","o2 b-4"],
# ["o4 <b-8 >d8","o3 d16 f16 a-16 b-16","o2 p4"],
# ["o4 e-8 p8","o3 g16 f16 g16 b-16","o1 e-8 >e-8"],
# ["o4 e-8 p8","o3 a-16 g16 a-16 >c16","o2 <f8 >e-8"],
# ["o4 e-8 p8","o3 <b-16 a-16 b-16 >d-16","o2 <g8 >e-8"],
# ["o4 e-8 p8","o4 c16 <b-16 >c16 e-16","o2 <a-8 >e-8"],
# ["o4 e-8 p8","o4 <g16 f16 g16 >e-16","o2 <b-8 >e-8"],
# ["o4 e-8 p8","o4 <a-16 g16 a-16 >e-16","o2 c8 e-8"],
# ["o4 p16 e-16 f16 g16","o4 <g8 b-8","o2 <b-8 p8"],
# ["o4 a-16 b-16 >c16 <b-16","o3 >e-8 <g8","o1 >c8 p8"],
# ["o4 a-16 g16 f16 a-16","o3 f8 b-8","o2 d8 p8"],
# ["o4 g8 <b-8","o3 p16 e-16 f16 g16","o2 e-4"],
# ["o3 >c8 <a-8","o3 a-16 b-16 >c16 <b-16","o2 e-4"],
# ["o3 >f4","o3 a-16 g16 f16 a-16","o2 d4"],
# ["o4 p16 a-16 g16 f16","o3 g8 <b-8","o2 e-4"],
# ["o4 e-16 d16 c16 <b-16","o2 >c8 <a-8","o2 a-4"],
# ["o3 a-16 g16 a-16 >f16","o2 >f4","o2 p4"],
# ["o4 <g16 >f16 e-16 d16","o3 p16 a-16 g16 f16","o2 <b4"],
# ["o4 c16 <b-16 a-16 g16","o3 e-16 d16 c16 <b-16","o1 >c4"],
# ["o3 f4","o2 a-16 g16 a-16 >f16","o2 d4"],
# ["o3 p16 a-16 g16 f16","o3 <g16 >f16 e-16 d16","o2 <e-4"],
# ["o3 e-4","o3 c16 <b-16 a-16 g16","o1 a-4"],
# ["o3 p16 d16 e-16 f16","o2 f4","o1 a-4"],
# ["o3 <b8 >d8","o2 p16 a-16 g16 f16","o1 g4"],
# ["o3 g8 b8","o2 e-8 g8","o1 p16 >g16 f16 g16"],
# ["o3 >c8 d8","o2 a8 b8","o2 e-16 f16 d16 e-16"],
# ["o4 e-16 c16 <b16 >c16","o3 c8 p8","o2 c8 e-8"],
# ["o4 <g16 >c16 <b16 >c16","o3 p4","o2 c8 e-8"],
# ["o4 e-16 c16 <b-16 >c16","o3 p4","o2 c8 e-8"],
# ["o4 <a-8 p8","o3 p16 f16 e-16 f16","o2 <f8 >a-8"],
# ["o3 >e-8 p8","o3 c16 f16 e-16 f16","o2 <f8 >a-8"],
# ["o4 e-8 p8","o3 a-16 f16 e-16 f16","o2 <f8 >a-8"],
# ["o4 p16 <b-16 a-16 b-16","o3 d8 p8","o2 <b-8 >d8"],
# ["o3 f16 b-16 a-16 b-16","o3 a-8 p8","o2 <b-8 >d8"],
# ["o3 >d16 <b-16 a-16 b-16","o3 a-8 p8","o2 <b-8 >d8"],
# ["o3 g8 p8","o3 p16 e-16 d-16 e-16","o2 <e-8 >g8"],
# ["o3 >d-8 p8","o3 <b-16 >e-16 d-16 e-16","o2 <e-8 >g8"],
# ["o4 d-8 p8","o3 g16 e-16 d-16 e-16","o2 <e-8 g8"],
# ["o3 p16 a-16 g16 a-16","o3 c16 f16 e16 f16","o1 a-8 >c8"],
# ["o3 f16 a-16 g16 a-16","o3 c16 f16 e16 f16","o2 <a-8 >c8"],
# ["o3 >c16 <a-16 g16 a-16","o3 a-16 f16 e-16 f16","o2 <a-8 >c8"],
# ["o3 f16 b-16 a-16 b-16","o3 d8 f8","o2 <a-8 >d8"],
# ["o3 >d16 <b-16 a-16 b-16","o3 b-4","o2 <a-8 >d8"],
# ["o3 >f16 d16 c16 d16","o3 b-4","o2 <a-8 >d8"],
# ["o4 b-8 g8","o3 p16 <b-16 a-16 b-16","o2 <g8 >e-8"],
# ["o4 e-4","o2 >e-16 <b-16 a-16 b-16","o2 <g8 >e-8"],
# ["o4 e-4","o2 >g16 e-16 d16 e-16","o2 <g8 >e-8"],
# ["o4 p16 d16 c16 <b-16","o3 a16 b-16 a16 g16","o2 <f4"],
# ["o3 a16 b-16 a16 g16","o3 f16 >d16 c16 <b-16","o1 p4"],
# ["o3 f16 >e-16 d16 c16","o3 a16 g16 f16 e-16","o1 p4"],
# ["o3 b-4","o3 d16 c16 d16 f16","o1 b-8 >b-8"],
# ["o3 b-4","o3 e-16 d16 e-16 g16","o2 c8 b-8"],
# ["o3 b-4","o3 f16 e-16 f16 a-16","o2 d8 b-8"],
# ["o3 p16 a16 b-16 >e-16","o3 g16 f16 g16 b-16","o2 e-8 b-8"],
# ["o4 <b-16 a16 b-16 >d16","o3 d16 c16 d16 b-16","o2 f8 b-8"],
# ["o4 c4","o3 e-16 d16 e-16 b-16","o2 g8 b-8"],
# ["o4 p16 g16 f16 e-16","o3 d4","o2 f8 b-8"],
# ["o4 d16 b-16 a16 g16","o3 p16 >d16 c16 <b-16","o2 e-8 b-8"],
# ["o4 f16 e-16 d16 c16","o3 a16 g16 f16 e-16","o2 f8 a8"],
# ["o3 b-8 >f8","o3 d16 b-16 a16 b-16","o1 b-4"],
# ["o4 g8 f8","o3 e-16 b-16 d16 b-16","o1 p4"],
# ["o4 g8 f8","o3 e-16 b-16 c16 b-16","o1 p4"],
# ["o4 f16 b-16 a16 b-16","o3 d8 f8","o1 b-4"],
# ["o4 e-16 b-16 d16 b-16","o3 g8 f8","o1 p4"],
# ["o4 e-16 b-16 c16 b-16","o3 g8 e-8","o1 p4"],
# ["o4 d4","o3 f16 <b-16 >c16 d16","o1 p8 >f8"],
# ["o4 p16 <b-16 >c16 d16","o3 e-4","o2 g8 f8"],
# ["o4 e-16 f16 g16 a16","o3 p16 d16 e-16 c16","o2 g8 e-8"],
# ["o4 b-8 <b-8","o3 f8 d8","o2 d8 g8"],
# ["o3 >c8 p8","o3 e-8 p8","o2 e-8 p8"],
# ["o4 <a4","o3 c4","o2 f4"],
# ["o3 mlb-4","o3 mld4","o1 mlb-4"],
# ["o3 b-4","o3 d4","o1 b-4"],
# ["o3 b-4","o3 d4","o1 b-4"]]

# lines = [["cdefgab>c", "efgab>cde", "gab>cdefg"]]

lines = [
    ["t140mll8g4.g>ce", "l8cp4c", "l8<ep4e"],
    ["t140mll8>d4.d<b->a", "l8dp4d", "l8<fp4f "],
]
for music in lines:
    pianoroll = []

    for f, v in enumerate(music):
        toparse = PlayStatement()
        toparse.channel = f
        toparse.statement = v.lower()
        pianoroll.extend(toparse.sound())

    pianoroll.sort(key=lambda x: x[3])

    # print(pianoroll)

    dt = datetime.now()
    for i in pianoroll:
        mdt = int((datetime.now() - dt).total_seconds() * 1000)
        while mdt < i[3]:
            mdt = int((datetime.now() - dt).total_seconds() * 1000)
        if i[1] == 0:
            pygame.mixer.Channel(i[0]).stop()
        else:
            pygame.mixer.Channel(i[0]).play(Note(i[1]), -1)


# m = ["E8 E8 F8 G8 G8 F8 E8 D8 C8 C8 E8 E8 E8 D12 D4",
#     "E8 E8 F8 C8 G8 F8 E8 D8 C8 C8 D8 E8 D8 C12 C4",
#     "D8 D8 E8 C8 D8 E12 F12 E8 C8 D8 E12 F12 E8 D8 C8 D8 P8",
#     "E8 E8 F8 G8 G8 F8 E8 D8 C8 C8 D8 E8 D8 C12 C4"]

# m = ["t64l12"+"v4<a>v7cv12e"*4]

# for i in m:
#     play = PlayStatement()
#     play.statement = i.lower()
#     play.sound()
