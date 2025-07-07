from flask import Flask, request, render_template

app = Flask(__name__)
result = None


@app.route('/home')
def greet():
    return "Hello!"


@app.route('/', methods=['POST'])
def receive_sms():
    # Get the message content and sender phone number from the request
    data = request.get_json()
    message_body = data['Body']
    sender_phone = data['From']

    global result
    result = message_body
    print("Phone:", sender_phone, "Message:", message_body)
    func = request.environ.get('werkzeug.server.shutdown')
    func()
    return "Server shutting down..."


def start():
    app.run(host='0.0.0.0', port=5000)
    return result

