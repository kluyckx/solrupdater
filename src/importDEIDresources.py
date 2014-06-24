# -*- coding: utf-8 -*-
'''
Read in the gazetteers for de-identification
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

import os

from dynamicConfig import RESOURCES_DIR
topFile = os.path.join(RESOURCES_DIR, "top10000nl.txt")

nameFile = os.path.join(RESOURCES_DIR, "names.txt")
firstnameFile = os.path.join(RESOURCES_DIR, "firstnames.txt")
streetFile = os.path.join(RESOURCES_DIR, "streets.txt")
cityFile = os.path.join(RESOURCES_DIR, "cities.txt")
countryFile = os.path.join(RESOURCES_DIR, "countries.txt")

def getGazetteers():
    '''List of the 10000 most commonly used words in Dutch'''
    topList = openFile(topFile, typ="top")
    topList = dict.fromkeys(topList, True)

    '''Read in lists of names etc. extracted from C2M'''
    names=openFile(nameFile)
    firstnames=openFile(firstnameFile)
    streets=openFile(streetFile)
    cities=openFile(cityFile, topList)
    countries=openFile(countryFile)
    DEIDlists=[names,firstnames,streets,cities,countries]

    return DEIDlists

def openFile(sourceFile,topList=[],typ=""):
    
    if os.path.isfile(sourceFile):
        with open(sourceFile,'r') as fi:
            itemList = fi.readlines()
        if topList == []:
            itemList = [ item.strip() for item in itemList ]
        else:
            itemList = [ item.strip() for item in itemList if item not in topList ]

    elif os.path.isfile(sourceFile) and typ == "top":
        with open(sourceFile,"r") as fi:
            topList = fi.readlines()
        itemList = [ removeSpecials(w.lower().strip()) for w in topList if w[0].islower() ]
        itemList = list(set(itemList))

    else:
        raise "Files does not exist. De-identification cannot be executed"

    return itemList

def removeSpecials(word):
    word=word.replace("\xc3\xab","e").replace("\xe8","e").replace("\xef","i").replace("\xdd","i").replace("\xe9","e").replace("\xeb","e").replace("\xcd","e")
    return word

if __name__ == "__main__":
    DEIDlists=getGazetteers()
