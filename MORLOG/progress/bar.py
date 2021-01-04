# -*- coding: utf-8 -*-

# Copyright (c) 2012 Georgios Verigakis <verigak@gmail.com>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from __future__ import unicode_literals
from enum import unique

import sys
import math

import numpy as np
from . import Progress
from .colors import color


class Bar(Progress):
    width = 32
    suffix = '%(index)d/%(max)d'
    bar_prefix = ' |'
    bar_suffix = '| '
    empty_fill = ' '
    fill = '#'
    color = None

    def update(self):
        filled_length = int(self.width * self.progress)
        empty_length = self.width - filled_length

        message = self.message % self
        bar = color(self.fill * filled_length, fg=self.color)
        empty = self.empty_fill * empty_length
        suffix = self.suffix % self
        line = ''.join([message, self.bar_prefix, bar, empty, self.bar_suffix,
                        suffix])
        return line


class ChargingBar(Bar):
    suffix = '%(index)d'
    bar_prefix = ' '
    bar_suffix = ' '
    empty_fill = '∙'
    fill = '█'


class FillingSquaresBar(ChargingBar):
    empty_fill = '▢'
    fill = '▣'


class FillingCirclesBar(ChargingBar):
    empty_fill = '◯'
    fill = '◉'


class IncrementalBar(Bar):
    suffix = '%(index)d'
    bar_prefix = ' :'
    bar_suffix = ' '
    empty_fill = '∙'
    if sys.platform.startswith('win'):
        # phases = (u' ', u'▌', u'█')
        phases = (' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉', '█')
    else:
        phases = (' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉', '█')
    def skip_to_frame(self, frame):
        self.index = frame

    def update(self):
        nphases = len(self.phases)
        filled_len = self.width * self.progress
        nfull = int(filled_len)                      # Number of full chars
        phase = int((filled_len - nfull) * nphases)  # Phase of last char
        nempty = self.width - nfull                  # Number of empty chars

        message = self.message % self
        bar = color(self.phases[-1] * nfull, fg=self.color)
        current = self.phases[phase] if phase > 0 else ''
        empty = self.empty_fill * max(0, nempty - len(current))
        suffix = self.suffix % self + '\n'
        line = ''.join([message, self.bar_prefix, bar, current, empty,
                        self.bar_suffix, suffix])
        return line
        # self.writeln(line)


class PixelBar(IncrementalBar):
    phases = ('⡀', '⡄', '⡆', '⡇', '⣇', '⣧', '⣷', '⣿')


class ShadyBar(IncrementalBar):
    phases = (' ', '░', '▒', '▓', '█')





def bin_behaviour(behaviour, behaviour_name):
    behaviour_len = len(behaviour)
    #total_length should be 60 (with each bin having three sub bins)
    total_bins = 180
    bin_size = math.ceil(len(behaviour)/total_bins)
    behaviour_locations = behaviour==behaviour_name
    behaviour_binned = [np.sum(behaviour_locations[(bin*bin_size):(bin+1)*bin_size]) for bin in range(total_bins)]
    total_bins = math.floor(len(behaviour_binned)/3)
    behaviour_binned = [tuple(behaviour_binned[(bin*3):(bin+1)*3]) for bin in range(60)]
    return behaviour_binned


def behaviour_convert(behaviour):
    behaviour_dict = dict({tuple([0, 0, 0]):'∙', tuple([1, 0, 0]):'⎸',\
                           tuple([0, 0, 1]):'⎹', tuple([1, 1, 0]):'⊩',\
                           tuple([0, 1, 1]):'⫣', tuple([1, 0, 1]):'‖',\
                           tuple([1, 1, 1]):'⦀', tuple([0, 1, 0]):'|'})
    max_behaviour = max(behaviour)
    if max_behaviour<=1:
        behaviour=behaviour_dict[behaviour]
    else:
        if sum(behaviour)==2:
            behaviour = '‖'
        else:
            behaviour='⦀'
    return behaviour

            
def behaviour_timeline(behaviour):


    behaviour_bar = [behaviour_convert(i) for i in behaviour]
    return ''.join(behaviour_bar)

def create_all_behaviour_bars(behaviour):
    behaviour_names = behaviour.unique()
    ##drop na and nothing
    behaviour_names = [i for i in filter(lambda v: v==v, behaviour_names) if i!='Nothing']
    behaviour_bar_block = ['\n']
    for name in behaviour_names:
          print(name)
          behaviour_select = bin_behaviour(behaviour, name)
          
          name = name[:9]
          name+=(9-len(name))*' '
          behaviour_bar_block.append('{}:'.format(name))
          behaviour_bar_block.append(behaviour_timeline(behaviour_select))  
          behaviour_bar_block.append('  {} \n'.format(np.sum(behaviour_select)))
    return ''.join(behaviour_bar_block)

