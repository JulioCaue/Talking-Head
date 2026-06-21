import serial
import time
import numpy as np
import subprocess
import os
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

def imitar_fala():
    #limite dos servos:
    # boca: 120, 40
    # olhos: 150 (esquerda), 35 (direita)
    # palpebras: 160 (abertas), 40 (fechada)

    PORTA_NOME = "/dev/ttyUSB0"
    BAUD_RATE = 115200
    CHUNK_SIZE = 128
    AUDIO_FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    boca_min_pos = 40
    boca_max_pos = 140

    THRESHOLD_ABRIR  = 2100
    THRESHOLD_FECHAR = 2000
    ALPHA = 0.4

    angulo_anterior = float(boca_min_pos)
    boca_aberta = False

    pa=pyaudio.PyAudio()
    stream = pa.open(
        format=AUDIO_FORMAT,
        channels=CHANNELS,
        rate = RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )
    try:
        with serial.Serial(PORTA_NOME, BAUD_RATE, timeout=2) as ser:
            time.sleep(2)
            print (f"Conectado com arduino na porta {PORTA_NOME}")

            print("Microfone ativo. Fale para mover boca... (ctrl + c para parar)")

            intervalo_limpesa = 15
            proxima_limpesa = time.time() + intervalo_limpesa

            while True:
                #ler data binaria do audio da stream do microfone
                data = stream.read(CHUNK_SIZE,exception_on_overflow=False)
                
                #converter data binaria para float para evitar overflow
                audio_data=np.frombuffer(data,dtype=np.int16).astype(np.float32)

                #computar raiz quadrada media para determinar a amplitude do volume
                rms = np.sqrt(np.mean(audio_data**2))

                #proteçao contra audio silencioso ou corrompido 
                if np.isnan(rms):
                    rms=0.0

                # -- logica de mapeamento --
                #ajustar o volume maximo dependendo da sensibilidade do microfone
                max_volume = 8000.0

                if not boca_aberta and rms >= THRESHOLD_ABRIR:
                    boca_aberta = True
                elif boca_aberta and rms < THRESHOLD_FECHAR:
                    boca_aberta = False

                if not boca_aberta:
                    servo_angle = boca_min_pos

                else:
                    #normalizar volume do som entre 0.0 e 1.0
                    normalised_volume = min(rms / max_volume, 1.0)
                    #transformar em angulo
                    servo_angle = int(boca_min_pos + normalised_volume * (boca_max_pos - boca_min_pos))

                angulo_suavizado = ALPHA * servo_angle + (1 - ALPHA) * angulo_anterior
                angulo_anterior = angulo_suavizado
                angulo_final = int(round(angulo_suavizado))

                if angulo_final < 63:
                    angulo_final = 40
                    boca_aberta = False

                print(f"RMS: {rms:.1f} | Aberta: {boca_aberta} | Ângulo: {angulo_final}°")

                ser.write(f"<{angulo_final},90,90,40>".encode('utf-8'))


                if time.time() >= proxima_limpesa:
                    subprocess.run('cls' if os.name == 'nt' else 'clear')
                    proxima_limpesa = time.time() + intervalo_limpesa

                time.sleep(0.025)

    except serial.SerialException as e:
        log_writer.write(f"Ocorreu um erro ao conectar a porta: {e}")
    except KeyboardInterrupt:
        log_writer.write("Encerrado pelo usuário.")
    except Exception as e:
        log_writer.write(f"\n{e}.")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()