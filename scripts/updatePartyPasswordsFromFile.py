#!/usr/bin/python
import hashlib
import MySQLdb
import sys
import warnings

# Process a tab-delimited file, passwords.tsv, containing 
# party IDs and clear passwords, updating the Credential of 
# the party with the encrypted password.

## TODO redo this as Django script, using standard view encryption rather than 
## hard-coded version here--risky. If necessary code view function to call.

# function to connect to API database.
def connect():
    host = 'phoenix-api.cwyjt5kql77y.us-west-2.rds.amazonaws.com'
    user="phoenix"
    password="password"
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

# Open and load the file.
with open('passwords.tsv', 'rb') as f:
    data = []
    for line in f:
        data.append(line)

# Connect to the database.
(conn, cur) = connect()

passwordSql = "UPDATE Credential SET password = '%s' WHERE partyId = %s;"
totalCount = 0

# Get and encrypt the password and update the party in the database.
for line in data:
    if "'" in line:
        line = line.replace("'","''")
    entry = line.split('\t')
    partyId = entry[0]
    digestedPw = create_signature(entry[1])
    if digestedPw.rstrip() == '':
        continue
    totalCount += 1

    # Execute the update.
    try: 
        cur.execute(passwordSql%(digestedPw,partyId,))
    except:
        print("Party {} -- exception: {}".format(partyId, sys.exc_info()[0]))

# Commit the transaction.
conn.commit()

print("total passwords updated: %s" %totalCount)
