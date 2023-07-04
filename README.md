# Jellyfish
Projet Jellyfish : Description du code


from flask import Flask, request
import requests
import json
from apscheduler.schedulers.background import BackgroundScheduler


Ces lignes importent les modules nécessaires pour l'application : Flask pour créer le serveur web, requests pour effectuer des requêtes HTTP, json pour travailler avec des données JSON, et BackgroundScheduler de apscheduler pour planifier des tâches en arrière-plan.

app = Flask(__name__)
coinapi_url = 'https://rest.coinapi.io/v1'
api_key = '8F03625F-22BE-4CDB-96CF-41895AB691FA'  

Ici, nous créons un objet d'application Flask et définissons les variables coinapi_url et api_key qui représentent respectivement l'URL de l'API CoinAPI et la clé d'API.

def authenticate(username, password):
    if username in users and users[username]['password'] == password:
        return True
    return False

Cette fonction authenticate prend un nom d'utilisateur et un mot de passe en paramètres. Elle vérifie si le nom d'utilisateur existe dans le dictionnaire users et si le mot de passe correspond à celui enregistré pour cet utilisateur. Elle renvoie True si l'authentification réussit, sinon elle renvoie False.


def check_alerts():
    for username, user_data in users.items():
        alerts = user_data['alerts']
        for alert in alerts:
            currency = alert['currency']
            alert_type = alert['type']
            value = alert['value']

            response = requests.get(f"{coinapi_url}/exchangerate/{currency}/USD", headers={'X-CoinAPI-Key': api_key})
            data = response.json()
            price = data['rate']

            if alert_type == 'below' and price < value:
                print(f"Alerte : le prix du {currency} est tombé en dessous de {value}$ pour l'utilisateur {username}")
            elif alert_type == 'above' and price > value:
                print(f"Alerte : le prix du {currency} a dépassé {value}$ pour l'utilisateur {username}")

Cette fonction check_alerts est appelée par le planificateur (scheduler) pour vérifier les alertes à intervalles réguliers. Elle itère sur chaque utilisateur dans le dictionnaire users et récupère les alertes associées à cet utilisateur. Pour chaque alerte, elle effectue une requête à l'API CoinAPI pour obtenir le dernier prix de la devise spécifiée. Ensuite, elle compare le prix avec la valeur de l'alerte et affiche un message d'alerte approprié si les conditions sont remplies.


scheduler = BackgroundScheduler()
scheduler.add_job(check_alerts, 'interval', minutes=1)  # Vérifie les alertes toutes les minutes
scheduler.start()

Ces lignes créent un objet BackgroundScheduler et y ajoutent la tâche check_alerts qui sera exécutée toutes les minutes. Ensuite, le planificateur est démarré
