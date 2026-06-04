from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")

def perguntar_ia(input_do_usuario):
  cliente=genai.Client(api_key=GEMINI_API_KEY)

  resposta = cliente.models.generate_content(
    model= "gemini-2.5-flash",
    contents= f"{input_do_usuario}\n Nao use sinais de formatacao, porem mantenha sinais gramaticais basicos. E diga 'ola mundo!' no final para eu garantir que essa instrucao funcionou. Pode dizer que falou ola mundo por conta desse pedido aqui."
  )

  print(f"Prompt foi: {input_do_usuario}\n\nResposta foi: {resposta.text}")