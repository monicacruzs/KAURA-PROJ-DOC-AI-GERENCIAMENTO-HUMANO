import logging
import json
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import azure.cognitiveservices.speech as speechsdk
import os
import base64 # Usaremos para receber o áudio no corpo da requisição

# Configurações do Key Vault
KEY_VAULT_NAME = "kvkauradocaisecprod002"
KEY_VAULT_URI = f"https://{KEY_VAULT_NAME}.vault.azure.net/"
SPEECH_KEY_SECRET_NAME = "SPEECH-KEY"
SPEECH_REGION_SECRET_NAME = "SPEECH-REGION"

def get_speech_credentials():
    """Obtém a chave e região do Azure AI Speech do Key Vault usando a MI."""
    try:
        # DefaultAzureCredential detecta a Identidade Gerenciada (MI) do Function App
        credential = DefaultAzureCredential()
        secret_client = SecretClient(vault_url=KEY_VAULT_URI, credential=credential)

        speech_key = secret_client.get_secret(SPEECH_KEY_SECRET_NAME).value
        speech_region = secret_client.get_secret(SPEECH_REGION_SECRET_NAME).value
        
        logging.info("Credenciais do Azure AI Speech recuperadas do Key Vault com sucesso.")
        return speech_key, speech_region

    except Exception as e:
        logging.error(f"Erro ao obter credenciais do Key Vault: {e}")
        return None, None

def transcribe_audio_data(audio_data, speech_key, speech_region):
    """Realiza a transcrição do áudio em memória (wav/mp3)"""
    try:
        speech_config = speechsdk.SpeechConfig(
            subscription=speech_key, 
            region=speech_region
        )
        speech_config.speech_recognition_language = "pt-BR" 

        # Cria um stream de áudio a partir dos dados binários (em memória)
        audio_stream = speechsdk.audio.PushAudioInputStream()
        audio_stream.write(audio_data)
        audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)

        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, 
            audio_config=audio_config
        )

        result = speech_recognizer.recognize_once_async().get()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            return "Nenhuma fala reconhecida."
        else:
            cancellation = result.cancellation_details
            return f"Transcrição cancelada: {cancellation.reason}. Detalhes: {cancellation.error_details}"

    except Exception as e:
        logging.error(f"Erro durante a transcrição: {e}")
        return f"Erro interno durante a transcrição: {e}"


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function (KAURA-SPEECH-REC) processed a request.')

    # --- 1. Obter Credenciais de Forma Segura (MI -> Key Vault) ---
    #speech_key, speech_region = get_speech_credentials()
    # NO SEU CODIGO PYTHON TEMPORARIAMENTE:
    speech_key = "FQcGYXxcR3jpm8vZ3WRxP21jRHBG3hvN8xPz0N4f8djXBzRqqhAEJQQJ99BKACZoyfiXJ3w3AAAYACOGxWyt" 
    speech_region = "brazilsouth"
    if not speech_key:
        return func.HttpResponse(
             "Erro na configuração de segurança: Falha ao obter credenciais do Key Vault.",
             status_code=500
        )

    # --- 2. Receber o Arquivo de Áudio ---
    try:
        # Espera o áudio codificado em Base64 no corpo da requisição JSON
        req_body = req.get_json()
        audio_base64 = req_body.get('audio_base64')
        if not audio_base64:
            return func.HttpResponse(
                 "Por favor, envie o campo 'audio_base64' no corpo da requisição.",
                 status_code=400
            )
        
        # Decodifica para dados binários
        audio_data = base64.b64decode(audio_base64)
        logging.info(f"Dados de áudio recebidos. Tamanho: {len(audio_data)} bytes.")

    except ValueError:
        return func.HttpResponse(
             "Erro ao decodificar JSON ou Base64.",
             status_code=400
        )
    
    # --- 3. Transcrever ---
    transcription = transcribe_audio_data(audio_data, speech_key, speech_region)

    # --- 4. Retornar Resultado ---
    response_data = {
        "transcription_result": transcription
    }

    return func.HttpResponse(
        json.dumps(response_data),
        mimetype="application/json",
        status_code=200
    )
