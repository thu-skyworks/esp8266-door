from peewee import *
import datetime
import config

mysql_db = MySQLDatabase(config.DBNAME, user=config.DBUSER, passwd=config.DBPASS, charset="utf8mb4")

class BaseModel(Model):
    class Meta:
        database = mysql_db

class AccountInfo(BaseModel):
    realname = CharField()
    studnum = CharField(unique=True)
    cardnum = CharField(index=True,unique=True)
    cardtype= IntegerField()
    userid  = CharField()


class AccessRecords(BaseModel):
    realname = CharField(default='')
    studnum = CharField(default='')
    cardnum = CharField(default='')
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

