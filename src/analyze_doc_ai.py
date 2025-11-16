
import os
import argparse
import json
# Adicionar imports necessários para Key Vault
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from dotenv import load_dotenv

# --- NOVOS IMPORTS PARA KEY VAULT ---
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
# ------------------------------------

# Carrega as variáveis de ambiente do arquivo .env (útil para desenvolvimento local)
load_dotenv()

# --- Configurações de Ambiente ---
# O ENDPOINT DEVE SER PASSADO COMO VARIÁVEL DE AMBIENTE (não está no Key Vault)
endpoint = os.environ.get("AZURE_FORM_RECOGNIZER_ENDPOINT")
VM_IP = os.environ.get("VM_IP_PUBLICO", "SUA_VM_IP_AQUI")

# --- NOVAS CONFIGURAÇÕES DE KEY VAULT ---
KEY_VAULT_URI = os.environ.get("AZURE_KEY_VAULT_URI", "https://kvkauradocaisecprod002.vault.azure.net/")
SECRET_NAME = "document-intelligence-key"
# ----------------------------------------

# Define as configurações de caminho e extração para cada modelo... (resto do código omitido)
MODEL_CONFIG = {
   
    "prebuilt-layout": {
        "description": "Extração de Layout e Texto Puro.",
        "path": "dados/documento-teste.jpeg", 
        "extract_fields": False,
        "output_file": "outputs/dados_layout_extraidos.txt" 
    },
    "prebuilt-invoice": {
        "description": "Extração de Campos de Fatura.",
        "path": "dados/fatura-teste.pdf",
        "extract_fields": {
            "InvoiceId": "ID da Fatura",
            "CustomerName": "Nome do Cliente",
            "InvoiceTotal": "Total da Fatura"
        },
        "output_file": "outputs/dados_fatura_extraidos.json"
    },
    "kaura-custom-viagem-v4": {
        "description": "Extração de Campos Customizados de Viagem (Neural v4).",
        "path": "dados/documento_viagem_teste.pdf", # Crie um novo PDF de teste nesta pasta
        "extract_fields": {
            "Nome_do_Colaborador": "Nome",
            "Centro_de_Custo": "Centro de Custo",
            "Data_de_Inicio_da_Viagem": "Início da Viagem",
            "Data_de_Fim_da_Viagem": "Fim da Viagem",
            "Valor_Total_Aprovado": "Valor Total",
            "Status_de_Aprovacao": "Status de Aprovação"
        },
        "output_file": "outputs/dados_viagem_extraidos.json" 
    }
}


def get_secret_from_key_vault(vault_uri, secret_name):
    """
    Tenta obter o segredo do Azure Key Vault usando DefaultAzureCredential.
    """
    try:
        print(f"Buscando chave '{secret_name}' no Key Vault: {vault_uri}...")
        
        # Usa DefaultAzureCredential para tentar autenticar
        credential = DefaultAzureCredential()
        
        secret_client = SecretClient(vault_url=vault_uri, credential=credential)
        key_value = secret_client.get_secret(secret_name).value
        
        print("✅ Chave obtida do Key Vault com sucesso.")
        return key_value
        
    except Exception as e:
        print(f"⚠️ ERRO ao acessar o Key Vault. Detalhes: {e}")
        # Retorna None se falhar, forçando o script a buscar no ambiente/fallback
        return None


def analyze_document(model_id, document_path):
    """
    Função unificada para análise de documentos com base no model_id.
    """
    
    # Obtém a chave APENAS do Key Vault(melhor prática de segurança)
    key = get_secret_from_key_vault(KEY_VAULT_URI, SECRET_NAME)

    # 1. VERIFICAÇÃO DE SEGURANÇA OBRIGATÓRIA
    if not endpoint:
        print("ERRO: O ENDPOINT (AZURE_FORM_RECOGNIZER_ENDPOINT) não foi encontrado no ambiente.")
        return
    
    if not key:
        # Se get_secret_from_key_vault retornou None, para a execução.
        print("ERRO CRÍTICO: Chave não pôde ser obtida do Azure Key Vault.")
        return

    config = MODEL_CONFIG.get(model_id)
    
    # Autenticação no Azure (AGORA USANDO A CHAVE OBTIDA COM SEGURANÇA)
    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    # Verifica a existência do arquivo no workspace do GitHub Actions
    if not os.path.exists(document_path):
        print(f"ERRO: Arquivo de documento não encontrado no caminho: {document_path}")
        print("\n*** AÇÃO NECESSÁRIA ***")
        print(f"Confirme se o arquivo de teste ({document_path}) foi comitado para a pasta 'dados/' do repositório.")
        return # <--- CORREÇÃO: Use 'return' para parar a execução
        
    print(f"Conectado ao Azure. Analisando documento: {document_path} usando modelo '{model_id}'...")
    
    try:
    # 2. Executa a análise (Abre o arquivo e inicia o poller)
        with open(document_path, "rb") as f:
            poller = document_analysis_client.begin_analyze_document(
                model_id, document=f.read()
            )
            result = poller.result() # Esta linha pode gerar exceções de rede/API
            
        print(f"\n--- Resultado da Análise ({config['description']}) ---")
        
        
        # ------------------------------------------------------------------
        # 3. Lógica de Extração e Output (Projeto 4: Modelos Estruturados: Faturas OU Customizados)
        # ------------------------------------------------------------------
        if config['extract_fields']:
            dados_extraidos = {}
            
            if result.documents:
                doc = result.documents[0]
                
                # --- Lógica de loop e extração dos campos ---
                print("Extraindo os campos do documento...")
                
                # Itera sobre os campos definidos no MODEL_CONFIG
                for field_name, friendly_name in config['extract_fields'].items():
                    field = doc.fields.get(field_name)
                    
                    valor = None
                    confianca = 0.0
                    
                    if field:
                        valor = field.value
                        confianca = field.confidence if field.confidence is not None else 0.0
                        
                        # Trata objetos de valor (como datas, números ou objetos complexos)
                        if hasattr(valor, 'isoformat'): # Trata datas/tempos
                            valor = valor.isoformat()
                        elif hasattr(valor, 'text') and valor.text is not None:
                             valor = valor.text
                        elif isinstance(valor, dict): # Trata casos em que o valor é um dicionário
                             # Geralmente usamos apenas o texto extraído para simplificar
                            valor = field.value.text
                            
                    
                    # Adiciona ao dicionário de saída
                    dados_extraidos[field_name] = {
                        "valor": valor,
                        "confianca": round(confianca, 2)
                    }
                    
                    # Imprime no console para debug (como no log que você viu)
                    print(f"  {friendly_name}: {valor} (Confiança: {round(confianca, 2)})")
                        
                    else:
                        print(f"  {friendly_name}: (Não encontrado)")
                        dados_extraidos[field_name] = {"valor": None, "confianca": "0.00"}

                # --- 4. Salvar em JSON (para Artefato do Projeto) ---
                if config['output_file']:
                   # ADICIONE ISTO: Cria a pasta 'outputs/' se não existir.
                    os.makedirs('outputs/', exist_ok=True)
                    with open(config['output_file'], "w", encoding="utf-8") as f:
                        json.dump(dados_extraidos, f, indent=4, ensure_ascii=False)
                    print(f"\n✅ Resultado da extração salvo para Artefato: {config['output_file']}")
                    
            else:
                print(f"Nenhum documento do tipo '{model_id}' detectado no arquivo.")
                
        # ------------------------------------------------------------------
        # 3. Lógica de Extração e Output (Modelos Estruturados: Projeto 2 - Faturas)
        # ------------------------------------------------------------------
        if config['extract_fields']:
            dados_extraidos = {}
            
            if result.documents:
                doc = result.documents[0]
                
                # ... (Lógica de loop e extração dos campos) ...
                
                # --- 4. Salvar em JSON (para Artefato do Projeto 2) ---
                if config['output_file']:
                    with open(config['output_file'], "w", encoding="utf-8") as f:
                        json.dump(dados_extraidos, f, indent=4, ensure_ascii=False)
                    print(f"\n✅ Resultado da extração salvo para Artefato: {config['output_file']}")
                    
            else:
                print(f"Nenhum documento do tipo '{model_id}' detectado no arquivo.")
                
        # ------------------------------------------------------------------
        # 3. Lógica de Extração e Output (Modelos de Layout: Projeto 1 - Layout/OCR)
        # ------------------------------------------------------------------
        else: # Entra aqui se config['extract_fields'] é False
            output_text = ""
            # ... (Lógica de loop e extração de texto) ...
            
            # 2. Salvar em TXT (para Artefato do Projeto 1)
            if config['output_file']:
                with open(config['output_file'], "w", encoding="utf-8") as f:
                    f.write(output_text)  
                print(f"\n✅ Resultado do layout salvo para Artefato: {config['output_file']}")
            
        print("---------------------------------------")

    except Exception as e:
        print(f"\nERRO DURANTE A ANÁLISE DO DOCUMENTO: {e}")

if __name__ == "__main__":
    # --- Configuração do Argument Parser --- (seu código original aqui)
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
