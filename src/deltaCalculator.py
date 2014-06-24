# -*- coding: utf-8 -*-
'''
Script to calculate distances between dates, change the earliest date to Jan 1 2000, and change the later dates accordingly, while keeping the distance intact
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

import datetime, re

class deltaCalculator(object):

    def __init__(self, wordList):
        self.wordList=wordList
        self.text="".join(self.wordList)
        return
    
    def track(self):
        '''Find date indications in self.wordList as they occur in the text'''
        self.text = "".join(self.wordList)
    
        dateRE = re.compile(r'(\d\d?[/-]\d\d?[/-]\d\d\d\d)(?![\d/-])')
        FULLdateList = dateRE.findall(self.text)
        tmpText = self.text
        tmpText = re.sub(dateRE,'',tmpText)
        
        reverseDateRE = re.compile(r'(\d\d\d\d[/-]\d\d?[/-]\d\d?)(?![\d/\-\.])')
        reverseFULLdateList = reverseDateRE.findall(tmpText)
        tmpText = re.sub(reverseDateRE, '', tmpText)

        SHORTdateRE = re.compile(r'(\d\d?[/-]\d\d?[/-]\d\d)(?![\d/-])')
        SHORTdateList = SHORTdateRE.findall(tmpText)

        newDateList = FULLdateList + reverseFULLdateList + SHORTdateList
        self.dateList = [d.strip() for d in newDateList]
        
        return self.dateList
    
    def calculateTransformations(self):
        if self.dateList != []:
            self.reformatted=reformat(self.dateList)
            
            if self.reformatted != []:
                self.minDate,self.adaptedMIN=findFirstDate(self.reformatted)
            
                self.MINdefaultDate=datetime.date(2000,01,01)
                self.transformations={}
                for original,reformatted in zip(self.dateList,self.reformatted):
                    if reformatted[0] != self.minDate:
                        try:
                            newDate=calculateDiff(reformatted,self.minDate,self.MINdefaultDate)
                        except:
                            newDate=original
                        self.transformations[original]=newDate
                    else:
                        self.transformations[original]=self.adaptedMIN
                return self.transformations
            else:
                pass
        else:
            pass

    def transform(self):
        from dynamicConfig import TMPDIR
        import os
        if (self.dateList != []) and (self.reformatted != []):
            '''Sort transformations to prevent cases of 7-01-2008 to be replaced before 07-01-2008'''
            self.orderedTransformations=sorted(self.transformations.items(), lambda x, y: cmp(x[0], y[0]), reverse=False)
            
            '''Transform the dates in the original text'''
            for orig, new in self.orderedTransformations:
                if orig in self.text:
                    self.text=self.text.replace(orig,"<"+new+">")
                else:
                    #print orig, new
                    #print self.dateList
                    #print self.text
                    if not os.path.isfile(os.path.join(TMPDIR,"problemDates.txt")):
                        with open(os.path.join(TMPDIR,"problemDates.txt"),"w") as f:
                            f.write(str(self.dateList)+"\n")
                            f.write(str(self.text) + "\n")
                            f.write("unable to locate %s - to be replaced by %s\n\n" %(orig,new))
                    else:
                        with open(os.path.join(TMPDIR,"problemDates.txt"),"a") as f:
                            f.write(str(self.dateList)+"\n")
                            f.write(str(self.text) + "\n")
                            f.write("unable to locate %s - to be replaced by %s\n\n" %(orig,new))
                    pass
            return self.text
        else:
            return self.text

def reformat(dateList):
    newDateList = []
    for d in dateList:
        SEP = findSEP(d)
        parts = d.split(SEP)
        
        '''Turn yyyy/mmm/dd into dd/mm/yyyy'''
        if len(parts[0]) == 4:
            swap = parts[0]
            parts[0] = parts[-1]
            parts[-1] = swap
            d = SEP.join(parts) 
        
        yy = parts[-1].lstrip(" ")
        if len(yy) == 2:
            newd=SEP.join(d.split(SEP)[:-1])
            if yy in ["00","01","02","03","04","05","06","07","08","09","10","11","12","13"]:
                newd+=SEP+"20"+yy
            else:
                newd+=SEP+"19"+yy
            newDateList.append(newd)
        else:
            newDateList.append(d)
    
    reformattedList=[]
    for d in newDateList:
        (date,SEP)=string2datetimeformat(d)
        if (date,SEP) != (None,None):
            reformattedList.append((date,SEP))
    return reformattedList

def string2datetimeformat(dateString):
    '''
    Convert a date to datetime format and keep separator information
    returns (datetime.date(2008, 1, 7), '/') on input of '07/01/2008'
    '''
    try:
        SEP=findSEP(dateString)        
        dd,mm,yy=[int(item) for item in re.split(r'(\d\d?)([/-])(\d\d?)([/-])(\d\d+)',dateString) if item != "" and item not in ["/","-"]]
        
        if dd == 0: dd = 1
        
        '''Months and days have probably been switched'''
        if mm > 12:
            swap = dd
            dd = mm
            mm = swap 
        
        date=datetime.date(yy, mm, dd)
        return (date,SEP)
    except:
        return (None,None)

def datetimeformat2string(datetimeObject,SEP):
    '''
    Reconstruct a datestring from datetime format and separator information
    '''
    return datetimeObject.strftime("%d/%m/%Y").replace("/",SEP)

def findSEP(d):
    if "/" in d:    SEP="/"
    elif "-" in d:  SEP="-"
    else:
        print "new sep in %s!" %d
        raise
    return SEP

def findFirstDate(reformattedList):
    reformattedSEPs=[y for x,y in reformattedList]
    reformattedDates=[x for x,y in reformattedList]
    reformattedDates.sort()
    '''Find the lowest date and replace it by the default date, i.e. 01/01/2000'''
    minDate=reformattedDates[0]
    SEP=reformattedSEPs[0]
    adaptedMIN="01%s01%s2000" %(SEP,SEP)
    return minDate,adaptedMIN

def calculateDiff(reformatted,minDate,defaultDate):
    reformattedDate=reformatted[0]
    reformattedSEP=reformatted[1]
    delta = reformattedDate - minDate
    new = defaultDate + datetime.timedelta(days=delta.days)
    newDate = datetimeformat2string(new,reformattedSEP)
    return newDate