from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import ollama

app=Flask(__name__)
app.secret_key='eiqramnasrullah0610'

class Database:
    def __init__(self,dataFile='Database\\Main.json'):
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
            results=self.data[username]
            if password==results:
                return "authenticate"
            else:
                return None
        except:
            return None

DB=Database()

class BMA:
    def levenshtein_distance(self,s1,s2):
        if len(s1)<len(s2):
            return self.levenshtein_distance(s2,s1)
        if len(s2)==0:
            return len(s1)
        previous=range(len(s2)+1)
        for i,a in enumerate(s1):
            current=[i+1]
            for j,b in enumerate(s2):
                current.append(
                    min(
                        previous[j+1]+1,
                        current[j]+1,
                        previous[j]+(a!=b)
                    )
                )
            previous=current
        return previous[-1]

    def ratio(self,s1,s2):
        distance=self.levenshtein_distance(s1,s2)
        maxLen=max(len(s1),len(s2))
        return 1-distance/maxLen

    def extractOne(self,userInput,choices):
        bestMatch=None
        bestScore=-1
        for choice in choices:
            score=self.ratio(userInput,choice)
            if score>bestScore:
                bestMatch=choice
                bestScore=score
        return bestMatch,bestScore

class ArtificialBrain:
    def __init__(self,data_file='Database\\Network.json'):
        self.Source=data_file
        self.load_data()
        self.model='PCT2'
        self.role='user'
        self.maxLength=4000

    def load_data(self):
        try:
            with open(self.Source,'r') as Source:
                self.knowledge=json.load(Source)
        except:
            self.knowledge={}
    def save_data(self):
        with open(self.Source,'w') as Source:
            json.dump(self.knowledge,Source)
    def best_match(self,question):
        questions=list(self.knowledge.keys())
        if not question:
            return None
        matches,threshold=BMA().extractOne(question,questions)
        if threshold>.2:
            return self.knowledge[matches]
    def get_response(self,question):
        response=self.best_match(question)
        if response:
            #return response
            return self.getUnknown(question)
        else:
            return self.getUnknown(question)
            #return "I couldn't respond to that question."

    def learn(self,question,alias):
        self.knowledge[question]=alias
        self.save_data()

    def getUnknown(self,question):
        data = ''
        stream = ollama.chat(
            model=self.model,
            messages=[{'role': self.role, 'content': str(question)}],
            options={'num_predict': self.maxLength},
            stream=True
        )

        for chunk in stream:
            data += str(chunk['message']['content'])
        return data


@app.route('/')
def login_page():
    session['logged_in']=False
    return render_template('index.html')

@app.route('/authenticate', methods=['POST'])
def auth():
    data=request.get_json()
    username=data.get('user','')
    password=data.get('pass','')
    authenticate=DB.collectData(username,password)
    print(f'Username: {username}')
    print(f'Password: {password}')
    if authenticate=='authenticate':
        session['logged_in']=True
        return jsonify({'logon': 'success'}), 200
    else:
        return jsonify({'logon': 'failed'}), 200

@app.route('/submit', methods=['POST'])
def handle_message():
    data = request.get_json()
    message = data.get('message', '') 
    print(f"Received: {message}")
    response=ArtificialBrain().get_response(message)
    return jsonify({'status': 'success', 'response': response}), 200


@app.route('/main', methods=['GET'])
def reroute_to_main_page():
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
    return render_template('AI-Page.html')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8080)
