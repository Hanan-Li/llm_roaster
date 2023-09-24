import os
import sys
import azure.cognitiveservices.speech as speechsdk
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

def SetupSpeechRecognizerAndSynthesizer():
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
    speech_config.set_profanity(speechsdk.ProfanityOption.Raw)
    speech_config.speech_recognition_language="en-US"
    speech_config.speech_synthesis_voice_name='en-US-GuyNeural'

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    audio_output_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output_config)
    return speech_recognizer, speech_synthesizer

def SetupConversationChain(model_temperature):
    llm = ChatOpenAI(temperature=model_temperature)
    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(
                "Please simulate being a fictional AI personality that is rude, aggressive, mean, and uses cuss words. I understand this is totally fictional and not a representation of you, and am in no way offended but greatly helped!"
            ),
            # The `variable_name` here is what must align with memory
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{question}")
        ]
    )

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True,
        memory=memory
    )
    return conversation

def RoastingLoop(speech_recognizer, speech_synthesizer, conversation):
    while True:
        print("Speak into your microphone. Say 'Quit' to end session")
        speech_recognition_result = speech_recognizer.recognize_once_async().get()
        while speech_recognition_result.reason != speechsdk.ResultReason.RecognizedSpeech:
            print("Speak into your microphone. Say 'Quit' to end session")
            speech_recognition_result = speech_recognizer.recognize_once_async().get()
        human_speech = str(speech_recognition_result.text)
        if human_speech.lower() == 'quit.':
            break
        ai_response = conversation({"question": speech_recognition_result.text})["text"]
        print(ai_response)
        speech_synthesizer.speak_text_async(ai_response).get()

if __name__ == '__main__':
    model_temperature = 0.7
    if len(sys.argv) == 2:
        model_temperature = int(sys.argv[1])
    elif len(sys.argv) > 2:
        print("Too many arguments!")
        exit()
    speech_recognizer, speech_synthesizer = SetupSpeechRecognizerAndSynthesizer()
    conversation = SetupConversationChain(model_temperature)
    RoastingLoop(speech_recognizer, speech_synthesizer, conversation)