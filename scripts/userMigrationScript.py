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
    dbName="demo2"
    
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
with open('community2csv', 'rb') as f:
    reader = csv.reader(f)
    data = list(reader)

# Step2: Initialize database.
(conn, cur) = connect()

# Sample queries.
newUserSql = "INSERT INTO User (username, password, email, partyId, partnerId, userIdentifier) VALUES (%s, %s, %s, %s, %s, %s)"
updateUserSql = "UPDATE User SET password=%s, email=%s, partnerId=%s, userIdentifier=%s WHERE username=%s"
partySql = "INSERT INTO Party (partyType, name) VALUES ('user', %s)"
countSql = "SELECT COUNT(*) FROM User WHERE username=%s"

partnerId = 'tair'
batchCount = 0
totalCount = 0
# Step 3: Main loop
for entry in data:
    totalCount += 1
    batchCount += 1
    communityId = entry[0]
    email = entry[1]
    username = entry[2]
    digestedPw = create_signature(entry[3])

    # determine if username already existed in API service database.
    cur.execute(countSql, (username))
    numUsername= cur.fetchall()[0][0]

    if numUsername == 0:
        # username not exist, create new Party and User entry.
        cur.execute(partySql, username)
        partyId = conn.insert_id()
        cur.execute(newUserSql, (username, digestedPw, email, partyId, partnerId, communityId))
    else:
        # username already exist, only update the User entry.
        cur.execute(updateUserSql, (digestedPw, email, partnerId, communityId, username))

    # Does 500 queries per transaction for performance improvement.
    if batchCount >= 500:
        print "total commit %s" % totalCount
        conn.commit()
        batchCount = 0
    
conn.commit()
