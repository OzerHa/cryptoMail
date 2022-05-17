from tkinter import *
from tkinter.messagebox import *
from package.crychatFunction import *
from socket import *
from datetime import datetime
import string, random, pyperclip, time

ipServeur = 'localhost'
portServeur = 15555
buffer = 2048
width = 1000
height = 400
geo = str(width)+'x'+str(height)
textDiscEmail = """
    Uniquement votre adresse email est collectée durant ce processus.
    Elle est collectée dans le but de permettre aux autres utilisateurs de pouvoir vous 
    envoyer des mails grâce à cette application.
    Vous pouvez mettre une adresse mail au hasard en cochant la case prévu à cette effet.
    Dans ce cas, personne ne pourra vous envoyer des messages cryptées via cette application.
    L'option "Sauvegarder votre adresse" stocke votre adresse dans un fichier sur votre ordinateur uniquement.
"""

textInform = """
    Que souhaitez-vous faire ?
"""

varSender = "Votre adresse mail"
varDesti = "Adresse mail du destinataire"

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

class lancement:
    def __init__(self,arg=0):
        global transf,sock,separator,AesSessionKey
        sock = socket(AF_INET, SOCK_STREAM)
        # connexion au serveur
        try:
            sock.connect((ipServeur,portServeur))
            g = gestionConnexion(sock, buffer,True)
            errors = gestionError(sock, buffer)
            try:
                AesSessionKey, separator = g.sendKeyLoginClient()  
            except ValueError as e:
                print(f"{bcolors.WARNING}[Error]: {bcolors.ENDC}"+str(e))
                del g
                del sock
                errors.RSAkeyFromat()
                lancement()
            transf = transfertMessage(sock, buffer, separator, AesSessionKey)
        except ConnectionRefusedError:
            print("Le serveur ne repond pas. Le programme va se fermer. Veuillez retenter plus tard")
            time.sleep(10)
            sys.exit()

class CheckEmail:
    def __init__(self):
        self.transfertMessage = transf
        self.root = Tk()
        self.root.title("CryptoMail")
        self.root.geometry(geo)
        self.root.resizable(0,0)
        self.placeLabel()
        self.root.mainloop()

    def placeLabel(self):
        self.check = Frame(self.root,bg='#ffffff')
        self.check.place(x=0,y=0,width=width,height=height)
        #loginLabel = Label(self.check,text="Entrez l'adresse mail du destinataire",font=('Arial',20),bg='#f7f7f7')
        #loginLabel.place(x=10,y=10,width=width-20,height=40)
        senderMail = StringVar()
        self.entryAccount = Entry(self.check,textvariable=senderMail,bg='#f7f7f7',font=('Arial',15))
        self.entryAccount.bind("<Button-1>", lambda event: self.clearEntry(self.entryAccount))
        self.mailSaved = CheckEmail.getEmailSave()
        self.entryAccount.insert(0,self.mailSaved)
        self.entryAccount.place(x=10,y=10,width=width-350,height=50)

        randomMail = IntVar()
        self.randomEmailCheck = Checkbutton(self.check, text='Adresse aléatoire',variable=randomMail, font=('Arial',10), command=lambda: CheckEmail.randomEmail(self,randomMail.get()))
        self.randomEmailCheck.place(x=width-330,y=20,width=130,height=30)

        saveEmail = IntVar()
        self.savedEmailCheck = Checkbutton(self.check, text='Sauvegarder votre adresse',variable=saveEmail, font=('Arial',10))
        if self.mailSaved != varSender:
            self.savedEmailCheck.config(state='disable')
        self.savedEmailCheck.place(x=width-190,y=20,width=180,height=30)
        
        destMail = StringVar()
        self.entryDestEmail = Entry(self.check,textvariable=destMail,bg='#f7f7f7',font=('Arial',15))
        self.entryDestEmail.bind("<Button-1>", lambda event: self.clearEntry(self.entryDestEmail))
        self.entryDestEmail.insert(0,varDesti)
        self.entryDestEmail.place(x=10,y=80,width=width-20,height=50)

        loginButton = Button(self.check,bd=0,bg='#f7f7f7',text='Verifier',activebackground='#f7f7f7',
        command= lambda: CheckEmail.sendEmail(self,senderMail.get(),destMail.get(),randomMail.get(),saveEmail.get()),font=('Arial',18))
        loginButton.place(x=width/2-50,y=150,width=100,height=50)

        testButton = Button(self.check,bd=0,bg='#f7f7f7',text='Tester',activebackground='#f7f7f7',
        command= lambda: CheckEmail.sendEmail(self,senderMail.get(),destMail.get(),randomMail.get(),saveEmail.get(),bp=True),font=('Arial',18))
        testButton.place(x=width-85,y=150,width=75,height=50)

        loginLabel = Label(self.check,text=textDiscEmail,font=('Arial',15),bg='#f7f7f7')
        loginLabel.place(x=10,y=210,width=width-20,height=180)

    def clearEntry(self,entry):
        if entry == self.entryAccount:
            self.savedEmailCheck.config(state='normal')
            self.randomEmailCheck.deselect()
        entry.delete(0, END)

    def randomEmail(self,check): 
        separator = '' 
        hexD = string.hexdigits
        ran = hexD
        i = random.randint(13,24)
        for loop in range(i):
            separator = separator + random.choice(ran)
        if ':' in separator:
            separator = separator.replace(':',';')
        separator = separator + "@random.com"
        self.entryAccount.delete(0, END)
        if check:
            self.entryAccount.insert(0,separator)
            self.savedEmailCheck.config(state='disable')
            self.savedEmailCheck.deselect()
        else: 
            self.entryAccount.insert(0,self.mailSaved)
            if self.mailSaved != varSender:
                self.savedEmailCheck.config(state='disable')

    def sendEmail(self,senderEmail,destMail,randomMail,saveEmail,bp=False):
        if not bp:
            if '@' not in senderEmail and '@' not in destMail and '.' not in destMail and '.' not in senderEmail:
                showerror('Informations incorrectes','Adresse mail invalide')
            if senderEmail == varSender:
                showerror('Informations incorrectes','Votre adresse mail est pas valable')
            elif destMail == varDesti:
                showerror('Informations incorrectes',"L'adresse mail du destinataire est pas valable")
            else:
                if saveEmail == 1: 
                    CheckEmail.saveEmailSave(senderEmail)
                    self.transfertMessage.send('add in db',str(senderEmail))
                if randomMail == 1:
                    self.transfertMessage.send('check in db',str(('',destMail)))
                else: 
                    self.transfertMessage.send('check in db',str((senderEmail,destMail)))
                check = eval(self.transfertMessage.recvMessage()[-1])
                if not check:
                    showerror('Adresse inconnue',"L'adresse mail du destinataire n'existe pas dans notre système")
                else:
                    showinfo('Adresse connue',"L'adresse mail du destinataire est dans notre système.")
                    CheckEmail.askWhatToDo(self,destMail)
        else:
            CheckEmail.askWhatToDo(self,"Anonymous")

    def askWhatToDo(self,destMail):
        self.check.place(x=0,y=0,width=0,height=0)
        self.ask = Frame(self.root,bg='#ffffff')
        self.ask.place(x=0,y=0,width=width,height=height)

        informLabel = Label(self.ask,text=textInform,font=('Arial',15),bg='#f7f7f7')
        informLabel.place(x=10,y=10,width=width-20,height=50)

        txt = "Ecrire un mail a:\n " + destMail
        wEmail = Button(self.ask,text=txt,font=('Arial',20),bg='#f7f7f7', command=lambda:CheckEmail.encodeEmailFrame(self))
        wEmail.place(x=10,y=70,width=width/2-20,height=height-90)

        txt2 = "Decoder un mail de:\n" + destMail
        dcodeEmail = Button(self.ask,text=txt2,font=('Arial',20),bg='#f7f7f7', command=lambda:CheckEmail.decodeEmailFrame(self))
        dcodeEmail.place(x=width/2+20,y=70,width=width/2-20,height=height-90)

    def encodeEmailFrame(self):
        self.ask.place(x=0,y=0,width=0,height=0)
        writeEmail = Frame(self.root,bg='#ffffff')
        writeEmail.place(x=0,y=0,width=width,height=height)

        S = Scrollbar(writeEmail,)
        S.place(x=width-30,y=10,width=20,height=height-100)
        
        textarea = Text(writeEmail,bg='#f7f7f7',font=('Arial',15))
        textarea.place(x=10,y=10,width=width-40,height=height-100)

        S.config(command=textarea.yview)
        textarea.config(yscrollcommand=S.set)

        encodeBtt = Button(writeEmail,text="Encoder le mail",font=('Arial',20),bg='#f7f7f7',command=lambda: CheckEmail.encodeEmail(self,textarea.get("1.0","end")))
        encodeBtt.place(x=width/2-150,y=height-80,width=300,height=40)

        backBtt = Button(writeEmail,text="retour",font=('Arial',20),bg='#f7f7f7',command=lambda: CheckEmail.back(self,writeEmail))
        backBtt.place(x=10,y=height-80,width=150,height=40)


    def decodeEmailFrame(self):
        self.ask.place(x=0,y=0,width=0,height=0)
        writeEmail = Frame(self.root,bg='#ffffff')
        writeEmail.place(x=0,y=0,width=width,height=height)

        S = Scrollbar(writeEmail,)
        S.place(x=width-30,y=10,width=20,height=height-100)
        
        self.textareaEmail = Text(writeEmail,bg='#f7f7f7',font=('Arial',15))
        self.textareaEmail.place(x=10,y=10,width=width-40,height=height-100)

        S.config(command=self.textareaEmail.yview)
        self.textareaEmail.config(yscrollcommand=S.set)

        encodeBtt = Button(writeEmail,text="Decoder le mail",font=('Arial',20),bg='#f7f7f7',command=lambda: CheckEmail.decodeEmail(self,self.textareaEmail.get("1.0","end")))
        encodeBtt.place(x=width/2-150,y=height-80,width=300,height=40)

        backBtt = Button(writeEmail,text="retour",font=('Arial',20),bg='#f7f7f7',command=lambda: CheckEmail.back(self,writeEmail))
        backBtt.place(x=10,y=height-80,width=150,height=40)

    def back(self,entry):
        entry.place(x=0,y=0,width=0,height=0)
        self.ask.place(x=0,y=0,width=width,height=height)


    def encodeEmailPreload(self):
        now = datetime.now()
        current_time = now.strftime(tEncode)
        self.transfertMessage.send('get key time',current_time)
        keyTime = self.transfertMessage.recvMessage()[-1]
        return chiffrementAES.getMyAesSessionKey(), keyTime

    
    def encodeEmail(self,msg):
        dTime = datetime.now()
        yearT = dTime.year
        monthT = dTime.month
        dayT = dTime.day
        hourT = dTime.hour
        minuteT = dTime.minute
        month, day, hour, minute = CheckEmail.cleanTime(monthT,dayT,hourT,minuteT)
        b = str(yearT)+"-"+month+"-"+day+" "+hour+":"+minute+":00"

        key, keyTime = CheckEmail.encodeEmailPreload(self)
        a = chiffrementAES.encryptAes(msg,key).decode("utf-8") + "\n" + key
        del key
        a = chiffrementAES.encryptAes(a,keyTime).decode("utf-8") + "\n" + b 
        del keyTime
        pyperclip.copy(a)
        showinfo('Email Encoder',"Votre mail encode a ete mis dans votre clipboard. Pressez ctrl v pour le coller dans votre mail")

    def decodeEmailPreload(self,msg):
        timeEmailsend = CheckEmail.getTimeEmail(msg)[-1]
        self.transfertMessage.send('get key time',timeEmailsend)
        keyTime = self.transfertMessage.recvMessage()
        if getType(keyTime) == "Error":
            return msg
        else:
            msg = CheckEmail.getTimeEmail(msg)[0]
            msg = chiffrementAES.decryptAes(msg,keyTime[-1])
            del keyTime
            msgFinal = CheckEmail.getTimeEmail(msg)[0]
            keyMsg = CheckEmail.getTimeEmail(msg)[-1]
            msgFinal = chiffrementAES.decryptAes(msgFinal,keyMsg)
            del keyMsg
            return msgFinal


    def decodeEmail(self,msg):
        msgUncrypt = CheckEmail.decodeEmailPreload(self,msg)
        if msgUncrypt != msg:
            self.textareaEmail.delete("1.0","end")
            self.textareaEmail.insert(INSERT,msgUncrypt)
            pyperclip.copy(msgUncrypt)
            showinfo('Email Decoder',"Votre mail decode a ete mis dans votre clipboard. Pressez ctrl v pour le coller")
        else :
            showerror("Erreur","Mail non crypte ou pas par notre systeme")
        

    @staticmethod
    def getTimeEmail(msg):
        t = CheckEmail.cleanMsg(msg)
        return t


    @staticmethod
    def cleanMsg(msg):
        lst = msg.split("\n")
        new = []
        for loop in range(len(lst)):
            if lst[loop] == '':
                pass
            else :
                new.append(lst[loop])
        return new


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
        
    @staticmethod
    def getEmailSave():
        try:
            fil = "emailSave.txt"
            with open(fil, "r") as f:
                l = f.readlines()
        except FileNotFoundError:
            return varSender
        cleanLst = CheckEmail.cleanFile(l) 
        try:
            if cleanLst[0] != '':
                return cleanLst[0]
            else: 
                return varSender
        except IndexError:
            return varSender

    @staticmethod
    def saveEmailSave(email):
        fil = "emailSave.txt"
        with open(fil, "w") as f:
            f.write(email)

    @staticmethod
    def cleanFile(l):
        cleanLst = []
        for loop in range(len(l)):
            clean = l[loop].replace('\n','')
            cleanLst.append(clean)
        try:
            cleanLst.remove('')
        except:
            pass
        return cleanLst

def getType(msg):
    return msg[1]   


if __name__ == '__main__':
    lancement()
    CheckEmail()