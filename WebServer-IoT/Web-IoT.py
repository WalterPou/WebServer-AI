from flask import Flask, request, render_template, jsonify, redirect, url_for, session
import json
from pyfirmata import Arduino

app=Flask(__name__)
app.secret_key='Database-SSLSSMS'

class DB:
    def __init__(self,dataFile='Database\\DB.json'):
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
    session['logon_passed']=False
    return render_template('index.html')

@app.route('/on', methods=['POST'])
def on():
    print('Light on')
    pin.write(1)
    return '',204

@app.route('/off', methods=['POST'])
def off():
    print('Light off')
    pin.write(0)
    return '',204

@app.route('/authenticate', methods=['POST'])
def authenticate():
    data=request.get_json()
    username=data.get('username','')
    password=data.get('password','')
    results=DB().collectData(username,password)
    if results=='success':
        session['logon_passed']=True
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "failed"}), 200
    
@app.route('/lobby')
def lobby():
    if not session['logon_passed']:
        return redirect(url_for('logon_page'))
    return render_template('lobby.html')

if __name__ == '__main__':
    board=Arduino(input('Board: '))
    pin=board.get_pin('d:8:o')
    app.run(host='0.0.0.0', port=8080)