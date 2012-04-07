#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

# thanks for Johannes Weiss
# code from: http://stackoverflow.com/a/566752/386521

import math
import traceback

def indent_text(text, extra_indentation=0):
    base_depth = 11
    stack_depth = (len(traceback.extract_stack())+extra_indentation) - base_depth
    return ' '*stack_depth+text

def generate_right_padded_string(text, character="=", consider_indendation=True):
    console_width = get_terminal_size()[0]
    if consider_indendation:
        console_width -= len(traceback.extract_stack()) - 3
    text_length = len(text)
    total_padding_count = console_width - text_length
    if total_padding_count > 1:
        text = text + character*total_padding_count
    return text
#end def generate_right_padded_string
    
def generate_centered_padded_string(text, character="="):
    console_width = get_terminal_size()[0]
    text_length = len(text)
    total_padding_count = console_width - text_length
    if total_padding_count > 1:
        left_padding = int(math.ceil(total_padding_count/2))
        right_padding = int(total_padding_count - left_padding)
        text = character*left_padding + text + character*right_padding
    return text
#end def generate_centered_padded_string

def get_terminal_size():
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
        '1234'))
        except:
            return None
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (env['LINES'], env['COLUMNS'])
        except:
            cr = (25, 80)
    return int(cr[1]), int(cr[0])
#end def get_terminal_size