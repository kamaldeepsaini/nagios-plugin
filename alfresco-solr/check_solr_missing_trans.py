#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
Project     :       Apache Solr Health Check
Version     :       1.0
Author      :       Gurvinder Dadyala
Summary     :       This program is a nagios plugin that check Count of missing transactions from the Index
Dependency  :       Linux/nagios/Python-2.6
Info 		: 		zero value means index is upto date. 
 
Usage :
```````
shell> python check_solr_index.py
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
#cmd_parser.add_option("-w", "--warning", type="long", action="store", dest="solr_warn", help="SOLR remaining transaction warning count, e.g 500")
#cmd_parser.add_option("-c", "--critical", type="long", action="store", dest="solr_critical", help="SOLR remaining transaction critical count, e.g 1000")

(cmd_options, cmd_args) = cmd_parser.parse_args()
# Check the Command syntax
if not (cmd_options.solr_host and cmd_options.solr_port and cmd_options.solr_warn and cmd_options.solr_critical):
    cmd_parser.print_help()
    sys.exit(3)



url = "http://"+cmd_options.solr_host+":"+cmd_options.solr_port+"/solr/admin/cores?"+urllib.urlencode({'action': 'REPORT', 'wt': 'xml'})
#print(url)
response=urllib.urlopen(url).read()
#print response
solr_all_stat = minidom.parseString(response)
#solr_all_stat = minidom.parseString(urllib.urlopen("https:///").read())
entries = solr_all_stat.getElementsByTagName('lst')
#print(len(entries)) #4 entries 
#print(entries[1].attributes['name'].value)
#print(entries[1].childNodes[0].toxml())
node = entries[1].childNodes[0]
node = node.childNodes
#print(node.length)
#print(node.item(6).toxml())
#print(node.item(6).nodeName)
#print(node.item(6).firstChild.data)
indexCount = long(node.item(6).firstChild.data)
#print(indexCount)

#summary_url="http://192.168.100.243:8080/solr/admin/cores?action=summary&wt=xml"
summary_url = "http://"+cmd_options.solr_host+":"+cmd_options.solr_port+"/solr/admin/cores?"+urllib.urlencode({'action': 'summary', 'wt': 'xml'})
#print "url="+summary_url
summary_response=urllib.urlopen(summary_url).read()
#print summary_response
summary = minidom.parseString(summary_response)
entries_summary = summary.getElementsByTagName('long')
#print len(entries_summary)
#print entries_summary[65].toxml() #<long name="Approx transactions remaining">0</long>
#print entries_summary[65].firstChild.data
remain_trans = entries_summary[65].firstChild.data


if long(indexCount) == 0 and long(remain_trans) == 0:
	print("Index is up to date")
	sys.exit(0)
elif long(indexCount) > 0:
	if long(remain_trans) >= long(cmd_options.solr_warn) and long(remain_trans) < long(cmd_options.solr_critical):
		print("Warning:Background indexing in progress, Remaining Transactions Count= "+str(remain_trans)+"|r_transactions="+str(remain_trans))
		sys.exit(1)
	elif long(remain_trans) > long(cmd_options.solr_critical):
		print("Critical|Missing Transactions, Remaining Transactions Count= "+str(remain_trans)+"|m_transactions="+str(remain_trans))
		sys.exit(2)
elif long(indexCount) < 0:
	print("Missing Transactions Status Unknown, Remaining Transactions Count= "+str(remain_trans))
	sys.exit(3)
		



