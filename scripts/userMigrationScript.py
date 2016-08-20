#!/usr/bin/python
import hashlib
import MySQLdb

# This is a very crude script that takes in a CSV file downloaded from the Community
# table of TAIR's Oracle database, and upload to API's database. The following formats are assumed
# for the CSV file:
# communityId,email,username,password
# 
# The source password is assuemd to be in plain text, and will be hashed before uploading to API
# server's database.

# function to connect to api database.
def connect():
    host = 'phoenix-api-test.cwyjt5kql77y.us-west-2.rds.amazonaws.com'
    user="phoenix"
    password="xrXbTZfrHdwmS7VC"
    dbName="phoenix_api"
    
    conn = MySQLdb.connect(host=host,
                         user=user,
                         passwd=password,
                        db=dbName)
    cur = conn.cursor()
    return conn, cur

# function to hash password
def create_signature(password):
    password = password.rstrip()
    return hashlib.sha1(password).hexdigest()


# Begin main program:

# Step1: Open the source CSV file and load into memory.
with open('users.txt', 'rb') as f:
    data = f

# Step2: Initialize database.
(conn, cur) = connect()

# Sample queries.
newUserSql = "INSERT INTO Credential (username, password, email, partyId, partnerId, userIdentifier, firstName, lastName) VALUES ('%s', '%s', '%s', %s, '%s', '%s', '%s', '%s');"
partySql = "INSERT INTO Party (partyType, name, display, countryId, label) VALUES ('user', '%s', False, NULL, NULL);"

partnerId = 'biocyc'
totalCount = 0
batchCount = 0
# Step 3: Main loop
for line in data:
    entry = line.split('\t')
    userIdentifier = entry[0]
    username = entry[1]
    email = entry[1]
    digestedPw = create_signature(entry[2])
    fullName = entry[3]
    firstName = entry[4]
    lastName = entry[5]
    if username.rstrip() == '':
        continue
    totalCount += 1
    batchCount += 1
    try: 
        cur.execute(partySql%(fullName,))
        partyId = conn.insert_id()
        cur.execute(newUserSql%(username, digestedPw, email, partyId, partnerId, userIdentifier, firstName, lastName))
    except:
        print username


    # Does 500 queries per transaction for performance improvement.
    if batchCount >= 500:
        print "total commit %s" % totalCount
        conn.commit()
        batchCount = 0

    
conn.commit()
