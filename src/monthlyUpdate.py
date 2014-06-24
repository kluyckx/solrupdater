# -*- coding: utf-8 -*-
'''
Script for monthly update of Solr index with extracts from a database (in this case containing Electronic Health Record data)

These scripts work for a dual-core Solr index, with 1) a 'deidientified' core containing only deidentified data, and 2) an 'original' core containing the original data
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

import sys, os, subprocess, urllib, time, text_util
import offloadC2M, organizeDATA
from DeIdentifier import DeIdentifier

from dynamicConfig import BASE_OFFLOAD_FOLDER, SOLR_BASE_URL, SOLR_BASE_DIR, SOLR_POST_DIR, UPDATE_DEID_URL, UPDATE_ORIG_URL, CHECK_SOLR_STATUS, DB

def startOffload(OFFLOAD_START, OFFLOAD_END, BASE_OFFLOAD_FOLDER, DB):
    offloadFiles = offloadC2M.startProcess(OFFLOAD_START, OFFLOAD_END, BASE_OFFLOAD_FOLDER, DB)
    return offloadFiles

def generateXML(offloadFile, DEID):
    entries = organizeDATA.organizeANDparse(offloadFile)

    if not DEID:
        XMLfile = offloadFile.replace(".txt",".noDEID.xml")
        save2XML(entries, XMLfile)
        return XMLfile

    else:
        import importDEIDresources
        DEIDlists=importDEIDresources.getGazetteers()
        print "DEID resources imported"
        
        DEIDentries=[]
        for entry in entries:
            DEID = DeIdentifier( entry["contents"], DEIDlists )
            entry["contentsDEID"]= resetControlCodes( DEID.deidentifyRAW() )
            del entry["contents"]
            DEIDentries.append(entry)
        DEIDXMLfile = offloadFile.replace(".txt",".DEID.xml")
        save2XML(DEIDentries, DEIDXMLfile)
        return DEIDXMLfile

def resetControlCodes(contents):
    '''Replace all control code tags we created by the actual control codes
    e.g. <newline> is replaced by \n again'''    
    translations={"<newline>":"\n", "<tab>":"\t", "<page>":"", "<horline>":"___"}
    for x,y in translations.items():
        contents=contents.replace(x,y)
    return contents

def save2XML(entries, XMLfile):
    fieldCONTENTS = "<field name=\"%s\">%s</field>"
    docCONTENTS = "<doc>\n%s\n</doc>"

    if os.path.isfile(XMLfile): os.remove(XMLfile)
    with open(XMLfile, "w") as fo:
        fo.write("<add>")
        fo.write("\n")
    
    for entry in entries:
        with open(XMLfile, "a") as fo:
            doc = []
            for k,v in entry.items():
                v = v.replace("&","&amp;").replace(">","&gt;").replace("<","&lt;")
                doc.append( fieldCONTENTS %(k,v) )
            
            fo.write( text_util.stripControlCodesString(str( docCONTENTS %("\n".join(doc)) )) )

    with open(XMLfile, "a") as fo:
        fo.write("\n")
        fo.write("</add>")
        fo.write("\n")

def save2XMLold(entries, XMLfile):
    fieldCONTENTS = "<field name=\"%s\">%s</field>"
    docCONTENTS = "<doc>\n%s\n</doc>"

    if os.path.isfile(XMLfile): os.remove(XMLfile)
    with open(XMLfile, "w") as fo:
        fo.write("<add>")
        fo.write("\n")
        for entry in entries:
            doc = []
            for k,v in entry.items():
                v = v.replace("&","&amp;").replace(">","&gt;").replace("<","&lt;")
                doc.append( fieldCONTENTS %(k,v) )
            
            fo.write(docCONTENTS %("\n".join(doc)))
        fo.write("\n")
        fo.write("</add>")
        fo.write("\n")

if __name__ == "__main__":

    if len(sys.argv) > 1:
        OFFLOAD_START = sys.argv[1] # e.g. "04/2004"
        OFFLOAD_END = sys.argv[2] # e.g. "05/2004" (excl.)
        try:
            DEID = sys.argv[3] # True or False
        except:
            from dynamicConfig import DEID
        from dynamicConfig import LOGFILE
    else:
        print 'Please define OFFLOAD_START, OFFLOAD_END, DEID as commandline arguments (e.g. python src/monthlyUpdate.py "04/2014" "05/2014" False)'
        sys.exit()
	
    start=time.time()
    
    '''First step: start the offload from the database'''
    TXTfiles = startOffload(OFFLOAD_START, OFFLOAD_END, BASE_OFFLOAD_FOLDER, DB)

    '''Checking whether SOLR is running is necessary on VM'''
    if CHECK_SOLR_STATUS:
        try:
            urllib.urlopen(SOLR_BASE_URL)
            pass
        except:
            os.chdir(SOLR_BASE_DIR)
            os.system(" ".join(["java", "-jar", "-server", "-Xmx2000M", "-Dfile.encoding=UTF8", "-Djava.headless=True", "start.jar &"]))

    '''
    Per extracted *.txt file, perform
    - Second step: transform C2M dump (in |-separated RTF and txt) into XML format for SOLR, with or without de-identification
    - Third step: add the XML file to the relevant (i.e. de-identified or not) SOLR index
    '''
    for TXTfile in TXTfiles:
        print "working on", TXTfile
        XMLfileDEID = generateXML(TXTfile, DEID=True)
        print "done generating", XMLfileDEID

        os.chdir(SOLR_POST_DIR)
        if DEID:
			proc = subprocess.Popen(["java", "-Durl=%s" %UPDATE_DEID_URL, "-jar", "post.jar", XMLfileDEID], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			if proc.stderr.read() != '':
				with open(LOGFILE, "a") as logf:
					logf.write(str(time.asctime()) + "\tfailed to index" + XMLfileDEID + "\n" + str(proc.stderr.read()))
			else:
				success=True
				os.remove(XMLfileDEID)
        else:
			proc = subprocess.Popen(["java", "-Durl=%s" %UPDATE_ORIG_URL, "-jar", "post.jar", XMLfileNODEID], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			if proc.stderr.read() != '':
				with open(LOGFILE, "a") as logf:
					logf.write(str(time.asctime()) + "\tfailed to index" + XMLfileNODEID + "\n" + str(proc.stderr.read()))
			else:
				success=True
				os.remove(XMLfileNODEID)
        if success: os.remove(TXTfile)
    
    print "total time spent", time.time()-start