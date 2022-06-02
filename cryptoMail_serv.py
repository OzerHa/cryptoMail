from package.crychatFunction import *
from socket import *
import threading, sqlite3, time, uuid
from datetime import datetime, timedelta


ipServeur = ''
portServeur = 15555
buffer = 2048
lock = threading.Lock()
master = "6dIs2O1C6UQ4RfFoifbMl/rD0ViSlGB5HixJ3FBOZpo="
tEncode =  "%Y-%m-%d %H:%M:%S"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Initialisation(threading.Thread):
    def __init__(self):
        global transMessage
        threading.Thread.__init__(self)
        try:
            # initialisation de la class
            gestConnexion = gestionConnexion(sock,buffer,True)
            AesSessionKey, separator = gestConnexion.gestionConnexionServeur()
            transMessage = transfertMessage(sock,buffer,separator,AesSessionKey,'serveur')
            m = main()
            m.start()
        except:
            pass

class generateKey(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.db = dataBase()

    def run(self):
        while True:
            timeChange = datetime.strptime(str(self.db.getTime()+timedelta(minutes=1)), tEncode)
            if timeChange < datetime.now():
                self.db.updateDB()
                print("DB update at: " + str(datetime.now()))
            else:
                tSleep = 60 - int(str(datetime.now().second)) 
                print('lets sleep for: ',tSleep)
                time.sleep(tSleep)
                self.db.cleanDb()
            

class main(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.db = dataBase()
        self.transfertMessage = transMessage
        

    def run(self):
        while True:
            try:
                msg = self.transfertMessage.recvMessage()
            except ValueError:
                sys.exit()
            except ConnectionResetError:
                print("client deconnecte")
            typeMesg = getType(msg)

            if typeMesg == 'check in db':
                check = self.db.checkInDb(eval(msg[-1])[-1])
                self.transfertMessage.send('',str(check))
            elif typeMesg == 'add in db':
                self.db.addInDb(msg[-1])
            elif typeMesg == 'get key time':
                key = self.db.getKeyTime(msg[-1])
                if key == "":
                    self.transfertMessage.send('Error','')
                else:
                    self.transfertMessage.send('Succes',key)

class dataBase:
    def __init__(self):
        if not os.path.exists('user.db'):
            try:
                self.conn =  sqlite3.connect('user.db', check_same_thread=False)
                self.cursor = self.conn.cursor()
                self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Main(
                mail TEXT
                )
                """)
                self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Keys(
                key TEXT,
                uuid TEXT,
                timeBegin TEXT,
                use INT
                )
                """)
                self.conn.execute("""
                    INSERT INTO Keys(key,uuid,timeBegin,use) VALUES(?,?,?,?)
                """,(str(genKey()),str(uuid.uuid4()),"2022-5-16 00:00:00",0,))
                self.conn.commit()
            except:
                os.remove('user.db')
        else: 
            self.conn = sqlite3.connect('user.db', check_same_thread=False)
            self.cursor = self.conn.cursor()
    
    def addInDb(self, email):
        try:
            lock.acquire(True)
            self.cursor.execute("""
            INSERT INTO main(mail) VALUES(?)""",(email,))
            self.conn.commit()
        finally:
            lock.release()

    def checkInDb(self, email):
        try:
            lock.acquire(True)
            self.cursor.execute("""
            SELECT mail FROM main""")
            rows = self.cursor.fetchall()
            try:
                emailDB = rows[0]
            except IndexError:
                return False
        finally:
            lock.release()
        if email in emailDB:
            return True
        else:
            return False
    
    def cleanDb(self):
        try:
            lock.acquire(True)
            self.cursor.execute("""DELETE FROM Keys WHERE use = ?""",(0,))
            self.conn.commit()
        finally:
            lock.release()

    def getTime(self):
        try:
            lock.acquire(True)
            self.cursor.execute("""
            SELECT timeBegin FROM Keys""")
            rows = self.cursor.fetchall()
            last = rows[-1][-1]
        finally:
            lock.release()
        try:
            return datetime.strptime(last, tEncode)
        except IndexError or ValueError:
            return 0

    def updateDB(self):
        try:
            lock.acquire(True)
            self.conn.execute("PRAGMA busy_timeout = 3000")
            dTime = datetime.now()
            yearT = dTime.year
            monthT = dTime.month
            dayT = dTime.day
            hourT = dTime.hour
            minuteT = dTime.minute
            month, day, hour, minute = dataBase.cleanTime(monthT,dayT,hourT,minuteT)
            a = str(yearT)+"-"+month+"-"+day+" "+hour+":"+minute+":00"
            self.cursor.execute("""
            INSERT INTO Keys(key,uuid,timeBegin,use) VALUES(?,?,?,?)"""
            ,(str(genKey()),str(uuid.uuid4()),a,0,))
            self.conn.commit()
        finally:
            lock.release()
    
    def getKeyTime(self,time):
        try:
            dTime = datetime.strptime(time, tEncode)
            yearT = dTime.year
            monthT = dTime.month
            dayT = dTime.day
            hourT = dTime.hour
            minuteT = dTime.minute
            lock.acquire(True)
            month, day, hour, minute = dataBase.cleanTime(monthT,dayT,hourT,minuteT)
            a = str(yearT)+"-"+month+"-"+day+" "+hour+":"+minute+":00"
            self.cursor.execute("""SELECT uuid FROM Keys WHERE timeBegin = ?""", (a,))
            UUID = self.cursor.fetchall()[0][0]
            self.cursor.execute("""SELECT key FROM Keys WHERE uuid = ?""", (UUID,))
            keys = self.cursor.fetchall()[0][0]
            self.cursor.execute("""SELECT use FROM Keys WHERE uuid = ?""",(UUID,))
            use = self.cursor.fetchall()[0][0]
            use = use + 1
            self.cursor.execute("""UPDATE Keys SET use = ? WHERE uuid = ?""",(use,UUID,))
            self.conn.commit()
            lock.release()
            return chiffrementAES.decryptAes(keys,master)
        except ValueError or ValueError:
            print("Pas encoder")
            return ""
        
    
    @staticmethod
    def cleanTime(monthT,dayT,hourT,minuteT):
        month = ""
        day = ""
        hour = ""
        minute = ""
        if int(str(monthT)) < 10:
            month = "0"+str(monthT)
        else:
            month = str(monthT)
        if int(str(dayT)) < 10:
            day = "0"+str(dayT)
        else :
            day = str(dayT)
        if int(str(hourT)) < 10:
            hour = "0"+str(hourT)
        else:
            hour = str(hourT)
        if int(str(minuteT)) < 10:
            minute = "0"+str(minuteT)
        else :
            minute = str(minuteT)
        return month, day, hour, minute



def getType(msg):
    return msg[1]  

def genKey():
    a = chiffrementAES.getMyAesSessionKey()
    b = chiffrementAES.encryptAes(a,master)
    return b.decode("utf-8")

if __name__ == '__main__':
    g = generateKey()
    g.start()
    so = socket(AF_INET,SOCK_STREAM)
    so.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    so.bind(('',portServeur))
    while True:
        so.listen(5)
        (sock, (ipClient, portClient)) = so.accept()
        thread = Initialisation()
        thread.start()