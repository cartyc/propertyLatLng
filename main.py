from properties import propertyData, insertProperty, workit

#make connection to database and get cursor
cur, con = propertyData('localhost', 'root', "1346", 'cityProperties')

#for fun lets insert a property
#insertProperty('5161286', '32', 'Wolfgang', 'Drive', 0, 0, cur)

#commit changes and close Database
#con.commit()
workit("mainAddr.csv", con, cur)

con.close()
