from flask import Flask, request
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)

coinapi_url = 'https://rest.coinapi.io/v1'



# authentication
def authenticate(username, password):
    if username in users and users[username]['password'] == password:
        return True
    return False


class UserResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username", type=str, required=True, help="Username is required")
        parser.add_argument("password", type=str, required=True, help="Password is required")
        args = parser.parse_args()

        if args["username"] in users:
            return {"message": "User already exists"}, 400

        users[args["username"]] = {"password": args["password"], "api_key": "8F03625F-22BE-4CDB-96CF-41895AB691FA", "alerts": []}  # Replace with your API key
        return {"message": "User created successfully"}, 201

    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username", type=str, required=True, help="Username is required")
        parser.add_argument("password", type=str, required=True, help="Password is required")
        args = parser.parse_args()

        if not authenticate(args["username"], args["password"]):
            return {"message": "Authentication failed"}, 401

        users[args["username"]] = {"password": args["password"], "alerts": []}
        return {"message": "User updated successfully"}

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username", type=str, required=True, help="Username is required")
        parser.add_argument("password", type=str, required=True, help="Password is required")
        args = parser.parse_args()

        if not authenticate(args["username"], args["password"]):
            return {"message": "Authentication failed"}, 401

        del users[args["username"]]
        return {"message": "User deleted successfully"}

class AlertResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username", type=str, required=True, help="Username is required")
        parser.add_argument("api_key", type=str, required=True, help="API key is required")
        args = parser.parse_args()

        if not authenticate(args["username"], users[args["username"]]['password']):
            return {"message": "Authentication failed"}, 401

        if args["api_key"] != users[args["username"]]["api_key"]:
            return {"message": "Invalid API key"}, 401

        if args["username"] not in users:
            return {"message": "User not found"}, 404

        return {"alerts": users[args["username"]]["alerts"]}

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username", type=str, required=True, help="Username is required")
        parser.add_argument("api_key", type=str, required=True, help="API key is required")
        parser.add_argument("currency", type=str, required=True, help="Currency is required")
        parser.add_argument("type", type=str, required=True, choices=["above", "below"], help="Type must be 'above' or 'below'")
        parser.add_argument("value", type=float, required=True, help="Value is required")
        args = parser.parse_args()

        if not authenticate(args["username"], users[args["username"]]['password']):
            return {"message": "Authentication failed"}, 401

        if args["api_key"] != users[args["username"]]["api_key"]:
            return {"message": "Invalid API key"}, 401

        if args["username"] not in users:
            return {"message": "User not found"}, 404

        alert = {"currency": args["currency"], "type": args["type"], "value": args["value"]}
        users[args["username"]]["alerts"].append(alert)

        return {"message": "Alert created successfully"}

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username", type=str, required=True, help="Username is required")
        parser.add_argument("password", type=str, required=True, help="Password is required")
        parser.add_argument("index", type=int, required=True, help="Alert index is required")
        args = parser.parse_args()

        if not authenticate(args["username"], args["password"]):
            return {"message": "Authentication failed"}, 401

        if args["username"] not in users:
            return {"message": "User not found"}, 404

        user_alerts = users[args["username"]]["alerts"]
        if args["index"] < 0 or args["index"] >= len(user_alerts):
            return {"message": "Invalid alert index"}, 400

        del user_alerts[args["index"]]
        return {"message": "Alert deleted successfully"}

api.add_resource(UserResource, "/user")
api.add_resource(AlertResource, "/alert")

# test
users = {
    "john_doe": {
        "password": "password123",
        "api_key": "8F03625F-22BE-4CDB-96CF-41895AB691FA",
        "alerts": [
            {"currency": "BTC", "type": "below", "value": 5000},
            {"currency": "BTC", "type": "above", "value": 7000}
        ]
    }
}

if __name__ == "__main__":
    app.run(debug=True)
