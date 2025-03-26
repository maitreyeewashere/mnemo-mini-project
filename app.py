from flask import *
from flask_cors import CORS
from rag.chatbot import *

app = Flask(__name__)
CORS(app)

@app.route('/chat',methods=['POST'])
def chatwithmnemo():
    data = request.json
    query = data.get('message')

    if not query:
        return jsonify({'response':'invalid query'})
    
    print('query',query)
    response = askmnemo(query)

    return jsonify({'response':response})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)

