from datetime import datetime

def write(error_line):
    caminho_pastas = "logs/errors/"
    ftype = ".txt"
    agora = datetime.now()
    dia_hoje = agora.strftime("%d-%m-%Y")
    hora_agora = agora.strftime("%H:%M:%S")

    with open(f"{caminho_pastas}{dia_hoje}{ftype}","a") as file:
        file.write(f"[{hora_agora}]: {error_line}\n")