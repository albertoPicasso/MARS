from flask import Flask, render_template, request, jsonify, render_template, redirect, url_for
import os


app = Flask(__name__)

# Configuración de la carpeta de subida
UPLOAD_FOLDER = 'viewAgent/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Asegúrate de que la carpeta de subida exista
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    
    user_message = request.json.get('message')
    additional_param = request.json.get('currentDB')

    print(f"Received message: {user_message}")
    print(f"Received param: {additional_param}") 

    response_message = f"Echo: {user_message}, Param: {additional_param if additional_param is not None else 'None'}"

    return jsonify({'response': response_message})

@app.route('/uploadFile')
def upload_file():
    db_name = request.args.get('db')
    if db_name not in ['DB1', 'DB2', 'DB3']:
        return "Base de datos no válida", 400
    return render_template('uploadFile.html')

@app.route('/upload', methods=['POST'])
def upload():
    print ("Hi")
    if 'file' not in request.files:
        return 'No file part', 400
    files = request.files.getlist('file')
    for file in files:
        if file.filename == '':
            return 'No selected file', 400
        if file:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return redirect(url_for('home')) 



if __name__ == '__main__':
    app.run(port=5005, debug=True)
