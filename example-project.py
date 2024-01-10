
#Import des packages nécéssaires à l'execution du code
import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import time
import plotly.graph_objs as go
from plotly.subplots import make_subplots


#Définition du stock à tracker
global stock_name
stock_name = "AAPL" # <- Changer l'entreprise ici


# Téléchargement les données historiques d'une action à partir de Yahoo Finance
stock = yf.Ticker(stock_name)
data = stock.history(period='max')

# Calcul la moyenne mobile sur x jours
data['SMA50'] = data['Close'].rolling(window=50).mean()

# Initialisation les variables pour suivre la position actuelle de l'action
in_position = False
buy_price = 0

# Paramètres pour l'envoi de mails
smtp_server = "pro1.mail.ovh.net"
smtp_port = 587
smtp_username = 'contact@associationmercure.fr'
smtp_password = ''

receiver = "contact@associationmercure.fr"


# Fonction pour envoyer un e-mail
def send_email(subject, html, text):
    # Créer le message MIME

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = smtp_username
    msg['To'] = receiver

    #Définition du message à envoyer en texte plein et format HTML
    part1 = MIMEText(html, 'html')
    part2 = MIMEText(text, 'plain')

    #Préparation de ma pièce jointe générée par Plotly
    webpage = MIMEApplication(open('data.html', 'rb').read())
    webpage.add_header('Content-Disposition', 'attachment', filename='data.html')

    #Ajoute les différentes parties de notre mail pour l'envoi
    msg.attach(part1)
    msg.attach(part2)
    msg.attach(webpage)

    # Établir une connexion SMTP sécurisée avec le serveur de messagerie et envoyer le message
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls() #Choix de StartTLS et pas SSL car stipulé par le fournisseur de mail OVH
    server.login(smtp_username, smtp_password)
    server.sendmail(smtp_username, receiver, msg.as_string())
    server.quit()


def generate_html(data):
    # Création d'une figure Plotly en subplots pour afficher le cours de l'action et la moyenne mobile
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)

    # Ajoute la courbe de l'action à la première subplot
    fig.add_trace(
        go.Scatter(x=data.index, y=data['Close'], name="Cours de l'action"),
        row=1, col=1
    )

    # Ajoute la courbe de la moyenne mobile à la première subplot
    fig.add_trace(
        go.Scatter(x=data.index, y=data['SMA50'], name="Moyenne mobile (50 jours)"),
        row=1, col=1
    )

    # Ajoute la courbe du volume à la deuxième subplot
    fig.add_trace(
        go.Scatter(x=data.index, y=data['Volume'], name="Volume"),
        row=2, col=1
    )

    # Mettre à jour la mise en page de la figure
    fig.update_layout(height=600, title_text="Données de l'action")

    # Générer le code HTML pour afficher la figure
    html = fig.to_html(full_html=False)

    return html

# Boucle sur les données pour effectuer des transactions de manière infinie
while True:
    try:
        stock = yf.Ticker(stock_name)
        current_price = stock.history(period='1d')['Close'][0]

        #Appel de la fonction qui génère le code HTML puis mettre ce code dans un document HTML
        html = generate_html(data)
        with open('data.html', 'w') as f:
            f.write(html)
        print('Fichier HTML généré') #Message de controle pour la console python

        #Attendre 1sc
        time.sleep(1)

        # Si la moyenne mobile entre dans le cours de l'action
        if current_price > data['SMA50'].iloc[-1] and not in_position:

            buy_price = current_price
            in_position = True
            text="Acheter l'action"

            #Définition du code HTML plus concatener la variable de prix ainsi que le nom de l'action au milieu du code HTML
            html= """\
            <html>
              <head></head>
              <body>
           <h1 style="color: #5e9ca0; text-align: center;"><span style="color: #ff0000;">Warning !</span></h1>
           <h1 style="color: #5e9ca0; text-align: center;"><span style="color: #33cccc;">Hello team All Stars</span></h1>
           <p>We detected an enter point with the moving average</p>
           <p style="color: #5e9ca0;"><span style="color: #000000;">You have to buy <span style="color: #33cccc; font-weight: bold;">""" + stock_name +"""</span></span></p>
           <p>The price of the common action is <span style="color: #33cccc; font-weight: bold;">"""+ str(buy_price) +"""</span> so it's above moving average and it provide profit.</p>
           <p>&nbsp;</p>
           <p>Click this link to access your account : &nbsp;<a href="https://app.traderepublic.com/login">traderepublic</a></p>
           <p>&nbsp;</p>
           <h2 style="text-align: center;"><span style="color: #33cccc;">Good luck for next deal !</span></h2>
           <p>xoxo Team &lt;3</p>
           <p><img src="https://media.istockphoto.com/id/184276818/fr/photo/pomme-rouge.jpg?s=612x612&amp;w=0&amp;k=20&amp;c=yk9viCWt8_VHAvSvzPuqZI-A79xkestBMyCf1AEyhrc=" alt="" /></p>
           <p style="text-align: center;">&nbsp;</p>
           <p style="text-align: center;">&nbsp;</p>
           <p><strong>&nbsp;</strong></p>
              </body>
            </html>
    
            """

            #Appel de la fonction d'envoi de mail avec les variables définies ci-dessus
            send_email("BUY POSITION", html, text) #Sujet + texte html + texte plein
            print('Mail achat action envoyé') #Message de controle pour la console python



        # Si la moyenne mobile sort du cours de l'action
        elif current_price < data['SMA50'].iloc[-1] and in_position:

            sell_price = current_price
            in_position = False
            profit = sell_price - buy_price

            text="Vendre action"
            html= """\
           <html>
             <head></head>
             <body>
         <h1 style="color: #5e9ca0; text-align: center;"><span style="color: #ff0000;">Warning !</span></h1>
         <h1 style="color: #5e9ca0; text-align: center;"><span style="color: #33cccc;">Hello team All Stars</span></h1>
         <p>We detected an enter point with the moving average</p>
         <p style="color: #5e9ca0;"><span style="color: #000000;">You have to sell <span style="color: #33cccc; font-weight: bold;">""" + stock_name +"""</span></span></p>
         <p>The price of the common action is <span style="color: #33cccc; font-weight: bold;">"""+ str(sell_price) +"""</span> so it's under moving average and it's the moment for exit.</p>
         <p>Click this link to access your account : &nbsp;<a href="https://app.traderepublic.com/login">traderepublic</a></p>
         <p>You have made a profit of <span style="color: #33cccc; font-weight: bold;">"""+ str(profit) +"""</span> </p>
         <h2 style="text-align: center;"><span style="color: #33cccc;">Congratulations !</span></h2>
         <p>xoxo Team &lt;3</p>
         <p><img src="https://media.istockphoto.com/id/119104612/fr/photo/trognon-de-pomme-isol&eacute;-sur-blanc.jpg?s=612x612&amp;w=0&amp;k=20&amp;c=372OJSp3XVJCefDlET8riPA0wEjeNzKJ28GqDqeBFdU=" alt="" width="535" height="803" /></p>
         <p style="text-align: center;">&nbsp;</p>
         <p style="text-align: center;">&nbsp;</p>
         <p><strong>&nbsp;</strong></p>
             </body>
           </html>
    
           """
            #Idem que pour l'achat d'action
            send_email("SELL POSITION", html, text)
            print('Mail vente envoyé') #Message controle pour la console python

    except Exception as e:
        # En cas d'erreur, envoyer un e-mail avec le message d'erreur
        subject = "Erreur de trading"
        message = f"Une erreur s'est produite lors de la vérification du cours de l'action : {e}" #Affiche l'erreur dans le mail
        html= """\
       <html>
         <head></head>
         <body>
     <h1 style="color: #5e9ca0; text-align: center;"><span style="color: #ff0000;">Warning !</span></h1>
     <h1 style="color: #5e9ca0; text-align: center;"><span style="color: #33cccc;">Hello team All Stars</span></h1>
     <p>We detected an error !!!</p>
     <p>Click this link to avoid this type of error for next time : <a href="https://investissementpourlesnuls.fr">L'investissement pour les nuls</a></p>
     <p>&nbsp;</p>
     <h2 style="text-align: center;"><span style="color: #33cccc;">Good luck for next deal !</span></h2>
     <p>xoxo Team &lt;3</p>
     <p><img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSkNfdsCO4ByXjiA3F63zlv8UxYeh-wGqo6oA&amp;usqp=CAU" alt="" width="522" height="522" /></p>
         </body>
       </html>

       """
        send_email("ERROR WITH MOVING AVERAGE PROGRAM", html, message)
        print ('Mail erreur envoyé') #Log pour la console !

    # Vérification du cours de l'action toutes les 2 heures
    time.sleep(2 * 60 * 60)
