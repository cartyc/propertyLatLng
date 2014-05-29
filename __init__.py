import MySQLdb as sql
import urllib2
import csv
import sys
import os.path
import time
from xml.dom.minidom import parse

#Connection
def propertyData():
	'''
	Returns connection object
	'''
	try:
		con = sql.connect('localhost', 'root', '1346', 'cityProperties')
		cur = con.cursor()
		return cur, con

	except:

		con = sql.connect('localhost', 'root', '1346')
		cur = con.cursor()
		#create datebase
		cur.execute("CREATE DATABASE cityProperties")

		cur.execute("use cityProperties")

		cur.execute("CREATE TABLE properties (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, addressNum INT, addressName varchar(255), addressType varchar(255), lat INT, lng INT)")

		return cur, con

#Select all properties
def selectAll(connection, table):

	connection.execute("Select * from %s" % table)
	data = connection.fetchall()

	return data

def insertProperty(addressNum, addressName, addressType, lat, lng, connection):

	connection.execute("INSERT INTO properties (addressNum, addressName, addressType, lat, lng) values( %s, '%s', '%s', %s, %s)" % ( addressNum, addressName, addressType, lat, lng))

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
		
def saveRecords(outfile,data):

	with open(outfile, 'aw') as csvfile:


		writer = csv.writer(csvfile)
		for line in data:
			writer.writerow(line)
	


def workit(filename, connection):
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
			print lineCount
			if lineCount == 0:
				lineCount += 1 
			
			else:
				print lineCount
				#try to get the information from google
				xml = parse( getLatLong(row[2],row[5]) )

				try:

					error = xml.getElementsByTagName('error_message')[0].firstChild.nodeValue
					print error 
					
					if error:
						print 'exceeded'
						print 'sleeping'
						print error
						time.sleep(60*60*24)
						continue


				except:
					lat = xml.getElementsByTagName('lat')[0].firstChild.nodeValue
					lng = xml.getElementsByTagName('lng')[0].firstChild.nodeValue
					
					insertProperty(row[2], row[5], row[7], lat, lng, connection)

					#increase count.
					lineCount += 1 

	else:
		#If source does not exist let user know
		f.close()
		print "File Does not exist."




#Run the script


database, connection = propertyData()

workit(sys.argv[1], database)


allProperties = selectAll(database, "properties")

for i in allProperties:
	print i

connection.commit()
connection.close()
