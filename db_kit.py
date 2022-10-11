import pymysql
import time

class db_kit(object):

    def __init__(self, host,user,passwd,db,charset):
        self.result = None
        self.set_mysql_param(host, user, passwd, db, charset)

 #'37.140.198.125', 'nasha10', '256celeron', 'nasha10', 'utf8'
    def set_mysql_param(self,host,user,passwd,db,charset):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.dbasa = db
        self.charset = charset

    def sql_zapros(self,sql_z):
        db = pymysql.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.dbasa, charset=self.charset)
        self.cur = db.cursor()
        self.cur.execute(sql_z)
        result = self.cur.fetchall()
        db.close()
        return result

    def guaranteed_query(self,zapros):
        i = 5
        while True:
            try:
                self.result = self.sql_zapros(zapros)
                return True
            except :
                i -= 1
                time.sleep(1)
                if i<0 : 
                    return False
            

