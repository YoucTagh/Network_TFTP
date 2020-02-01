import socket


ConnexionAuServeur = socket.socket()
port = 9500
host = "192.168.1.12"

ConnexionAuServeur.connect((host,port))


while True:
    
    print("Entrez la commande TFTP : ")
    inp=input()
    ConnexionAuServeur.send(inp.encode('utf-8'))
    reqSplit = inp.split(":")
    commande = ConnexionAuServeur.recv(1024).decode('utf-8')

    if commande == "200 k, bye":
        print("Exiting")
        break

    elif  reqSplit[0] == "1" and commande != "501 DIRECTORY TRAVERSAL DENIED" and commande != "500 Fichier introuvable" :
        #print("Tag : "+commande.decode('utf-8'))

        if commande[:6] == 'EXISTS':
            filesize = int(commande[6:])
            resp = input("File exists, " + str(filesize) +" Bytes, download? (Y/N)? -> ")
            while resp != 'N' and resp != 'Y' :
                print("Answer must be Y/N")
                resp=input()
            if resp == 'Y':
                ConnexionAuServeur.sendall(b"OK")
                f = open('new_'+reqSplit[1], 'wb')
                data = ConnexionAuServeur.recv(1024)
                totalRecv = len(data)
                f.write(data)
                while totalRecv < filesize:
                    data = ConnexionAuServeur.recv(1024)
                    totalRecv += len(data)
                    f.write(data)
                    print ("{0:.2f}".format((totalRecv/float(filesize))*100)+ "% Done")
                print ("Download Complete!")
                f.close()
            else :
                print("--StartOfFile--")
                ConnexionAuServeur.sendall(b"OK")
                data = ConnexionAuServeur.recv(1024)
                totalRecv = len(data)
                print(data.decode('utf-8'))
                while totalRecv < filesize:
                    data = ConnexionAuServeur.recv(1024)
                    totalRecv += len(data)
                    print(data.decode('utf-8'))
                print ("--EndOfFile--")
            
            
        else:
            print ("File Does Not Exist!")
            continue
            
    else :
        print(commande)
        while commande.find("--\r\n\r\n") == -1:
            commande = ConnexionAuServeur.recv(1024).decode("utf-8")
            print(commande)

ConnexionAuServeur.close()
