from properties import propertyData, insertProperty, selectAll

#make connection to database and get cursor
cur, con = propertyData('', 'root', "", 'cityProperties')

#for fun lets insert a property
#insertProperty('5161286', '32', 'Wolfgang', 'Drive', 0, 0, cur)

#commit changes and close Database
#con.commit()

print selectAll(cur, 'properties')
con.close()
