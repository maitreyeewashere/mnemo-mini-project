from flask import *
from flask_cors import CORS
from rag.chatbot import *
from rag.dataentry import *

app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": "*"}})

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/family_entries')
def family_entries():
    return render_template('family_entries.html')
@app.route('/diary_entries')
def diary_entries():
    return render_template('diary_entries.html')

#chatbot
@app.route('/chat',methods=['POST'])
def chatwithmnemo():
    data = request.json
    query = data.get('message')

    if not query:
        return jsonify({'response':'invalid query'})
    
    print('query',query)
    response = askmnemo(query)

    return jsonify({'response':response})


@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

#connecting family form submission
@app.route('/add_person', methods=['POST'])
def add_person_route():
    name = request.form['name']
    relationship = request.form.get('relationship')
    add_person(name, relationship)
    return redirect('/family_entries')

#connection diary entry form submission
@app.route('/add_entry', methods=['POST'])
def add_entry_route():
    text = request.form['entry']
    date = request.form.get('date')
    add_entry(text, date=date)
    return redirect('/diary_entries')

if __name__ == '__main__':
        app.run(debug=True, host="0.0.0.0", port=5500)