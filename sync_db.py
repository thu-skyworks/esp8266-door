#!/usr/bin/env python3

import datetime
import pymssql
from peewee import SelectQuery
from db_models import *

DB_Init()

class TempAccountInfo(AccountInfo):
    class Meta:
        db_table = 'temp_accout_info'

tmp_tbl = TempAccountInfo._meta.db_table
acct_tbl = AccountInfo._meta.db_table

mysql_db.execute_sql('CREATE TEMPORARY TABLE {} SELECT * FROM {} LIMIT 0'.format(tmp_tbl,acct_tbl))

# Connect to MSSQL Server 
conn = pymssql.connect(server=config.UPSTREAM_DB_SERVER, 
                       user=config.UPSTREAM_DB_U, 
                       password=config.UPSTREAM_DB_P, 
                       database=config.UPSTREAM_DB_NAME) 
 
# Create a database cursor 
cursor = conn.cursor() 
 
# Replace this nonsense with your own query :) 
query = config.UPSTREAM_DB_SQL
 
# Execute the query 
cursor.execute(query)

data_source=[]
for row in cursor:
    if len(row[0])>0 and len(row[2])>0:
        data_source.append({
            'realname':  row[1],
            'studnum':   row[0],
            'cardnum':   row[2],
            'cardtype':  row[3],
            'userid':    row[4],
            })

# Close the cursor and the database connection 
cursor.close() 
conn.close()

print("%d records in total" %(len(data_source)))

with mysql_db.atomic():
    TempAccountInfo.insert_many(data_source).execute()

print("%d records in temp table" %(SelectQuery(TempAccountInfo).count()))

cursor = mysql_db.get_cursor()
cursor.execute('UPDATE {0} INNER JOIN {1} ON {0}.studnum = {1}.studnum SET {0}.cardnum = {1}.cardnum WHERE {0}.cardnum != {1}.cardnum'.format(acct_tbl,tmp_tbl))
print("%d records updated" % (mysql_db.rows_affected(cursor)))
cursor.execute('INSERT IGNORE INTO {0} SELECT * FROM {1}'.format(acct_tbl,tmp_tbl))
print("%d new records added" % (mysql_db.rows_affected(cursor)))
mysql_db.commit()
