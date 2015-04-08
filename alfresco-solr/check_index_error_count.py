#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
Project     :       Apache Solr Health Check
Version     :       1.0
Author      :       Gurvinder Dadyala
Summary     :       This program is a nagios plugin that check Index error count
Dependency  :       Linux/nagios/Python-2.6
Info 		    : 		  zero value means index is upto date. 
 
Usage :
```````
shell> python check_index_error_count.py
'''
 
#-----------------------|
# Import Python Modules |
#-----------------------|
import os, sys, urllib
from xml.dom import minidom
from optparse import OptionParser
 
#--------------------------|
# Main Program Starts Here |
#--------------------------|
# Command Line Arguments Parser

cmd_parser = OptionParser(version="%prog 0.1")
cmd_parser.add_option("-H", "--host", type="string", action="store", dest="solr_host", help="SOLR Server host, e.g locahost")
cmd_parser.add_option("-P", "--port", type="string", action="store", dest="solr_port", help="SOLR Server Port, e.g 8080")
cmd_parser.add_option("-w", "--warning", type="long", action="store", dest="solr_warn", help="SOLR Index error count warning count, e.g 500")
cmd_parser.add_option("-c", "--critical", type="long", action="store", dest="solr_critical", help="SOLR Index error count critical count, e.g 1000")


(cmd_options, cmd_args) = cmd_parser.parse_args()
# Check the Command syntax
if not (cmd_options.solr_host and cmd_options.solr_port and cmd_options.solr_warn and cmd_options.solr_critical):
    cmd_parser.print_help()
    sys.exit(3)

# Collect Solr Statistics Object
# http://localhost/report-alfresco.xml
#http://localhost:8080/solr/admin/cores?action=REPORT&wt=xml
#url="http://localhost/report-alfresco.xml"
url = "http://"+cmd_options.solr_host+":"+cmd_options.solr_port+"/solr/admin/cores?"+urllib.urlencode({'action': 'REPORT', 'wt': 'xml'})

#print(url)

try:
	response=urllib.urlopen(url).read()
except IOError:
	print "ERROR:Cannot connect to server"
	sys.exit(3)

#print response
xmlResponse = minidom.parseString(response)
elements = xmlResponse.getElementsByTagName('lst')
#print(len(entries)) #4 entries 
#print(elements[2].attributes['name'].value) #output is alfresco
alfrescoElement = elements[2]
if alfrescoElement.getAttribute('name') != "alfresco":
  print "UNKNOWN:Valid Tag not Found, Check XML response"
  sys.exit(3)

#print(alfrescoElement.getElementsByTagName('long'))
longElements = alfrescoElement.getElementsByTagName('long')

#ELEMENT API Reference https://docs.python.org/2/library/xml.dom.html#dom-element-objects
indexErrorCountElement = "NULL"

for longElementSingle in longElements:
  #print longElementS.getAttribute('name')
  elementAttr = longElementSingle.getAttribute('name')
  if elementAttr=="Index error count":
    #print "Element Found"
    #print longElementSingle.getAttribute('name')
    indexErrorCountElement = longElementSingle


if indexErrorCountElement != "NULL":
  #print (indexErrorCountElement.firstChild.data)
  indexErrorCount = indexErrorCountElement.firstChild.data
else:
  print "UNKNOWN:Valid Tag not Found, Check XML response"
  sys.exit(3)

if long(indexErrorCount)==0:
	print "INFO:No Issues with Index, Index error count= "+str(indexErrorCount)+"| i_err_count="+str(indexErrorCount)
	sys.exit(0)
elif long(indexErrorCount) >= long(cmd_options.solr_warn) and long(indexErrorCount) < long(cmd_options.solr_critical):
	print "WARNING:There is an issue with the index, Index error count = "+str(indexErrorCount)+"| i_err_count="+str(indexErrorCount)
	sys.exit(1)
elif long(indexErrorCount) >= long(cmd_options.solr_critical):
	print "CRITICAL:There is an issue with the index, Index error count = "+str(indexErrorCount)+"| i_err_count="+str(indexErrorCount)
	sys.exit(2)
elif long(indexErrorCount) < 0:
	print "UNKNOWN:Invalid Index error count, Index error count = "+str(indexErrorCount)+"| i_err_count="+str(indexErrorCount)
	sys.exit(3)	


