from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from flask_socketio import SocketIO, emit
import json

app=Flask(__name__)
src_key="DatabaseSSLSSMS-Server"
app.config['SECRET_KEY']=src_key
app.secret_key=src_key
socketio=SocketIO(app)

class DB:
    def __init__(self,dataFile="Database\\DB.json"):
        self.Source=dataFile
        self.loadData()

    def loadData(self):
        try:
            with open(self.Source,'r') as Source:
                self.data=json.load(Source)
        except:
            self.data={}

    def saveData(self):
        with open(self.Source,'w') as Source:
            json.dump(self.data,Source)

    def collectData(self,username,password):
        try:
            value=self.data[username]
            if password==value:
                return "success"
            else:
                return "failed"
        except:
            return "failed"

@app.route('/')
def logon_page():
    session['logged_in']=False
    return render_template('logon-page.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    data=request.get_json()
    username=data.get('username','')
    password=data.get('password','')
    results=DB().collectData(username,password)
    if results=='success':
        session['logged_in']=True
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "failed"})

@app.route('/control-page', methods=['GET'])
def control_page():
    if not session['logged_in']:
        return redirect(url_for('logon_page'))
    return render_template('control-page.html')

@socketio.on('connect')
def handle_connect():
    print('Client Connected.')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client Disconnected.')

@socketio.on('message')
def handle_message(message):
    #print(f'Received Message: {message}')
    emit('message', {'message': message}, broadcast=True)

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=8080)
