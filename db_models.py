from peewee import *
import datetime
import config

mysql_db = MySQLDatabase(config.DBNAME, user=config.DBUSER, passwd=config.DBPASS, charset="utf8mb4")

class BaseModel(Model):
    class Meta:
        database = mysql_db

class AccountInfo(BaseModel):
    realname = CharField(max_length=30)
    studnum = CharField(max_length=12,unique=True)
    cardnum = CharField(max_length=10,index=True,unique=True)
    cardtype= IntegerField()
    userid  = CharField(max_length=20)


class AccessRecords(BaseModel):
    realname = CharField(max_length=30,default='')
    studnum = CharField(max_length=12,default='')
    cardnum = CharField(max_length=10,default='')
    status = IntegerField()
    created = DateTimeField(index=True, default=datetime.datetime.now)

def DB_Init():
    mysql_db.connect() #连接数据库
    mysql_db.create_tables([AccountInfo, AccessRecords], safe=True)
    # AccountInfo.create(
    #             realname = 'good one',
    #             studnum  = '2017011234',
    #             cardnum  = '0000080801',
    #             cardtype = 2,
    #             userid = 'test',
    #             ).save()

