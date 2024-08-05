from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    print("Enviando a " )
    user_message = request.json.get('message')
    
    # Aquí podrías integrar una llamada a GPT-4 u otro servicio de generación
    # En este ejemplo, simplemente devolvemos el mensaje del usuario como respuesta
    response_message = f"Echo: {user_message}"
    
    return jsonify({'response': response_message})

if __name__ == '__main__':
    app.run(port=5005, debug=True)
