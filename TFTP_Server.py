# Python 3!
import socket 
import os
import re
import _thread

def TraitNewConnection(ConnexionAUnClient,addrclient):
    # Acceder au repertoire racine
    os.chdir(Chemin_racine)
   
    print("Connexion de la machine = ", addrclient)
    while True:
      
       # Format des commandes transmis par le client : "Type_Commande:NomFichier"
       # Type_Commande == 3 changer le repertoire courant (Change Working Dirrectory "CWD" dans FTP et "cd" dans Windows et Linux)
       # Type_Commande == 2 demander la liste des fichiers dans le repetoir courant (comme la commande "dir" dans Windows et "ls" dans Linux)
       # Type_Commande == 1 telecharger un fichier( par exemple si la commande recue == "1:File.png" signifie telecharger "File.png" )
       # Type_Commande == 0 Si la commende commence par "0:" cela signifie que le client souhaite deconnecter
       # par exemple "0:", "0:CYA" et "0:leaving" signifient deconnexion       
        try:
            Commande=ConnexionAUnClient.recv(1024).decode("utf-8")
            # decouper la commande par le caractere ":"
            Arguments=Commande.split(":")
            # le premier argument represente le type de la commande
            Type_Commande=int(Arguments[0])
            Nom_Fichier=Arguments[1]
            if(Type_Commande==0):# commande de deconnexion
                ConnexionAUnClient.send(b"200 k, bye")
                # L'envoie d'une sequence "--\r\n\r\n" delimite la fin d'une reponse
                ConnexionAUnClient.send(b"--\r\n\r\n")
                # Sortir de la boucle de traitement while
                break
            elif(Type_Commande==1):# commande de telechargement de fichier       
                # Nom_Fichier ne doit pas contenir ".." ou / (tentative de parcourir les repertoires )
                if( ".." in Nom_Fichier or "/" in Nom_Fichier ):
                    ConnexionAUnClient.send(b"501 DIRECTORY TRAVERSAL DENIED")
                    ConnexionAUnClient.send(b"--\r\n\r\n")
                    continue # Esquiver le reste des instructions
                
                if os.path.isfile(Nom_Fichier):
                    taille = os.path.getsize(Nom_Fichier)
                    ConnexionAUnClient.sendall(b"EXISTS "+str(taille).encode())
                    userResponse = ConnexionAUnClient.recv(1024)
                    if userResponse.decode('utf-8')[:2] == 'OK':
                        with open(Nom_Fichier, 'rb') as f:
                            bytesToSend = f.read(1024)
                            sendedData = len(bytesToSend)
                            ConnexionAUnClient.send(bytesToSend)
                            while sendedData < taille:
                                bytesToSend = f.read(1024)
                                ConnexionAUnClient.send(bytesToSend)
                                sendedData += len(bytesToSend)    
                        print("Done File")
                else:  
                    ConnexionAUnClient.sendall(b"ERR ")

            elif(Type_Commande==2):# commande pour lister le contenu du repertoir courant
                # os.listdir(".") revoie la liste des fichier / repertoires dans le repertoire courant (comme ls et dir)
                Liste_Des_Fichiers=os.listdir(".")
                ConnexionAUnClient.send(("\n".join(Liste_Des_Fichiers)).encode())
                ConnexionAUnClient.send(b"--\r\n\r\n")               
            elif(Type_Commande==3):# commande d'acces au repertoir en parametre
                try:
                    # acceder au repertoir transmis par le client ( cd Nom_Fichier)
                    # os.chdir renvoie une exeception si le nom du repertoir en parametre ("Nom_Fichier") n'existe pas
                    os.chdir(Nom_Fichier)
                    
                    if( Reprtoir_racine in os.listdir(".")):
                        os.chdir(Reprtoir_racine)
                        ConnexionAUnClient.send(b"501 Nope (pls, just, k?)")
                    else:
                        ConnexionAUnClient.send(("200 OK "+Nom_Fichier).encode())
                except:
                    # en cas d'exception (le repertoir demandee par le client est inexistant)
                    # transmettre le code 404
                    ConnexionAUnClient.send(("404 Le repertoire "+Nom_Fichier+" est introuvable").encode())
                ConnexionAUnClient.send(b"--\r\n\r\n")
            else:
                # si la commande du client ne correspond a aucune des commandes permises
                # transmettre le code 400
                ConnexionAUnClient.send(("400 Commande inconue = "+Commande).encode())
                ConnexionAUnClient.send(b"--\r\n\r\n")
                
        except:           
            try:
              # envoie de code 401: syntaxe incorrecte              
              ConnexionAUnClient.send(("401 Format de commande incorrect : "+Commande).encode())
              ConnexionAUnClient.send(b"--\r\n\r\n")
               
            except:
                pass
                break
           
    
    try:
        print( "Deconnexion de :",addrclient)
        ConnexionAUnClient.close()
    except :
        pass




SocketServeur = socket.socket()
port = 9500

# Obtention du chemin courant (getcwd()==get current working directory)
Chemin_racine=os.getcwd()
Reprtoir_racine=os.getcwd().split("\\")[-1]
                                
# Ecout de connexion sur toutes les insterfacces (0.0.0.0)
SocketServeur.bind(("0.0.0.0", port)) 
SocketServeur.listen(1)
print("Lancement serveur")

while True:
   # Attente d'une connexion (accept)
   ConnexionAUnClient, addrclient = SocketServeur.accept()
   
   _thread.start_new_thread(TraitNewConnection,(ConnexionAUnClient,addrclient))


SocketServeur.close() 
 