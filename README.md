# Messenger-OpenAI-GPT-chatbot
Flask application that integrates with the Facebook Messenger API and OpenAI's GPT-4 to create an automated chatbot.

This code is a simple Flask application that integrates with the Facebook Messenger API and OpenAI's GPT-4 to create an automated chatbot. Here's a breakdown of what each part of the code does:

### Imports and Initialization
```python
from flask import Flask, request
import requests
import openai

app = Flask(__name__)
```
- `Flask`: A web framework for creating web applications in Python.
- `request`: A Flask object to handle incoming HTTP requests.
- `requests`: A library to send HTTP requests to the Facebook Messenger API.
- `openai`: A library to interact with OpenAI's GPT-4 API.

### Configuration and API Keys
```python
# Replace with your credentials
PAGE_ACCESS_TOKEN = 'YOUR_FACEBOOK_PAGE_ACCESS_TOKEN'
VERIFY_TOKEN = 'YOUR_VERIFICATION_TOKEN'
OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY'

openai.api_key = OPENAI_API_KEY
```
- `PAGE_ACCESS_TOKEN`: Token to authenticate with the Facebook Messenger API.
- `VERIFY_TOKEN`: Token used to verify the webhook setup with Facebook.
- `OPENAI_API_KEY`: Key to access OpenAI's API.

### Data Storage
```python
# Store conversation history
user_conversations = {}
```
- `user_conversations`: A dictionary to store conversation histories for each user.

### Verification Endpoint
```python
@app.route('/', methods=['GET'])
def verify():
    # Facebook Webhook Verification
    if request.args.get('hub.verify_token') == VERIFY_TOKEN:
        return request.args.get('hub.challenge')
    return 'Verification token mismatch', 403
```
- This endpoint is used by Facebook to verify the webhook URL. If the verification token matches, it responds with the challenge sent by Facebook.

### Webhook Endpoint
```python
@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                if messaging_event.get('message'):
                    sender_id = messaging_event['sender']['id']
                    message_text = messaging_event['message']['text']
                    
                    # Store the user's message
                    if sender_id not in user_conversations:
                        user_conversations[sender_id] = [{"role": "system", "content": "You are a friendly and helpful assistant."}]
                    user_conversations[sender_id].append({"role": "user", "content": message_text})
                    
                    response = generate_gpt_response(sender_id)
                    send_message(sender_id, response)
    return 'ok', 200
```
- This endpoint handles incoming messages from Facebook Messenger.
- It processes each message, updates the conversation history, generates a response using GPT-4, and sends the response back to the user.

### Generate GPT-4 Response
```python
def generate_gpt_response(sender_id):
    # Retrieve the conversation history
    messages = user_conversations[sender_id]
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    
    # Store the assistant's response
    assistant_message = response['choices'][0]['message']['content'].strip()
    user_conversations[sender_id].append({"role": "assistant", "content": assistant_message})
    
    return assistant_message
```
- This function generates a response from GPT-4 based on the conversation history.
- The conversation history is updated with the assistant's response.

### Send Message to Facebook Messenger
```python
def send_message(recipient_id, message_text):
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'recipient': {'id': recipient_id},
        'message': {'text': message_text}
    }
    url = f'https://graph.facebook.com/v12.0/me/messages?access_token={PAGE_ACCESS_TOKEN}'
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        print(f'Unable to send message: {response.text}')
```
- This function sends a message to the user via the Facebook Messenger API.
- It constructs the HTTP request with the recipient ID and message text, then posts it to the Messenger API.

### Run the Application
```python
if __name__ == '__main__':
    app.run(debug=True, port=5000)
```
- This block starts the Flask web server on port 5000 in debug mode.

### Summary
1. The Flask application listens for verification and message events from Facebook Messenger.
2. Incoming messages are processed and stored in a conversation history.
3. A response is generated using OpenAI's GPT-4 model based on the conversation history.
4. The response is sent back to the user via the Facebook Messenger API.
