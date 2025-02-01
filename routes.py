from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from chatbot import CustomChatAssistant

app = Flask(__name__)
CORS(app)
bot = CustomChatAssistant()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    # Check if the incoming request is in JSON format
    if request.is_json:
        data = request.get_json()  # Parse the incoming JSON data
        text = data.get('text')  # Extract the 'text' field
        
        print("Received text:", text)  # Log the received text
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400  # Return error if text is missing
        
        response = bot.process_query(text)  # Process the query
        return jsonify({'response': response})
    
    # If the content is not JSON
    return jsonify({'error': 'Request must be JSON'}), 400

if __name__ == '__main__':
    app.run(debug=True)
