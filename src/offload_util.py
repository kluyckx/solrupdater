# -*- coding: utf-8 -*-
'''
Basic utilities for offloading data from the database
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

import os, sys
from datetime import datetime
from time_util import daterange
        
DELIMITER = "%|"
ESCAPED_DELIMITER = "@%@|"

def escape_delimiter(s):
    return s.replace(DELIMITER, ESCAPED_DELIMITER)

def unescape_delimiter(s):
    return s.replace(ESCAPED_DELIMITER, DELIMITER)

def prepare_offload_folder(offload_folder):
    if not os.path.exists(offload_folder):
        print "\tCreating {0}".format(offload_folder)
        os.makedirs(offload_folder)
    else:
        print "\tUsing {0}".format(offload_folder)
    return offload_folder


def prepare_offload_file(offload_file):
    print "\tUsing {0}".format(offload_file)
    return offload_file
        
        
def prepare_monthly_offload(single_date, base_offload_folder):
    offload_folder = prepare_offload_folder(single_date.strftime("{0}{1}%Y".format(base_offload_folder, os.sep)))
    return prepare_offload_file(single_date.strftime("{0}{1}-dump-%m.txt".format(offload_folder, os.sep)))
    
if __name__ == "__main__":
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    
    start_date = datetime.strptime(sys.argv[1], '%d/%m/%Y')
    end_date = datetime.strptime(sys.argv[2], '%d/%m/%Y')
    base_offload_folder = sys.argv[3] 
    
    print "Start: {0}".format(start_date.strftime('%Y-%m-%d'))
    print "End: {0}".format(end_date.strftime('%Y-%m-%d'))
    print "Offloads: {0}\n".format(base_offload_folder)
    
    for single_date in daterange(start_date, end_date):
        print "Handling: {0}".format(single_date.strftime("%Y-%m-%d"))
        prepare_monthly_offload(single_date, base_offload_folder)        
    