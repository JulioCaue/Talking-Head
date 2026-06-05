import scipy.io.wavfile as wav
import sounddevice as sd


def Tocar_Wav():
    sample_rate,data = wav.read("audio_output.wav")
    sd.play(data,sample_rate)
    sd.wait()