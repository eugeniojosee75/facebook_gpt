from flask import Flask, request
import requests
import json
import subprocess
import os
import re

app = Flask(__name__)

# Tokens de acesso
FB_ACCESS_TOKEN = 'SEU_TOKEN_DE_ACESSO_DO_FACEBOOK'
OPENAI_API_KEY = 'SUA_CHAVE_API_DA_OPENAI'

# URL da API do Facebook
FB_API_URL = f'https://graph.facebook.com/v11.0/me/messages?access_token={FB_ACCESS_TOKEN}'

def get_gpt_response(message):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}',
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": message}]
    }

    try:
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição para a API OpenAI: {e}")
        return "Desculpe, ocorreu um erro ao processar sua solicitação."

def send_message(recipient_id, message_text):
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }

    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(FB_API_URL, headers=headers, data=json.dumps(data))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar mensagem para o Facebook: {e}")

@app.route('/')
def index():
    return "Bem-vindo ao servidor Flask!", 200

@app.route('/webhook', methods=['GET'])
def verify():
    # Método de verificação da API do Facebook
    if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.challenge'):
        if request.args.get('hub.verify_token') == 'SEU_TOKEN_DE_VERIFICAÇÃO':
            return request.args['hub.challenge'], 200
        return 'Falha na verificação', 403
    return 'Requisição inválida', 400

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                if messaging_event.get('message'):
                    sender_id = messaging_event['sender']['id']
                    message_text = messaging_event['message'].get('text')

                    if message_text:
                        response_text = get_gpt_response(message_text)
                        send_message(sender_id, response_text)

    return "OK", 200

def install_dependencies():
    os.system("pkg update -y && pkg upgrade -y")
    os.system("pkg install python -y")
    os.system("pkg install openssh -y")
    os.system("pip install flask requests")

def start_serveo_tunnel():
    # Inicia o túnel Serveo e captura a URL pública
    process = subprocess.Popen(
        ['ssh', '-R', '80:localhost:5000', 'serveo.net'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    for line in process.stdout:
        match = re.search(r'http://.*serveo.net', line)
        if match:
            print(f"Túnel público URL: {match.group(0)}")
            break

if __name__ == '__main__':
    install_dependencies()
    start_serveo_tunnel()
    app.run(debug=True, port=5000)