from flask import Flask, request, jsonify
import requests
import openai
import os
app = Flask(__name__)
# Carrega variáveis de ambiente do arquivo .env
from dotenv import load_dotenv load_dotenv()
# Configuração da API da OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')
# Rota para receber mensagens do Facebook Messenger
@app.route('/webhook', methods=['POST']) def webhook():    data = request.get_json()
    # Verifica se a mensagem é um evento de mensagem    
if 'entry' in data and len(data['entry']) > 0 and 'messaging' in data['entry'][0]:        
for message in data['entry'][0]['messaging']:            
if 'message' in message and 'text' in message['message']:                
  user_message = message['message']['text']                
  chatgpt_response = chat_with_gpt(user_message)                
  send_message(message['sender']['id'], chatgpt_response)
    return jsonify({'status': 'ok'})
# Função para enviar mensagens de volta para o Facebook Messenger
def send_message(recipient_id, text):   
  payload = {        'recipient': {'id': recipient_id},        'message': {'text': text}    }    requests.post('https://graph.facebook.com/v12.0/me/messages', params={'access_token': os.getenv('PAGE_ACCESS_TOKEN')}, json=payload)
# Função para interagir com o modelo GPT
def chat_with_gpt(user_message):    response = openai.Completion.create(        engine="text-davinci-003",        prompt=user_message,        max_tokens=50    )    
  return response['choices'][0]['text'].strip()
if __name__ == '__main__':    app.run(debug=True)
