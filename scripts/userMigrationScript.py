#!/usr/bin/python
import csv
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
    host = 'paywall2.cwyjt5kql77y.us-west-2.rds.amazonaws.com'
    user="phoenix"
    password="phoenix123"
    dbName="demo1"
    
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
with open('community.csv', 'rb') as f:
    reader = csv.reader(f)
    data = list(reader)

# Step2: Initialize database.
(conn, cur) = connect()

# Sample queries.
newUserSql = "INSERT INTO Credential (username, password, email, partyId, partnerId, userIdentifier) VALUES (%s, %s, %s, %s, %s, %s)"
partySql = "INSERT INTO Party (partyType, name, display, countryId) VALUES ('user', %s, %s, %s)"

partnerId = 'tair'
totalCount = 0
batchCount = 0
# Step 3: Main loop
for entry in data:
    communityId = entry[0]
    communityType = entry[1]
    email = entry[2]
    username = entry[4]
    digestedPw = create_signature(entry[5])
    isObsolete = entry[6]
    if not communityId.isdigit():
        continue
    if not communityType == 'person':
        continue
    if username.rstrip() == '':
        continue
    if isObsolete == 'T':
        continue
    totalCount += 1
    batchCount += 1
    try: 
        cur.execute(partySql, (username, True, 10))
        partyId = conn.insert_id()
        cur.execute(newUserSql, (username, digestedPw, email, partyId, partnerId, communityId))
    except:
        print username


    # Does 500 queries per transaction for performance improvement.
    if batchCount >= 500:
        print "total commit %s" % totalCount
        conn.commit()
        batchCount = 0

    
conn.commit()
