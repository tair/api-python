#!/usr/bin/python
import MySQLdb

def connect():
    host = 'phoenix-api-test.cwyjt5kql77y.us-west-2.rds.amazonaws.com'
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
cur.execute("ALTER TABLE Credential MODIFY username VARCHAR(32) CHARACTER SET utf8 COLLATE utf8_bin")
conn.commit()
