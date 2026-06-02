import serial
import time


#limite dos servos:
# boca: 120,40
# olhos: 150 (esquerda), 35 (direita)
# palpebras: 160 (abertas), 40 (fechada)

porta_nome = "/dev/ttyUSB0"
baud_rate = 9600

try:
    with serial.Serial(porta_nome, baud_rate, timeout=2) as ser:
        time.sleep(2)
        while True:
            comando = input("Quais as posiçoes? ")
            ser.write(f"<{comando}>".encode('utf-8'))
            resposta = ser.readline()
            print(f"O arduino recebeu '{resposta.decode('utf-8').strip()}'")

except serial.SerialException as e:
    print(f"Ocorreu um erro ao conectar a porta: {e}")
except KeyboardInterrupt:
    print("\nEncerrado pelo usuario.")