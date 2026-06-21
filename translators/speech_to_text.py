from groq import Groq as grq
import os
from dotenv import load_dotenv
from logs import log_writer
#suprimir mensagens de erros do ALSA
from ctypes import cdll, CFUNCTYPE, c_char_p, c_int
_alsa_handler_ref = None

try:
    _HANDLER_TYPE = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
    _alsa_handler_ref = _HANDLER_TYPE(lambda *_: None)  # guardado na global
    cdll.LoadLibrary('libasound.so.2').snd_lib_error_set_handler(_alsa_handler_ref)
except Exception:
    pass

#continua normalmente
import speech_recognition as sr

load_dotenv()

GROQ_API_KEY=os.getenv('GROQ_API_KEY')

def criar_wav():
    recognizer = sr.Recognizer()
    TIMEOUT_AUDIO = 5
    TEMPO_MAXIMO_FALA = 30
    try:
        with sr.Microphone() as mic:
            recognizer.pause_threshold=2
            recognizer.energy_threshold=60
            try:
                print("Ouvindo microfone...\n\n")
                audio_data = recognizer.listen(mic,TIMEOUT_AUDIO,TEMPO_MAXIMO_FALA)

                wav_bytes = audio_data.get_wav_data()

                with open("audios/audio_input.wav","wb") as file:
                    file.write(wav_bytes)

                print(f"arquivo criado. Threshold foi: {recognizer.energy_threshold}\n\n\n")
            except Exception as e:
                log_writer.write(
                    f"{e}\nThreshold foi: {recognizer.energy_threshold}"
                    )
                

    except sr.WaitTimeoutError:
        log_writer.write(f"{sr.WaitTimeoutError}")

    except sr.UnknownValueError:
        log_writer.write(f"{sr.UnknownValueError}")


def receber_STT():
    #Inicia cliente groq
    client = grq(api_key=GROQ_API_KEY,timeout=5)

    #Caminho pro arquivo de audio
    filename = os.path.dirname(__file__) + "/audio_input.wav" # nome do arquivo

    # Open the audio file
    with open(filename, "rb") as file:
        #Criar Transcriçao
        transcription = client.audio.transcriptions.create(
        file=file, # Arquivo de audio
        model="whisper-large-v3-turbo", # Modelo para transcricao
        )
        language="pt-BR"
        return transcription.text

def pegar_transcricao():
    criar_wav()
    return receber_STT()