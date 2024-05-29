from flask import Flask, request
import requests
import openai

app = Flask(__name__)

# Replace with your credentials
PAGE_ACCESS_TOKEN = 'PAGE_ACCESS_TOKEN'
VERIFY_TOKEN = 'VERIFY_TOKEN'
OPENAI_API_KEY = 'OPENAI_API_KEY'

openai.api_key = OPENAI_API_KEY

# Store conversation history
user_conversations = {}


@app.route('/', methods=['GET'])
def verify():
    # Facebook Webhook Verification
    if request.args.get('hub.verify_token') == VERIFY_TOKEN:
        return request.args.get('hub.challenge')
    return 'Verification token mismatch', 403


@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                if messaging_event.get('message'):
                    sender_id = messaging_event['sender']['id']
                    message_text = messaging_event['message'].get('text')  # Use .get() to avoid KeyError

                    if message_text:
                        # Store the user's message
                        if sender_id not in user_conversations:
                            user_conversations[sender_id] = [
                                {"role": "system", "content": "You are an artificial intelligence that responds to users' messages on the Facebook Messenger application"}]
                        user_conversations[sender_id].append({"role": "user", "content": message_text})

                        response = generate_gpt_response(sender_id)
                        send_message(sender_id, response)
    return 'ok', 200


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


if __name__ == '__main__':
    app.run(debug=True, port=5000)
