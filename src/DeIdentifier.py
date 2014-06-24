# -*- coding: utf-8 -*-
'''
Script to
1- read in the data
2- perform processing in the different modules
2a- text segmentation
2b- tokenization
2c- de-identification
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

months=["januari", "jan", "februari", "feb", "maart", "mar", "mrt", "april", "apr", "mei", "juni", "jun", "juli", "jul", "augustus", "aug", "september", "sept", "sep", "oktober", "okt", "november", "nov", "december", "dec"]

from deltaCalculator import deltaCalculator
import re

class DeIdentifier(object):
    def __init__(self,dataPoint,DEIDlists):
        self.dataPoint=dataPoint
        [self.names,self.firstnames,self.streets,self.cities,self.countries]=DEIDlists
        return

    def deidentifyRAW(self):
        '''De-identify raw text'''
        
        '''1. Perform simple tokenization, but keep all formatting information'''
        words=re.split(r'(\s|<newline>|\.|<tab>|:|,|;|\?|!|-|\"|\'|\)|\(|<page>|<horline>|<arrowright>|<italic>|<dash>|<registered>|<dotdotdot>|<euro>|<circa>|<lte>|<arrowup>|<micro>|<alpha>|<born>)',self.dataPoint)

        '''2. From Gazetteer lists: Names, first names, street names, city names, country names, hospital names, mut institution names, legacy network names, month names'''
        words=simpleReplace(words,self.names,"<name>")
        words=simpleReplace(words,self.firstnames,"<firstname>")
        words=simpleReplace(words,self.streets,"<street>")
        words=simpleReplace(words,self.cities,"<city>")
        words=simpleReplace(words,self.countries,"<country>")
        words=simpleReplace(words,months,"<month>")
        
        '''3. Randomize dates, but keep the relative distance between dates'''
        deltas=deltaCalculator(words)
        deltas.track()
        deltas.calculateTransformations()
        newwords=deltas.transform()

        '''4. Tag time indications'''
        text="".join(newwords)
        timeRE=re.compile(r'\d\d?:\d\d\s')
        timeList=timeRE.findall(text)
        for time in timeList:
            text=text.replace(time,"<time>")
    
        '''5. Identify national ID and patient ID numbers'''
        natID=re.compile(r'\d\d\d\d\d\d\s*\d\d\d\s*\d\d')
        natIDs=natID.findall(text)
        if natIDs!=[]:
            for natID in natIDs:
                text=text.replace(natID,"<id>")
        patID=re.compile(r'\d\d\d\d\d\d\d\d\d')
        patIDs=patID.findall(text)
        if patIDs!=[]:
            for patID in patIDs:
                text=text.replace(patID,"<id>")

        '''6. Final postprocessing to make sure no names remain'''
        text=postprocess(text,self.names,self.firstnames)
        return text

def postprocess(text,names,firstnames):
    '''Locate any remaining names, possibly missed because of the absence of spaces'''
    
    ''''Simple tokenization, but keeping all information'''
    words=re.split(r'(\s|<newline>|\.|<tab>|:|,|;|\?|!|-|\"|\'|\)|\(|<page>|<name>|<firstname>|<street>|<city>|<country>|<hospital>|<mut>|<network>|<month>|<time>|<id>|<horline>|<arrowright>|<italic>|<dash>|<registered>|<dotdotdot>|<euro>|<circa>|<lte>|<arrowup>|<micro>|<alpha>|<born>)',text)

    words=simpleReplace(words,names,"<name>")
    words=simpleReplace(words,firstnames,"<firstname>")
    text="".join(words)
    return text
    
def simpleReplace(wordList,itemList,code):
    '''Locate and replace items from a list in a set of words
    these are items you can replace without conditions
    
    I assume in this basic version of the DEID that Named Entities are capitalized (names are also capitalized in the list of names and first names)
    Only does complete matches, so no partial matches
    
    FAST version using the dict.fromkeys(itemList,True) trick'''
    
    itemList=dict.fromkeys(itemList,True)
    
    flags=[]
    for word in wordList:
        if len(word) > 1:
            if word[0]+"".join(word[1:].lower()) in itemList:
                flags.append(word)
        else:
            if word in itemList:
                flags.append(word)

    if flags != []:
        newwords=[]
        for word in wordList:
            if len(word) > 1:
                if word[0].isupper() == True:
                    word2check=word[0]+"".join(word[1:].lower())
                    if word2check not in itemList:
                        newwords.append(word)
                    elif word2check in itemList:
                        #index=words.index(word)
                        #print words[ index-4:index+5 ] #4L, 4R
                        newwords.append(code)
                else:
                    newwords.append(word)
            else:
                if word in itemList:
                    #index=words.index(word)
                    #print words[ index-4:index+5 ] #4L, 4R
                    newwords.append(code)
                else:
                    newwords.append(word)
    else:
        newwords=wordList
    return newwords

def identifyContext(index,words):
    '''To be used as input for machine learning algorithm'''
    basket=["","","",words[index],"","",""]
    i=0
    for x in xrange(index-3,index+4):
        if x >= 0:
            try:
                if words[x] != '':
                    basket[i]=words[x].lower()
            except:
                basket[i]=""
        i+=1
    print "===", basket

if __name__ == "__main__":
    print '''
###
Commandline usage:

echo "This is my text with a name, Marc, in it." | python DeIdentifier.py
###
	'''
    import sys
    
    '''Collect and read in all resources'''
    import importDEIDresources
    DEIDlists = importDEIDresources.getGazetteers()

    dataPoint=sys.stdin.read()
    DEID=DeIdentifier(dataPoint, DEIDlists)
    DEIDtext=DEID.deidentifyRAW()
    print "output:", DEIDtext
