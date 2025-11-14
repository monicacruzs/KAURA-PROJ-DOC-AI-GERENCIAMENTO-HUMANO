import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentAnalysisFeature, AnalyzeDocumentRequest

# --- Configurações de Acesso (Deve vir do Key Vault) ---
# Substitua pelos valores reais.
endpoint = "SEU_ENDPOINT_DO_DOCUMENT_INTELLIGENCE"
key = "SUA_CHAVE_DO_DOCUMENT_INTELLIGENCE"

# O ID do Modelo customizado que você definiu e treinou no Studio (Exemplo: kaura-custom-v1)
# O model_id será passado para o cliente na chamada 'begin_analyze_document'
model_id = "SEU_MODEL_ID_CUSTOMIZADO" 

# --- Caminho do Arquivo para Análise ---
# Substitua pelo caminho do seu documento de teste.
document_path = "caminho/para/seu/documento_nao_padrao.pdf"

def analyze_custom_document(file_path: str, model_id: str):
    """
    Analisa um documento usando o modelo customizado treinado.
    """
    print(f"Iniciando análise com o modelo customizado: {model_id}...")
    
    # 1. Criação do Cliente
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=endpoint, 
        credential=AzureKeyCredential(key)
    )

    # 2. Leitura do Conteúdo do Arquivo
    try:
        with open(file_path, "rb") as f:
            document_content = f.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em {file_path}")
        return

    # 3. Análise do Documento
    # O model_id é a única mudança significativa em relação ao 'prebuilt-invoice'
    poller = document_intelligence_client.begin_analyze_document(
        # Especifica o model_id customizado
        model_id=model_id, 
        analyze_request=AnalyzeDocumentRequest(base64_source=document_content),
        # Se precisar de extração de tabelas/layout, mantenha esta opção
        features=[DocumentAnalysisFeature.OCR_HIGH_RESOLUTION] 
    )

    # 4. Obtenção dos Resultados
    result = poller.result()
    
    # 5. Processamento dos Resultados
    if result.documents:
        print("--- Resultados da Extração do Modelo Customizado ---")
        for analyzed_document in result.documents:
            print(f"Documento do Tipo: {analyzed_document.doc_type}")
            print("Campos extraídos:")
            
            # Itera sobre os campos que você rotulou e treinou
            for name, field in analyzed_document.fields.items():
                # O nome (name) será o nome que você deu ao campo no Studio (ex: "NomeCliente", "ValorTotal")
                value = field.content if field.content else "Não Encontrado"
                confidence = field.confidence
                print(f"  - {name}: {value} (Confiança: {confidence:.2f})")
    else:
        print("Nenhum documento detectado no resultado da análise.")

# --- Execução ---
# analyze_custom_document(document_path, model_id)
