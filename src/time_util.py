# -*- coding: utf-8 -*-
'''
Basic utilities for anything time-related
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
import sys
from datetime import datetime, timedelta


def daterange(start_date, end_date):
    start = start_date
    for n in range((end_date - start_date).days):
        end = start_date + timedelta(n+1)
        yield start, end
        start = end

        
def monthrange(start_date, end_date):
    start_month = start_date.month
    end_months = ((end_date.year-start_date.year) * 12) + (end_date.month + 1)
    dates = [ datetime(year=yr, month=mn, day=1) 
             for (yr, mn) in (((m - 1) / 12 + start_date.year, (m - 1) % 12 + 1) 
                              for m in range(start_month, end_months)) ]
    
    dates[0] = start_date    
    if dates[-1] != end_date:
        dates.append(end_date)
    
    for i in range(len(dates)):
        if i == (len(dates) - 1):
            break        
        yield dates[i], dates[i+1] 
        

def convertDateW3C(tmexam):
    '''Transform a string of the format 4/01/2008 11:15:13 (as present in our db) to official W3C dateTime format (as described on http://www.w3.org/TR/xmlschema-2/#dateTime and used in SOLR)'''
    import re
    origFormat=re.compile(r'\d+')
    try:
        dd,mm,yyyy,hh,mins,sec=origFormat.findall(tmexam)
        if len(dd) == 1: dd="0"+dd
        if len(mm) == 1: mm="0"+mm
        if len(hh) == 1: hh="0"+hh
        newFormat="%s-%s-%sT%s:%s:%sZ" %(yyyy,mm,dd,hh,mins,sec)
    except:
        try:
            dd,mm,yyyy=origFormat.findall(tmexam)
            if len(dd) == 1: dd="0"+dd
            if len(mm) == 1: mm="0"+mm
            newFormat="%s-%s-%sT%s:%s:%sZ" %(yyyy,mm,dd,"00","00","00")
        except:
            print "failed on", tmexam
    return newFormat

def getInHMS(seconds):
    import time
    return time.strftime('%H:%M:%S', time.gmtime(seconds))
