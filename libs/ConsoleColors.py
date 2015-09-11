# -*- coding: utf-8 -*-
'''
@author: moloch

    Copyright 2013

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''

import platform

if platform.system().lower() in ['linux', 'darwin']:

    # === Text Colors ===
    W = "\033[0m"  # default/white
    BLA = "\033[30m"  # black
    R = "\033[31m"  # red
    G = "\033[32m"  # green
    O = "\033[33m"  # orange
    BLU = "\033[34m"  # blue
    P = "\033[35m"  # purple
    C = "\033[36m"  # cyan
    GR = "\033[37m"  # gray

    # === Styles ===
    bold = "\033[1m"
    underline = "\033[4m"
    blink = "\033[5m"
    reverse = "\033[7m"
    concealed = "\033[8m"

    # === Background Colors ===
    bkgd_black = "\033[40m"
    bkgd_red = "\033[41m"
    bkgd_green = "\033[42m"
    bkgd_yellow = "\033[43m"
    bkgd_blue = "\033[44m"
    bkgd_magenta = "\033[45m"
    bkgd_cyan = "\033[46m"
    bkgd_white = "\033[47m"

else:

    # Sets all colors to blank strings
    # === Text Colors ===
    W = ""
    BLA = ""
    R = ""
    G = ""
    O = ""
    BLU = ""
    P = ""
    C = ""
    GR = ""

    # === Styles ===
    bold = ""
    underline = ""
    blink = ""
    reverse = ""
    concealed = ""

    # === Background Colors ===
    bkgd_black = ""
    bkgd_red = ""
    bkgd_green = ""
    bkgd_yellow = ""
    bkgd_blue = ""
    bkgd_magenta = ""
    bkgd_cyan = ""
    bkgd_white = ""

# === Macros ===
INFO = bold + C + "[*] " + W
WARN = bold + R + "[!] " + W
PROMPT = bold + P + "[?] " + W
