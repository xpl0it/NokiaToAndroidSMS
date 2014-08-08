################################################################################################################
# VMGtoXML.py to convert VMG files in a particular directory to an XML format understandable by
# SMS Backup and Restore (https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore&hl=en)
# application for Android
#
# Before you run this script, make sure you edit the Dictionary of contact numbers and their corresponding names
# Doing this will populate the XML file with names which would be shown up once imported into Android.
#
# v1.7
# Adding functionalities to process both Sent and Received messages
#
# v1.6
# * Using lxml to create xml files
#
# v1.4
# * All special characters converted to their HTML equivalents in the Body section
# * Used python dictionary (key-value pairs) for looking up names for the contact number 
################################################################################################################

from sys import argv
import os, os.path, glob
from datetime import datetime
import time
from lxml import etree

line1 = "" # Individual lines in the VMG file
smsCount = len(glob.glob1(".","*.vmg")) # Total count of VMG files. Reflects the total number of SMS

# ------------------------------------------------------------
# Variables for XML file
protocol = "0" 			# Fixed
address = "" 			# Variable. Set in the following code
date = "" 				# Variable. Set in the following code
type = ""				# Variable. Type 2 = Sent. Type 1 = Received
subject = "null"		# Fixed
body = ""				# Variable. Set in the following code
toa = ""				# Variable. Set in the following code
sc_toa = ""				# Fixed
service_center = "null"	# Variable
read = ""				# Variable. Based on X-IRMC-STATUS. If READ, then read=0
status = "-1"			# Fixed. 1
locked = "0"			# Fixed. 0
date_sent = "null"		# Fixed.
readable_date = ""		# Fixed. Set in the following code. Jul 3, 2011 11:23:16 AM
#------------------------------------------------------------
contact_name = ""	# Variable
body_value = 14		# Fixed

##############################################
# Edit this before running this script
##############################################
contactNameNumberDictionary = {"+1234567890":"John Doe", "+0987654321":"Jane Doe"}

XMLbegin = """<?xml version=\'1.0\' encoding=\'UTF-8\' standalone=\'yes\' ?>
<?xml-stylesheet type="text/xsl" href="sms.xsl"?>
"""

dir = '.'

rootElement = etree.Element("smses", count="\'%d\'" % smsCount)
#rootElement = etree.Element("root")

smsCount = 0

for root, dirs, filenames in os.walk(dir):
	for vmgfile in filenames:
		line = ""
		line1 = ""
		if ".vmg" in vmgfile:
			print "File: ", vmgfile
			smsCount += 1
			try:
				inputfile = open(vmgfile, "r")
				byte = inputfile.read(1)
				while byte != "":
					# Do stuff with byte.
					if byte.strip() != "\x00":
						line1+=str(byte)
					byte = inputfile.read(1)
			finally:
				inputfile.close()

			#with open('3.txt', 'w') as outfile:
			#	outfile.write(line1)

			protocol = "0" 		# Fixed
			address = "" 		# Variable. Set in the following code
			date = "" 			# Variable. Set in the following code
			type = ""			# Variable. Set in the following code
			# Type 2 = Sent
			# Type 1 = Received
			subject = "null"		# Fixed
			body = ""			# Variable. Set in the following code
			body_value = 14		# Fixed
			toa = "0"			# Variable. Set in the following code
			sc_toa = "0"			# Fixed
			service_center = ""	# Variable
			read = ""			# Variable. Based on X-IRMC-STATUS. If READ, then read=0
			status = "-1"			# Fixed. 1
			# Status -1 = Received
			# Status 0 = Sent
			locked = "0"		# Fixed. 0
			date_sent = "null"		# Fixed.
			readable_date = ""	# Variable. Set in the following code. Jul 3, 2011 11:23:16 AM
			contact_name = "(Unknown)"	# Variable
			lines = []

			for line in line1.split('\n'):
				lines.append(line)
				## From
				if line.find("TEL") != -1:
					address = line[line.find("TEL:")+4:]
					if (address.strip() != ""):
						print "Address: ", str(address)
						contact_name = contactNameNumberDictionary[address]
				
				## Type = Sent or Received
				## DELIVER = Received. SUBMIT = Sent.
				## Type 1 = Received	Status -1 = Received
				## Type 2 = Sent		Status 0 = Sent
				if line.find("X-MESSAGE-TYPE") != -1:
					print "Line: ", line
					if line.find("SUBMIT") != -1:
						print "Message was sent"
						type = 2
						status = 0
					elif line.find("DELIVER") != -1:
						print "Message was received"
						type = 1
						status = -1

				## Date
				if line.find("Date") != -1:
					date_human = datetime.strptime(line[line.find("DATE:")+6:], "%d.%m.%Y %H:%M:%S") # "11.06.2011 10:30:12"
					#date_sent = time.mktime(date_human.timetuple())
					date = long(time.mktime(date_human.timetuple()) * 1000 + date_human.microsecond / 1000)
					readable_date = datetime.strptime(str(date_human), "%Y-%m-%d %H:%M:%S").strftime('%b %d, %Y %I:%m:%d %p')
				
				text = "BEGIN:VBODY"
				for i, lineSearch in enumerate(lines, 1):
					if text in lineSearch:
						body_value = i+1
				
				if line.find("END:VBODY") != -1:
					while lines[body_value] != "END:VBODY":
						body += lines[body_value]
						if lines[body_value+1] != "END:VBODY":
							body = body.strip()
							# body += '&#10;&#13;'
						body_value += 1
				
				if line.find("X-IRMC-STATUS") != -1:
					if line.find("READ") != -1:
						read = 0
					else:
						read = 1
		
			print "Done"
			print "-------------Written-------------- Now creating XML"
			
			rootElement.append(etree.Element('sms', protocol = str(protocol), address = str(address), date = str(date), type = str(type), subject = str(subject), body = str(body.strip()), toa = str(toa), sc_toa = str(sc_toa), service_center = str(service_center), read = str(read), status = str(status), locked = str(locked), date_sent = str(date_sent), readable_date = str(readable_date), contact_name = str(contact_name)))

print "Done %d. Now writing to file" % (smsCount)
outputfile = open(".\\xmlfile.xml", "w")
outputfile.write(XMLbegin + etree.tostring(rootElement, pretty_print=True))
outputfile.close()
