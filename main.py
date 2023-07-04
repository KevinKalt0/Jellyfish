from flask import Flask, request
import requests
import json
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
coinapi_url = 'https://rest.coinapi.io/v1'
api_key = '8F03625F-22BE-4CDB-96CF-41895AB691FA'  # Replace with your CoinAPI API key


def authenticate(username, password):
    if username in users and users[username]['password'] == password:
        return True
    return False

def check_alerts():
    for username, user_data in users.items():
        alerts = user_data['alerts']
        for alert in alerts:
            currency = alert['currency']
            alert_type = alert['type']
            value = alert['value']

            # Fetch the latest price from CoinAPI
            response = requests.get(f"{coinapi_url}/exchangerate/{currency}/USD", headers={'X-CoinAPI-Key': api_key})
            data = response.json()
            price = data['rate']

            if alert_type == 'below' and price < value:
                print(f"Alert: {currency} price fell below {value}$ for user {username}")
            elif alert_type == 'above' and price > value:
                print(f"Alert: {currency} price went above {value}$ for user {username}")

scheduler = BackgroundScheduler()
scheduler.add_job(check_alerts, 'interval', minutes=1)  # Check alerts every minute
scheduler.start()

@app.route('/user', methods=['POST'])
def create_user():
    username = request.form.get('username')
    password = request.form.get('password')

    if username in users:
        return {"message": "User already exists"}, 400

    users[username] = {"password": password, "api_key": api_key, "alerts": []}
    return {"message": "User created successfully"}, 201

@app.route('/user', methods=['PUT'])
def update_user():
    username = request.form.get('username')
    password = request.form.get('password')

    if not authenticate(username, password):
        return {"message": "Authentication failed"}, 401

    users[username]["password"] = password
    return {"message": "User updated successfully"}

@app.route('/user', methods=['DELETE'])
def delete_user():
    username = request.form.get('username')
    password = request.form.get('password')

    if not authenticate(username, password):
        return {"message": "Authentication failed"}, 401

    del users[username]
    return {"message": "User deleted successfully"}

@app.route('/alert', methods=['GET'])
def get_alerts():
    username = request.args.get('username')
    api_key = request.args.get('api_key')

    if not authenticate(username, users[username]['password']):
        return {"message": "Authentication failed"}, 401

    if api_key != users[username]["api_key"]:
        return {"message": "Invalid API key"}, 401

    if username not in users:
        return {"message": "User not found"}, 404

    return {"alerts": users[username]["alerts"]}

@app.route('/alert', methods=['POST'])
def create_alert():
    username = request.form.get('username')
    api_key = request.form.get('api_key')
    currency = request.form.get('currency')
    alert_type = request.form.get('type')
    value = float(request.form.get('value'))

    if not authenticate(username, users[username]['password']):
        return {"message": "Authentication failed"}, 401

    if api_key != users[username]["api_key"]:
        return {"message": "Invalid API key"}, 401

    if username not in users:
        return {"message": "User not found"}, 404

    alert = {"currency": currency, "type": alert_type, "value": value}
    users[username]["alerts"].append(alert)

    return {"message": "Alert created successfully"}

@app.route('/alert', methods=['DELETE'])
def delete_alert():
    username = request.form.get('username')
    password = request.form.get('password')
    index = int(request.form.get('index'))

    if not authenticate(username, password):
        return {"message": "Authentication failed"}, 401

    if username not in users:
        return {"message": "User not found"}, 404

    user_alerts = users[username]["alerts"]
    if index < 0 or index >= len(user_alerts):
        return {"message": "Invalid alert index"}, 400

    del user_alerts[index]
    return {"message": "Alert deleted successfully"}

# test
users = {
    "john_doe": {
        "password": "password123",
        "api_key": api_key,
        "alerts": [
            {"currency": "BTC", "type": "below", "value": 5000},
            {"currency": "BTC", "type": "above", "value": 7000}
        ]
    }
}

if __name__ == "__main__":
    app.run()
