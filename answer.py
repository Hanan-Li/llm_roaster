from flask import Flask, request
import roaster
from twilio.twiml.voice_response import Gather, VoiceResponse

app = Flask(__name__)

@app.route("/answer", methods=['GET', 'POST'])
def answer_call():
    """Respond to incoming phone calls with a brief message."""
    # Start our TwiML response
    response = VoiceResponse()
    # Read a message aloud to the caller
    gather = Gather(input='speech', action='/completed')
    response.append(gather)
    return str(response)

@app.route("/completed", methods=['GET', 'POST'])
def gather():
    response = VoiceResponse()
    text_input = request.values['SpeechResult']
    conversation = roaster.SetupConversationChain(0.8)
    ai_response = conversation({"question": text_input})["text"]
    response.say(ai_response, voice ='Polly.Amy')
    response.redirect('/answer')
    return str(response)
    

if __name__ == "__main__":
    app.run(debug=True)
