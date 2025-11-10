import os
import argparse
import json
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- Configurações de Ambiente ---
endpoint = os.environ.get("AZURE_FORM_RECOGNIZER_ENDPOINT")
key = os.environ.get("AZURE_FORM_RECOGNIZER_KEY")
VM_IP = os.environ.get("VM_IP_PUBLICO", "SUA_VM_IP_AQUI") # Usado para instrução SCP

# --- Mapeamento de Campos e Configuração de Modelos ---
# Define as configurações de caminho e extração para cada modelo
MODEL_CONFIG = {
    "prebuilt-layout": {
        "description": "Extração de Layout e Texto Puro.",
        "path": "dados/documento-teste.jpeg", # Atualizado para a pasta 'dados/' e extensão '.jpeg'
        "extract_fields": False,
        "output_file": None
    },
    "prebuilt-invoice": {
        "description": "Extração de Campos de Fatura.",
        "path": "dados/fatura-teste.pdf",
        "extract_fields": {
            "InvoiceId": "ID da Fatura",
            "CustomerName": "Nome do Cliente",
            "InvoiceTotal": "Total da Fatura"
        },
        "output_file": "dados_fatura_extraidos.json" # Arquivo de saída para o Artefato
    }
}

def analyze_document(model_id, document_path):
    """
    Função unificada para análise de documentos com base no model_id.
    """
    if not endpoint or not key:
        print("ERRO: O ENDPOINT ou KEY não foi encontrado no arquivo .env.")
        return

    config = MODEL_CONFIG.get(model_id)
    if not config:
        print(f"ERRO: Modelo '{model_id}' não suportado ou não configurado.")
        print(f"Modelos suportados: {list(MODEL_CONFIG.keys())}")
        return

    # 1. Autenticação no Azure
    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    # Verifica a existência do arquivo
    if not os.path.exists(document_path):
        print(f"ERRO: Arquivo de documento não encontrado no caminho: {document_path}")
        
        # Cria a pasta 'dados/' se não existir
        os.makedirs(os.path.dirname(document_path) or "dados", exist_ok=True)
        
        print("\n*** AÇÃO NECESSÁRIA ***")
        print(f"Suba seu arquivo de teste ({document_path}) para a pasta '{os.path.dirname(document_path) or 'dados/'}'.")
        print(f"Exemplo de comando SCP (no seu terminal local, não no SSH):")
        print(f"scp /caminho/do/seu/arquivo kaurauser@{VM_IP}:/home/kaurauser/KAURA-PROJ-DOC-AI-GERENCIAMENTO-HUMANO/{document_path}")

        return

    print(f"Conectado ao Azure. Analisando documento: {document_path} usando modelo '{model_id}'...")

    try:
        # 2. Executa a análise
        with open(document_path, "rb") as f:
            poller = document_analysis_client.begin_analyze_document(
                model_id, document=f.read()
            )
            result = poller.result()

        print(f"\n--- Resultado da Análise ({config['description']}) ---")
        
        # Dicionário para armazenar dados extraídos (apenas para modelos de extração de campos)
        dados_extraidos = {} 
        
        # 3. Lógica de Extração e Output
        if config['extract_fields']:
            
            if result.documents:
                doc = result.documents[0]
                
                for campo_nome, campo_descricao in config['extract_fields'].items():
                    campo = doc.fields.get(campo_nome)
                    
                    valor = None
                    confianca = "N/A"
                    
                    if campo and campo.value is not None:
                        confianca = f"{campo.confidence:.2f}"
                        
                        # Tratamento específico para moeda (InvoiceTotal)
                        if campo_nome == "InvoiceTotal" and campo.value_currency:
                            valor_currency = campo.value_currency
                            valor = f"{valor_currency.amount} {valor_currency.currency_code or valor_currency.currency_symbol}"
                        else:
                            valor = str(campo.value)
                        
                        dados_extraidos[campo_nome] = {
                            "Valor": valor,
                            "Confianca": float(confianca) # Salvar como float no JSON
                        }
                        
                    # Imprime o resultado formatado
                    print(f"**{campo_descricao}** ({campo_nome}): {valor or 'Não Encontrado'} (Confiança: {confianca})")

                # --- 4. Salvar em JSON (para Artefato) ---
                if config['output_file']:
                    with open(config['output_file'], "w", encoding="utf-8") as f:
                        json.dump(dados_extraidos, f, indent=4, ensure_ascii=False)
                    print(f"\n✅ Resultado da extração salvo para Artefato: {config['output_file']}")
            
            else:
                print(f"Nenhum documento do tipo '{model_id}' detectado no arquivo.")
        
        else:
            # Lógica para modelos que extraem texto puro (prebuilt-layout)
            for page in result.pages:
                for line in page.lines:
                    print(line.content)
        
        print("---------------------------------------")

    except Exception as e:
        print(f"\nERRO DURANTE A ANÁLISE DO DOCUMENTO: {e}")

if __name__ == "__main__":
    # --- Configuração do Argument Parser ---
    parser = argparse.ArgumentParser(
        description="Script unificado para análise de documentos usando o Azure Document Intelligence."
    )
    
    # Argumento obrigatório para especificar o modelo
    parser.add_argument(
        '--model-id',
        required=True,
        choices=list(MODEL_CONFIG.keys()),
        help=f"ID do modelo do Azure Document Intelligence a ser utilizado. Opções: {list(MODEL_CONFIG.keys())}"
    )
    
    args = parser.parse_args()
    
    # Define o caminho do documento com base no modelo
    path = MODEL_CONFIG[args.model_id]["path"]
    
    # Inicia a análise
    analyze_document(args.model_id, path)
