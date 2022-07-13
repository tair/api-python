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
    host =  'phoenix-api-test.cwyjt5kql77y.us-west-2.rds.amazonaws.com'
    user="phoenix"
    password="password"
    dbName="demo1"

    conn = MySQLdb.connect(host=host,
                         user=user,
                         passwd=password,
                        db=dbName)
    cur = conn.cursor()
    return conn, cur

(conn, cur) = connect()

with open('country.csv', 'rb') as f:
    reader = csv.reader(f)
    data = list(reader)

batchCount = 0
totalCount = 0
# Step 3: Main loop
for entry in data:
    totalCount += 1
    batchCount += 1
    countryName = entry[1]

    # determine if username already existed in API service database.
    sql = "INSERT INTO Country (name) VALUES (%s)"
    cur.execute(sql, (countryName))

    # Does 500 queries per transaction for performance improvement.
    if batchCount >= 500:
        print("total commit %s" % totalCount)
        conn.commit()
        batchCount = 0

conn.commit()
