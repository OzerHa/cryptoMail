#####################################################################
#   This library allows the security of your data through a socket. #
#   It uses 3 different encryptions: Diffie-hellman, RSA and AES.   #
#   It also provides packet management and formatting of your data. #
#####################################################################


### Import ###
import base64, os, time, sys, string, random, math, hashlib

try:
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP, AES
    import pyDH
except ImportError:
    try:
        os.system("pip install pycrypto")
        os.system("pip install pyDH")

        from Crypto.PublicKey import RSA
        from Crypto.Cipher import PKCS1_OAEP, AES
        import pyDH
    except :
        print("Erreur d'importation, veuillez contacter un admin.")


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


class cleanMessage:
    # Fonction pour le formatage des messages lors du transfert par le socket #
    def cleanMsgEnvoie(message):
        message = message.replace('(','%*$')
        message = message.replace(')','+-*')
        message = message.replace('{','&*&')
        message = message.replace('}','@-@')
        message = message.replace('[','*/-')
        message = message.replace(']','*!:')
        return message.encode('utf-8')

    def cleanMsgRecv(message):
        message = message.replace('%*$','(')
        message = message.replace('+-*',')')
        message = message.replace('&*&','{')
        message = message.replace('@-@','}')
        message = message.replace('*/-','[')
        message = message.replace('*!:',']')
        return message
    ###

class chiffrementRSA:
    # Fonction de cryptage et decryptage RSA
    def getMyAccountRSAKey(sizeRSA):
        key = RSA.generate(sizeRSA)
        privateKey = key.export_key('PEM')
        publicKey = key.public_key().export_key('PEM')
        # Output: bytes
        return privateKey,publicKey

    def encryptRsa(message,RsaPublicKeyServeur):
        RsaPublicKeyServeur = RSA.import_key(RsaPublicKeyServeur)
        encryptor = PKCS1_OAEP.new(RsaPublicKeyServeur)
        # Output: bytes
        return encryptor.encrypt(bytes(message,'utf-8'))

    def decryptRSA(message,RsaPrivateKeyUser):
        RsaPrivateKeyUser = RSA.import_key(RsaPrivateKeyUser)
        decryptor = PKCS1_OAEP.new(RsaPrivateKeyUser)
        # Output: str
        return decryptor.decrypt(message).decode('utf-8')
    ###

class chiffrementDH:
    def getMyDHSessionKey():
        people = pyDH.DiffieHellman()
        peoplePublic = people.gen_public_key()
        return people,peoplePublic
    
    def decodeDH(people,key):
        peopleSharedKey = people.gen_shared_key(key)
        return peopleSharedKey

    def getUseableKey(key):
        return hashlib.sha512(bytes(key,'utf-8')).hexdigest()[:32]

    def encryptDH(message,key,separator='//'):
        IV = 16 * b'\x00' 
        encryption_suite = AES.new(key, AES.MODE_CBC, IV = IV)
        message = str(len(message)) + separator + message
        for loop in range((16-len(message)) % 16):
            message = message + random.choice(string.ascii_letters)
        messageEdit = message
        messageEdit = bytes(messageEdit,'utf-8')
        messageCrypt = encryption_suite.encrypt(messageEdit)
        # Output: bytes
        return base64.b64encode(messageCrypt)

    def decryptDH(message,key,separator='//'):
        IV = 16 * b'\x00' 
        message = base64.b64decode(message)
        # base64: convertir le bytes en hex, .decode() impossible
        decryption_suite = AES.new(key, AES.MODE_CBC, IV = IV)
        try:
            messageDecrypt = decryption_suite.decrypt(message)
        except ValueError:
            sys.exit()
        # Output: str
        messageDecrypt = messageDecrypt.decode('utf-8')
        messageToReform = messageDecrypt.split(separator)
        lenmessageToReform = int(messageToReform[0])
        messageReformate = messageToReform[-1]
        messageDecrypt = messageReformate[:lenmessageToReform]
        return messageDecrypt

class chiffrementAES:
    def getMyAesSessionKey():
        keyLenght = 32
        # base64: convertir le bytes en hex, .decode() impossible
        AesSessionKey = base64.b64encode(os.urandom(keyLenght))
        # Output: bytes
        # renvoie une cle aes de 32 bytes
        return AesSessionKey.decode('utf-8')

    # Fonction de cryptage et decryptage AES
    def encryptAes(message,AesSessionKey,separator='//'):
        IV = 16 * b'\x00' 
        key = base64.b64decode(AesSessionKey)
        encryption_suite = AES.new(key, AES.MODE_CBC, IV = IV)
        message = str(len(message)) + separator + message
        for loop in range((16-len(message)) % 16):
            message = message + random.choice(string.ascii_letters)
        messageEdit = message
        messageEdit = bytes(messageEdit,'utf-8')
        messageCrypt = encryption_suite.encrypt(messageEdit)
        # Output: bytes
        return base64.b64encode(messageCrypt)

     
    def decryptAes(message,AesSessionKey,separator='//'):
        IV = 16 * b'\x00' 
        key = base64.b64decode(AesSessionKey)
        message = base64.b64decode(message)
        # base64: convertir le bytes en hex, .decode() impossible
        decryption_suite = AES.new(key, AES.MODE_CBC, IV = IV)
        try:
            messageDecrypt = decryption_suite.decrypt(message)
        except ValueError:
            sys.exit()
        # Output: str
        messageDecrypt = messageDecrypt.decode('utf-8')
        messageToReform = messageDecrypt.split(separator)
        lenmessageToReform = int(messageToReform[0])
        messageReformate = messageToReform[-1]
        messageDecrypt = messageReformate[:lenmessageToReform]
        return messageDecrypt
    ###

class formatageMessage:
    # Fonction de formatage des messages avant et apres transfert par le socket
    def formatMessage(buffer,uid,types,message,opt='',arg = 0):
        lenMsg = len(message)
        # en cas de message trop long
        if lenMsg > int(buffer/2):
            messageToSend = []
            # mise en place de la limite de caractere par message: buffer/4 car ensuite converti en bytes
            limitLen = int(buffer/2)
            # en cas de message systeme
            if opt != '':
                a = 0
                # en cas de fichier
                if types == 'File':
                    # limite encore plus faible pour eviter encore plus les erreurs de tailles
                    nombreMessageTot = int(limitLen/4)
                    m = nombreMessageTot
                    mBase = m
                # en cas de message texte
                else:
                    nombreMessageTot = limitLen
                    m = nombreMessageTot
                    mBase = m
                # pour savoir le nombre totale de message a envoyer, sert a la reception
                for loop in range(int(lenMsg/nombreMessageTot)+arg):
                    lenTot = loop
                for loop in range(lenTot):
                    msgClean = cleanMessage.cleanMsgEnvoie(message[a:m])
                    # correction d'erreur du a la boucle
                    if arg == 0:
                        messageToSend.append((uid,types,loop,lenTot-1,lenMsg,opt,msgClean))
                    else:
                        messageToSend.append((uid,types,loop,lenTot,lenMsg,opt,msgClean))
                    a = m
                    m = m+mBase
                    # pour entre sur d'envoyer tt le message
                    if m > lenMsg:
                        m = lenMsg-arg
                    else:
                        pass
                
            # en cas de message client to client
            else:
                a = 0
                m = limitLen
                mBase = m
                lenTot = math.ceil(lenMsg/limitLen+arg) 
                for loop in range(lenTot):
                    msgClean = cleanMessage.cleanMsgEnvoie(message[a:m])
                    if arg == 0:
                        messageToSend.append((uid,types,loop,lenTot-1,lenMsg,msgClean))
                    else: 
                        messageToSend.append((uid,types,loop,lenTot,lenMsg,msgClean))
                    a = m
                    m = m+mBase
                    if m > lenMsg:
                        m = lenMsg-arg
                    else:
                        pass
        # si le message est cour, formatage direct
        else:
            message = cleanMessage.cleanMsgEnvoie(str(message))
            # en cas de message systeme
            if opt != '':
                messageToSend = (uid,types,0,0,lenMsg,opt,message)
            # en cas de message client to client
            else:
                messageToSend = (uid,types,0,0,lenMsg,message)
        # Output: str, tuple dans liste 
        return str(messageToSend)

    def reformatMessage(message):
        messageToReform = []
        # recuperation d'une liste contenant l'ensemble des messages recu sous forme divise et bytes
        for loop in range(len(message)):
            try:
                messageToReform.append(message[loop].decode('utf-8'))
            except UnicodeDecodeError:
                # en cas de fichier, donc de bytes non decodable 
                messageToReform.append(message[loop])
        # formation du message en une seule partie
        try:
            msg = ''.join(messageToReform)
            msg = cleanMessage.cleanMsgRecv(msg)
        except TypeError:
            msg = b''.join(messageToReform)
        return msg
    ###

class gestionConnexion:
    def __init__(self,socket,buffer,verbose=False):
        self.socket = socket
        self.buffer = buffer
        self.separator = gestionConnexion.generateSeparator()
        self.verbose = verbose

    @staticmethod
    def generateSeparator():
        # sert pour le cryptage
        separator = ''
        hexD = string.hexdigits
        pun = string.punctuation
        ran = hexD + pun
        for loop in range(8):
            separator = separator + random.choice(ran)
        if ':' in separator:
            separator = separator.replace(':',';')
        return separator

    # Fonction de gestion de connexion
    def gestionConnexionServeur(self,sizeRSA=2048):
        if self.verbose:
            print(getLocalTime()+"Starting DH exchange...")
        p1,p1Public = chiffrementDH.getMyDHSessionKey()
        self.socket.send(bytes(str(p1Public),'utf-8'))
        p2Public = int(self.socket.recv(self.buffer).decode('utf-8'))
        keyDH = chiffrementDH.decodeDH(p1,p2Public)
        keyDH = bytes(chiffrementDH.getUseableKey(keyDH),'utf-8')
        if self.verbose:
            print(getLocalTime()+"DH exchange succesfull, starting RSA exchange...")
        privateKey, publicKey = chiffrementRSA.getMyAccountRSAKey(sizeRSA)
        pubicKeyCryptDH = chiffrementDH.encryptDH(publicKey.decode('utf-8'),keyDH)
        self.socket.sendall(pubicKeyCryptDH)
        recv = self.socket.recv(self.buffer)
        recv = chiffrementRSA.decryptRSA(recv,privateKey)
        if recv == "error RSA":
            gestionConnexion.gestionConnexionServeur(self,1024)
            if self.verbose:
                print(getLocalTime()+"RSA exchange error, trying again...")
        if self.verbose:
            print(getLocalTime()+"RSA exchange succesfull, starting AES key reconstruction...")
        AesSessionKey, self.separator = eval(recv)
        if self.verbose:
            print(getLocalTime()+"AES key reconstruction succesfull.")
        return AesSessionKey, self.separator

    def sendKeyLoginClient(self): 
        if self.verbose:
            print(getLocalTime()+"Starting DH exchange...")
        p2,p2Public = chiffrementDH.getMyDHSessionKey()
        p1Public = int(self.socket.recv(self.buffer).decode('utf-8'))
        keyDH = chiffrementDH.decodeDH(p2,p1Public)
        keyDH = bytes(chiffrementDH.getUseableKey(keyDH),'utf-8')
        self.socket.send(bytes(str(p2Public),'utf-8'))
        if self.verbose:
            print(getLocalTime()+"DH exchange succesfull, starting RSA exchange...")
        RsaPublicKeyServeurCryptDH = self.socket.recv(self.buffer)
        RsaPublicKeyServeur = bytes(chiffrementDH.decryptDH(RsaPublicKeyServeurCryptDH,keyDH),'utf-8')
        if self.verbose:
            print(getLocalTime()+"RSA exchange succesfull, starting AES key exchange...")
        AesSessionKey = chiffrementAES.getMyAesSessionKey()
        messageToSend = chiffrementRSA.encryptRsa(str([AesSessionKey,self.separator]),RsaPublicKeyServeur)
        self.socket.sendall(messageToSend)
        if self.verbose:
            print(getLocalTime()+"AES key exchange succesfull.")
        return AesSessionKey, self.separator
        ###

class transfertMessage():
    def __init__(self,socket,buffer,separator,AesSessionKey,uid=''):
        self.socket = socket
        self.buffer = buffer
        self.separator = separator
        self.AesSessionKey = AesSessionKey
        self.myId = uid

    # Fonction pour l'envoie et la reception des messages
    def send(self,types,message,myId='',opt='',timesCleanErreur=0.0000,repetCount=0):
        # types: types de la requete, opt, option du message
        # message: message a envoyer, timesCleanErreur: en cas de client to client, pour enviter les erreurs de transmissions
        # repetCount: compteur du nombre de message envoyer
        # formatage du message
        if myId != '':
            self.myId = myId

        messageToSend = formatageMessage.formatMessage(self.buffer,self.myId,types,message,opt)

        # si le message est trop long, donc divise en plusieurs morceaux
        if len(message) > self.buffer/2:
            # recuperation du nombre de message a envoyer
            lenMsg = len(eval(messageToSend))
            messageToSend = eval(messageToSend)
            for loop in range(lenMsg):
                # recupereation du message a envoyer
                msg = messageToSend[loop]
                # cryptage de l'ensemble du paquet
                messageTo = chiffrementAES.encryptAes(str(msg),self.AesSessionKey,self.separator)
                # envoie
                self.socket.sendall(messageTo)
                # pour eviter les erreurs
                if loop%200==0 and timesCleanErreur == 0.0000:
                    time.sleep(timesCleanErreur + 0.0001)
                elif timesCleanErreur != 0.0000:
                    time.sleep(timesCleanErreur)
        # si le message est court
        else :
            messageToSend = chiffrementAES.encryptAes(messageToSend,self.AesSessionKey,self.separator)

            self.socket.sendall(messageToSend)
            if repetCount % 200 == 0 and 0.0000 == timesCleanErreur:
                time.sleep(timesCleanErreur + 0.0001)
        repetCount += 1
        return repetCount

    def recvMessage(self):
        messageRecv = self.socket.recv(self.buffer).decode('utf-8')
        
        
        # tant qu'une connexion existe
        toRecompose = False
        # decryptage du message              
        messageRecv = eval(chiffrementAES.decryptAes(messageRecv,self.AesSessionKey,self.separator))
        
        act = messageRecv[2]
        tot = messageRecv[3]

        # si le message est decompose
        if act != tot:
            toRecompose = True
            messageToReform = [messageRecv[-1]]
            # reception de l'ensemble des messages
            while act != tot:
                messageRecv = self.socket.recv(self.buffer).decode('utf-8')
                # decryptage
                messageRecv = eval(chiffrementAES.decryptAes(messageRecv,self.AesSessionKey,self.separator))
                messageToReform.append(messageRecv[-1])
                act = messageRecv[2]
                tot = messageRecv[3]
        # recomposition des messages
        if toRecompose:
            lst = list(eval(str(messageRecv)))
            # reformatage du message
            lst[-1] = cleanMessage.cleanMsgRecv(formatageMessage.reformatMessage(messageToReform))
            messageRecv = tuple(lst)
        else:
            lst = list(eval(str(messageRecv)))
            lst[-1] = cleanMessage.cleanMsgRecv(lst[-1].decode('utf-8'))
            messageRecv = tuple(lst)
        lenMsgTot = messageRecv[4]
        # si opt est vide
        if messageRecv[-2] == '':
            messageRecv.pop(-2)
        return eval(str(messageRecv))
    ###

class gestionError():
    def __init__(self,socket,buffer): 
        self.socket = socket
        self.buffer = buffer

    def RSAkeyFromat(self): 
        self.socket.send(bytes("error RSA",'utf-8'))


def getLocalTime(): 
    now = time.localtime(time.time())
    year, month, day, hour, minute, second, weekday, yearday, daylight = now
    return str(f"{bcolors.OKBLUE}[%02d:%02d:%02d]: {bcolors.ENDC}" % (hour, minute, second))