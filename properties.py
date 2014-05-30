import MySQLdb as sql
import urllib2
import csv
import sys
import os.path
import time
from xml.dom.minidom import parse
import re

#Connection
def propertyData(location, user, password, database):
	'''
	Returns connection object
	'''
	try:
		print "getting the connection"
		con = sql.connect(location, user, password, database)
		print "got the connection"
		cur = con.cursor()
		return cur, con

	except:

		con = sql.connect(location, user, password)
		cur = con.cursor()
		#create datebase
		cur.execute("CREATE DATABASE cityProperties")

		cur.execute("use cityProperties")

		cur.execute("CREATE TABLE properties (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, pin INT UNIQUE, addressNum INT, addressName varchar(255), addressType varchar(255), lat FLOAT(10,6), lng FLOAT(10,6))")

		return cur, con

#Select all properties
def selectAll(connection, table):

	connection.execute("Select * from %s" % table)
	data = connection.fetchall()

	return data

def insertProperty(pin, addressNum, addressName, addressType, lat, lng, connection):

	addressName = re.escape(addressName)
	connection.execute("INSERT INTO properties (pin, addressNum, addressName, addressType, lat, lng) values( %s, %s, '%s', '%s', %s, %s)" % ( pin, addressNum, addressName, addressType, lat, lng))

	return 0


#Get filename via sys

def stringClean(str):

	return str.replace(' ', '+')

def getLatLong( addrNum, addrName):

	address = stringClean(addrNum+addrName+',Ottawa,on')
	base = "http://maps.google.com/maps/api/geocode/xml?address=%s&sensor=false" % address
	try:
		response = urllib2.urlopen(base)

	
	except urllib2.HTTPError, e:
		#kick it back to the start. Sometimes it takes a couple of tries
		print 'HTTP'
		print e.code
		
	
	except urllib2.URLError, e:
		print 'URLError'
		print e.code

	finally:
		time.sleep(1)
		return response
		

def checkifExists(pin, database):

	database.execute("SELECT pin FROM properties WHERE pin = %s" % pin)

	result = database.fetchone()

	return result

def workit(filename, connection, database):
	'''
	takes two command line arguments
	filename --> csv file that contains the properties you want to get latlong's for
	output --> location of the saved csv file
	'''
	#Check if the import file exits
	if os.path.exists(filename):

		f = open(filename)
	
		#open out put file with ab so that you do not overwrite the existing file if it exists.
		#This will append if the file already exists

		#Set source file to reader
		reader = csv.reader(f)
		#Set new file to Writer
		lineCount = 0

		for row in reader:
			'''
			Header
			objectid, pin, addrNumber, LglUnit, AddrQual, 
			RoadName, RdNameFrench, RdType, RdDir, txtHght, txtRot,
			centroidX, centroidY

			Loop through Propery List
			Write to file every 100 records so that if something goes wrong along the way you
			capture some information
			'''
			if lineCount == 0:
				lineCount += 1 
			
			else:

				if checkifExists(row[1], database):
					#print "pass"
					#print lineCount
					lineCount += 1
					pass

				else:
					#try to get the information from google
					xml = parse( getLatLong(row[2],row[5]) )

					try:

						error = xml.getElementsByTagName('error_message')[0].firstChild.nodeValue
						print error 
						
						if error:

							print error
							print 'sleeping'
							time.sleep(60*60*24)
							continue


					except:
						lat = xml.getElementsByTagName('lat')[0].firstChild.nodeValue
						lng = xml.getElementsByTagName('lng')[0].firstChild.nodeValue
						
						try:
							insertProperty(row[1], row[2], row[5], row[7], lat, lng, database)

							if lineCount % 100:
								connection.commit()
							#increase count.
							lineCount += 1 

						except:

							continue

	else:
		#If source does not exist let user know
		f.close()
		print "File Does not exist."
