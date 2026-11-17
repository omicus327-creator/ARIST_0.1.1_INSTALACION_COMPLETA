from __future__ import annotations

class Voice:
    def __init__(self, microphone=None):
        self.microphone=microphone; self.sr=None; self.tts=None
        try:
            import speech_recognition as sr
            self.sr=sr; self.rec=sr.Recognizer()
        except Exception: self.rec=None
        try:
            import pyttsx3
            self.tts=pyttsx3.init(); self.tts.setProperty('rate',175)
        except Exception: self.tts=None
    def say(self,text):
        print('ARIST:',text)
        if self.tts:
            try: self.tts.say(text); self.tts.runAndWait()
            except Exception: self.tts=None
    def listen(self,timeout=8,limit=20):
        if not self.rec: raise RuntimeError('Instala dependencias de voz: pip install -r requirements-voice.txt')
        with self.sr.Microphone(device_index=self.microphone) as source:
            self.rec.adjust_for_ambient_noise(source,duration=.4)
            audio=self.rec.listen(source,timeout=timeout,phrase_time_limit=limit)
        return self.rec.recognize_google(audio,language='es-MX')
    def wake_loop(self, callback, wake_word='arist', model_path=''):
        try:
            from vosk import Model, KaldiRecognizer
            import json, pyaudio
        except Exception as e: raise RuntimeError('Para palabra clave instala requirements-voice.txt y requirements-wakeword.txt') from e
        if not model_path: raise RuntimeError('Configura ARIST_VOSK_MODEL_PATH con la carpeta del modelo español Vosk descargado.')
        model=Model(model_path); pa=pyaudio.PyAudio(); stream=pa.open(format=pyaudio.paInt16,channels=1,rate=16000,input=True,frames_per_buffer=8000); stream.start_stream()
        rec=KaldiRecognizer(model,16000)
        self.say(f'Activación por palabra clave habilitada. Di {wake_word}.')
        try:
            while True:
                data=stream.read(4000,exception_on_overflow=False)
                if rec.AcceptWaveform(data):
                    text=json.loads(rec.Result()).get('text','').lower()
                    if wake_word.lower() in text:
                        self.say('Te escucho.')
                        try: callback(self.listen(timeout=8,limit=25))
                        except Exception as e: self.say(f'No pude procesar la instrucción: {e}')
        finally:
            stream.stop_stream(); stream.close(); pa.terminate()
