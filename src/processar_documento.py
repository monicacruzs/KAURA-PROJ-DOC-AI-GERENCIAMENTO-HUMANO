# processar_documento.py

import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

# VARIÁVEIS DE AMBIENTE (SUBSTITUIR PELAS SUAS CHAVES ANOTADAS)
# --- ESTAS CHAVES SÃO A PROVA DE AUTENTICAÇÃO E CUSTO ZERO ---
AZURE_ENDPOINT = "SEU_ENDPOINT_AQUI" # Ex: https://kaura-doc-ai.cognitiveservices.azure.com/
AZURE_KEY = "SUA_CHAVE_AQUI" # Ex: 123456789abcdef123456789abcdef

# Caminho para o arquivo que será processado (Lista Escolar)
CAMINHO_DO_DOCUMENTO = "documento_a_analisar.jpg"

def analisar_documento_com_ocr():
    """
    Realiza a análise de um documento usando o modelo 'prebuilt-read' do Azure Document Intelligence.
    Este modelo é otimizado para extração de texto genérico (OCR).
    """
    if not os.path.exists(CAMINHO_DO_DOCUMENTO):
        print(f"ERRO: Arquivo não encontrado em {CAMINHO_DO_DOCUMENTO}")
        return

    print("--- INICIANDO ANÁLISE ---")
    try:
        # 1. Autenticação e Criação do Cliente
        document_analysis_client = DocumentAnalysisClient(
            endpoint=AZURE_ENDPOINT, 
            credential=AzureKeyCredential(AZURE_KEY)
        )

        # 2. Leitura do Conteúdo do Documento
        with open(CAMINHO_DO_DOCUMENTO, "rb") as f:
            document_content = f.read()

        # 3. Chamada Assíncrona para Análise
        # 'prebuilt-read' é o modelo de OCR que extrai todo o texto.
        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-read", document_content
        )
        
        # 4. Aguardar e Obter o Resultado
        result = poller.result()
        print("--- ANÁLISE CONCLUÍDA ---")

        # 5. Extração e Apresentação do Texto Completo (OCR)
        full_text = result.content
        
        # 6. Salvando o resultado na arquitetura KAURA (output/)
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "resultado_ocr_kaura.txt")
        
        with open(output_file, "w", encoding="utf-8") as out_f:
            out_f.write(f"--- Texto Completo Extraído do KAURA-PROJ-DOC-AI-GERENCIAMENTO-HUMANO ---\n\n")
            out_f.write(full_text)

        print("\n=============================================")
        print(f"✅ SUCESSO: Texto Completo Salvo em: {output_file}")
        print("=============================================\n")

    except Exception as e:
        print(f"Ocorreu um erro durante a análise: {e}")

if __name__ == "__main__":
    analisar_documento_com_ocr()
