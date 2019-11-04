
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, jsonify

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/boink')
def boink():
    return 'Boink'

@app.route('/orders/api/v1.0/skus', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})