import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Variáveis de ambiente
endpoint = os.environ.get("AZURE_FORM_RECOGNIZER_ENDPOINT")
key = os.environ.get("AZURE_FORM_RECOGNIZER_KEY")

if not endpoint or not key:
    print("ERRO: O ENDPOINT ou KEY não foi encontrado no arquivo .env.")
    exit()

# 1. Autenticação no Azure
document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

# 2. Defina o caminho para o seu documento (caminho padrão do repositório)
document_path = "dados/lista-material-escolar.jpeg"

if not os.path.exists(document_path):
    print(f"ERRO: Arquivo de documento não encontrado no caminho: {document_path}")
    print("Vamos criar a pasta 'dados/' e usar um arquivo temporário para teste.")

    # Cria a pasta 'dados/' se não existir
    os.makedirs("dados", exist_ok=True)

    # Em um ambiente real, você usaria scp para subir o arquivo.
    # Aqui, vamos parar o script para você adicionar o arquivo.
    print("\n*** AÇÃO NECESSÁRIA ***")
    print(f"Suba seu arquivo de teste (ex: lista-material-escolar.jpeg) para a pasta 'dados/' na VM.")
    print("Você pode usar o comando `scp` no seu terminal local (NÃO NO SSH) ou a extensão VS Code.")
    print(f"scp /caminho/do/seu/arquivo kaurauser@{os.environ.get('VM_IP_PUBLICO')}:/home/kaurauser/KAURA-PROJ-DOC-AI-GERENCIAMENTO-HUMANO/dados/")

    exit() # Encerra o script para o usuário adicionar o arquivo

print(f"Conectado ao Azure. Analisando documento: {document_path}...")

try:
    # 3. Executa a análise de layout (modelo 'prebuilt-layout')
    with open(document_path, "rb") as f:
        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-layout", document=f.read()
        )
        result = poller.result()

    # 4. Exibe o resultado (o texto puro extraído)
    print("\n--- Resultado da Análise de Documento ---")
    for page in result.pages:
        for line in page.lines:
            print(line.content)
    print("---------------------------------------")

except Exception as e:
    print(f"\nERRO DURANTE A ANÁLISE DO DOCUMENTO: {e}")
