from properties import propertyData, insertProperty, workit

f = open('accounts.txt')
lines = f.readlines()

user = lines[0].strip()
password = lines[1].strip()
database = lines[2].strip()
host = lines[3].strip()

f.close()

#make connection to database and get cursor
cur, con = propertyData(host, user, password , database)

#for fun lets insert a property
#insertProperty('5161286', '32', 'Wolfgang', 'Drive', 0, 0, cur)

#commit changes and close Database
#con.commit()
workit("mainAddr.csv", con, cur)

con.close()
