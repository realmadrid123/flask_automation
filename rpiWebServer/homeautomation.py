import firebase_admin
from firebase_admin import db
import flask

app = flask.Flask(__name__)

firebase_admin.initialize_app(options={
    'databaseURL': 'https://iothome-6bab7.firebaseio.com'
})
HOMEAUTOMATION = db.reference('homeautomation')


@app.route('/devices', methods=['POST'])
def create_device():
    req = flask.request.json
    hero = HOMEAUTOMATION.push(req)
    return flask.jsonify({'id': device.key}), 201

@app.route('/devices/<id>')
def read_device(id):
    return flask.jsonify(_ensure_device(id))

@app.route('/devices/<id>', methods=['PUT'])
def update_device(id):
    _ensure_device(id)
    req = flask.request.json
    HOMEAUTOMATION.child(id).update(req)
    return flask.jsonify({'success': True})

@app.route('/devices/<id>', methods=['DELETE'])
def delete_device(id):
    _ensure_device(id)
    HOMEAUTOMATION.child(id).delete()
    return flask.jsonify({'success': True})

def _ensure_hero(id):
    hero = HOMEAUTOMATION.child(id).get()
    if not device:
        flask.abort(404)
    return device

