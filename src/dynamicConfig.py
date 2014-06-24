# -*- coding: utf-8 -*-
'''
Dynamic configuration file
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
cwd = os.getcwd()

if "github" in cwd.lower():
    SOLRUPDATER = cwd
    RESOURCES_DIR = os.path.join(SOLRUPDATER, "DEIDresources")
    BASE_OFFLOAD_FOLDER = os.path.join(SOLRUPDATER, "tmp")
    SOLR_BASE_URL = "http://solrprod:8080/solr"
    SOLR_BASE_DIR = "/home/solr/solr3/myIndex"
    SOLR_POST_DIR = "/home/solr/solr3/myIndex/solr"
    UPDATE_DEID_URL = SOLR_BASE_URL + "/deidentified/update"
    UPDATE_ORIG_URL = SOLR_BASE_URL + "/original/update"

    LOGFILE = os.path.join(SOLRUPDATER, "solrupdater-logs.txt")
    TMPDIR = os.path.join(SOLRUPDATER, "tmp")
    CHECK_SOLR_STATUS = False

else:
    print "unknown project or machine"
    raise

### default
DEID = True
DB = "mydb"
USER = ""
PASSWORD = ""
HOST = ""