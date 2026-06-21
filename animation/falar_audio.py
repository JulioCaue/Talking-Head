import librosa
import numpy as np
import time
import serial
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
import pyaudio

def dublar_audio():
    # --- variaveis para serial ---
    PORTA_NOME = "/dev/ttyUSB0"
    BAUD_RATE = 115200

    # --- variaveis de movimento ---
    boca_min_pos = 40
    boca_max_pos = 140
    RMS_MAX = 0.3
    ALPHA = 0.35
    angulo_anterior = float(boca_min_pos)

    # --- variaveis de audio ---
    ARQUIVO_AUDIO = "audios/audio_output.wav"
    TAMANHO_CHUNK = 1024

    y, sr = librosa.load(ARQUIVO_AUDIO, sr=44100)

    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paFloat32, channels=1, rate=int(sr), output=True,frames_per_buffer=TAMANHO_CHUNK
    )

    frame_start = 0

    # --- inicio da conexão ---
    with serial.Serial(PORTA_NOME, BAUD_RATE, timeout=2) as ser:
        print (f"Conectado com arduino na porta {PORTA_NOME}")

        try:
            while frame_start < len(y):
                chunk_audio = y[frame_start : frame_start + TAMANHO_CHUNK]
                
                if len(chunk_audio) < TAMANHO_CHUNK:
                    chunk_audio = np.pad(
                        chunk_audio, (0, TAMANHO_CHUNK - len(chunk_audio))
                    )

                rms = np.sqrt(np.mean(chunk_audio**2))

                if np.isnan(rms):
                    rms = 0.0

                angulo_calculado = boca_min_pos + (rms / RMS_MAX) * (boca_max_pos - boca_min_pos)
                angulo_suavizado = ALPHA * angulo_calculado + (1 - ALPHA) * angulo_anterior
                angulo_anterior = angulo_suavizado
                angulo_final = int(round(angulo_suavizado))

                boca_aberta = True if angulo_final > boca_min_pos else False

                print(f"RMS: {rms:.4f} | Aberta: {boca_aberta} | Ângulo: {angulo_final}°")

                stream.write(chunk_audio.astype(np.float32).tobytes())
                ser.write(f"<{angulo_final},90,90,40>".encode('utf-8'))

                frame_start += TAMANHO_CHUNK

        except KeyboardInterrupt:
            log_writer.write("Encerrado pelo usuário.")
        except Exception as e:
            log_writer.write(f"{e}")
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()