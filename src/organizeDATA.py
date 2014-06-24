# -*- coding: utf-8 -*-
'''
1- organizing extracted data into fields
2- parsing RTF, converting (cf. W3C format for dates) and cleaning these fields
3- organizing it into a dictionary {'extpid':'', ...}

Makes use of pyth for RTF parsing; see https://pypi.python.org/pypi/pyth and https://github.com/brendonh/pyth
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


import re, time_util
import cStringIO
from offload_util import DELIMITER
from pyth.plugins.rtf15.reader import Rtf15Reader
from pyth.plugins.plaintext.writer import PlaintextWriter

def organizeANDparse(f):
    with open(f, 'r') as orig:
        lines = orig.read()

    '''Make sure tab and newline information is not lost'''
    lines = lines.replace("\x00","").replace("\n","").replace("\\par ", "<newline>").replace("\\tab ","<tab>").replace("\x0c","").replace("\'19","")

    header=["CONTENTS","EXTPID","CONCLUSION","CREATOR","DESCRIPTION","TMEXAM","CATEGORY","SPECIALTY"]
    contentMap = [x.lower().strip() for x in header]
    
    eggboxes = []
    eggbox = []
    for item in lines.split(DELIMITER):
        if len(eggbox) != len(header):
            eggbox.append( item.replace("\xef\xbb\xbf","").rstrip())
        else:
            eggboxes.append( eggbox )
            eggbox = []
            eggbox.append( item.replace("\xef\xbb\xbf","").rstrip())

    allEntries = []
    entry = []

    for eggbox in eggboxes:

        for item in eggbox:

            if isRTF(item):
                '''Parse the RTF'''
                '''1. Create a virtual document'''
                fh = cStringIO.StringIO()
                fh.write(item)
                '''2. De-RTF it using pyth'''
                try:
                    parsed = parseRTFstring(fh)
                except:
                    pass
                parsedText = parsed.replace("<newline>","\n").replace("<tab>","\t").replace("<par>","")
                item2index = re.sub(r'  +',' ', parsedText)
                entry.append( item2index )
            
            elif isPID(item):
                item2index = item
                entry.append( item2index )
            
            elif isDATE(item):
                item2index = time_util.convertDateW3C(item)
                entry.append( item2index )
            
            elif isCREATOR(item):
                item2index = item.replace(" ","_")
                entry.append( item2index )
            
            else:
                item2index = item
                entry.append( item2index )

        else:
            d = dict(zip(contentMap, entry))
            allEntries.append(d)
            entry=[]
#    fo.close()
    return allEntries

def parseRTFstring(rtfSTRING):
    doc = Rtf15Reader.read(rtfSTRING)
    #print PlaintextWriter.write(doc).getvalue()
    return PlaintextWriter.write(doc).getvalue()

def isRTF(item):
    if '{\\rtf1' in item: return True
    else: return False

def isPID(item):
    PID = re.compile(r'^\d{9}$')
    if PID.match(item): return True
    else: return False

def isDATE(item):
    date = re.compile(r'^\d{2}/\d{2}/\d{4} \d{1,2}\:\d{2}\:\d{2}$')
    if date.match(item): return True
    else: return False

def isCREATOR(item):
    creator = re.compile(r'^\d{14}.\d{3}.\d{2} \d{1,4}$')
    if creator.match(item): return True
    else: return False
    
def isSTR(item):
    return isinstance(item, str)

def saveResult(eggboxes,newf):
    '''Save output'''
    with open(newf, 'w') as fo:
        for eggbox in eggboxes:
            fo.write(eggbox+"\n")
    return newf
