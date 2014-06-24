# -*- coding: utf-8 -*-
'''
Basic utilities for dealing with unstructured data
'''

__author__ = "Kim Luyckx (luyckx.kim@gmail.com)"
__license__ = '''Copyright (C) 2014  Kim Luyckx <luyckx.kim@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.'''

import unicodedata, re, sys

characters2strip=[0,1,2,3,4,5,6,7,8,13,14,15,16,17,18,21,22,23,24,25,26,27,28,29,30,31]
characters2save=[9, 10]

def stripControlCodesString(string):
    return "".join([i for i in string if ord(i) in range(0, 256) if ord(i) not in characters2strip])
