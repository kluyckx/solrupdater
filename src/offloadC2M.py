# -*- coding: utf-8 -*-
'''
Script to offload data from the database
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

import time, os
from datetime import datetime

from offload_util import DELIMITER, prepare_monthly_offload, escape_delimiter
from time_util import monthrange, getInHMS
from dynamicConfig import USER, PASSWORD, HOST

global start; start = time.time()

QUERY_TEMPLATE_docs = '''SELECT d.CONTENTS, p.EXTPID, d.CONCLUSION, d.CREATOR, d.DESCRIPTION, d.TMEXAM, d.CATEGORY, a.MODIFSPECIALTY \
                FROM <DB>.<table>.PATIENT p, <DB>.<table>.DOC_ACT d, <DB>.<table>.ACT a \
                WHERE a.PID = p.PID \
                      AND d.CREATOR = a.CREATOR \
                      AND a.MODIFDELETED = 0 \
                      AND d.TMEXAM > \'%s\' \
                      AND d.TMEXAM < \'%s\' \
                ORDER BY d.TMEXAM'''

QUERY_TEMPLATE_notes = '''SELECT n.RTFTEXT, p.EXTPID, ' ' as conclusion , n.CREATOR, n.TYPE, a.TMRESULTCREATED, 'nota' as category, a.MODIFSPECIALTY \
                FROM <DB>.<table>.PATIENT p, <DB>.<table>.NOTE_ACT n, <DB>.<table>.ACT a \
                WHERE a.PID = p.PID \
                        AND n.CREATOR = a.CREATOR \
                        AND a.MODIFTM >= \'%s\' \
                        AND a.MODIFTM < \'%s\''''

def closeConnection(connection):
    connection.close()
    
def writeResultToFile(result, offload_file):
    f = open(offload_file, 'a')
    result[5] = datetime.strptime(result[5], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S')
    result = result
    f.write(DELIMITER.join(result).replace("\x00","") + DELIMITER + '\n')
    f.close()

def processDate(start_date, end_date, base_offload_folder, connection, DB):
    offload_file = prepare_monthly_offload(start_date, base_offload_folder)
    
    if not os.path.isfile(offload_file):
        query_start_date = start_date.strftime('%d/%m/%Y')
        query_end_date = end_date.strftime('%d/%m/%Y')
        query_start_date_intl = start_date.strftime('%Y-%m-%d')
        query_end_date_intl = end_date.strftime('%Y-%m-%d')
        
        print "\tProcessing query for {0}".format(query_start_date)
        start = time.time()
        
		processQuery(connection, query_start_date_intl, query_end_date_intl, offload_file)
        print "\t\tQuery took {0}".format( getInHMS(time.time()- start))
    else:
        pass
    return offload_file

def processQuery(connection, offload_start_date, offload_end_date, offload_file):
    cursor = connection.cursor()
    
    '''Process the query'''
    print "starting execution of query", time.time()-start
    cursor.execute(QUERY_TEMPLATE_docs %(offload_start_date, offload_end_date))

    row = cursor.fetchone()
    tot=0
    while row:
        entry=[]
        for idx in xrange(0, len(row)):
            if row[idx] is None:
                entry.append('(None)')
            else:
                entry.append(escape_delimiter(str(row[idx]).decode('latin-1', "strict").encode('utf8', "strict")))

        writeResultToFile(entry, offload_file)
        tot+=1
        row=cursor.fetchone()

    cursor.execute(QUERY_TEMPLATE_notes %(offload_start_date, offload_end_date))

    row = cursor.fetchone()
    while row:
        entry=[]
        for idx in xrange(0, len(row)):
            if row[idx] is None:
                entry.append('(None)')
            else:
                entry.append(escape_delimiter(str(row[idx]).decode('latin-1', "strict").encode('utf8', "strict")))
        writeResultToFile(entry, offload_file)
        tot+=1
        row=cursor.fetchone()

    cursor.close()
    
    print "\t\tProcessed {0} results".format(tot), "after %s seconds" %(time.time()-start)
    
    return

def makeConnection():
    import pymssql
    connection = pymssql.connect(host=HOST, user=USER, password=PASSWORD, database=DB)
    print "made connection", time.time()-start
    return connection

def startProcess(offload_start, offload_end, base_offload_folder, DB):
    start_date = datetime.strptime(offload_start, '%m/%Y')
    end_date = datetime.strptime(offload_end, '%m/%Y')

    print "starting execution", time.time()-start
    connection = makeConnection()

    offload_files = []
    for d1, d2 in monthrange(start_date, end_date):
        print "Handling: {0} <=> {1}".format(d1.strftime("%Y-%m-%d"), d2.strftime("%Y-%m-%d"))
        offload_files.append( processDate(d1, d2, base_offload_folder, connection, DB) )
    
    print "closing connection", time.time()-start
    closeConnection(connection)
    return offload_files
