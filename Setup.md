# 🛠️ SETUP.md: Provisionamento e Desprovisionamento Azure CLI (KAURA)

Este documento detalha o passo a passo técnico para provisionar e desprovisionar os recursos do Azure necessários para o projeto **Assistente de Gerenciamento de Documentos Centrado no Ser Humano (Doc Intelligence no Azure)**, usando a linha de comando (Azure CLI).

**⚠️ ESTRATÉGIA DE CUSTO (FINOPS):**
O projeto segue uma rigorosa política de **Custo Zero**. O provisionamento é dividido em duas fases:
1.  **Fase 1 (Custo Zero - PaaS):** Criação do Grupo de Recursos e do Serviço de IA (Document Intelligence) em Tier Gratuito (F0).
2.  **Fase 2 (Custo por Hora - IaaS):** Criação da Máquina Virtual (VM) para execução do script, com a meta de execução e **desprovisionamento total em no máximo 2 horas**.

---
## 1. FASE 1: PROVISIONAMENTO (CUSTO ZERO - PAAS)

Estes comandos criam o "container" do projeto e os serviços de PaaS de custo zero. Eles devem ser executados no **Azure Cloud Shell** ou em um ambiente com o Azure CLI instalado.


### 1.1. Configuração e Criação do Serviço de IA

Copie e cole este bloco no seu terminal:

```bash
# -- 1. VARIÁVEIS --
# Defina o Resource Group (Container) e a Localização (brazilsouth)
RESOURCE_GROUP_NAME="RG-KAURA-DOC-AI"
LOCATION="brazilsouth" 
AI_SERVICE_NAME="kaura-doc-ai-service-kaura" # Lembre-se: Deve ser único globalmente.

# 2. CRIA O GRUPO DE RECURSOS
echo "Criando o Grupo de Recursos: $RESOURCE_GROUP_NAME..."
az group create \
    --name $RESOURCE_GROUP_NAME \
    --location $LOCATION

# 3. CRIA O SERVIÇO DE DOCUMENT INTELLIGENCE (SKU F0 É GRATUITO)
echo "Criando o Serviço de Document Intelligence (SKU F0 - GRÁTIS)..."
az cognitiveservices account create \
    --name $AI_SERVICE_NAME \
    --resource-group $RESOURCE_GROUP_NAME \
    --location $LOCATION \
    --kind "FormRecognizer" \
    --sku "F0" \
    --yes
```

---

### 1.2. Criação e Configuração do Key Vault (Melhoria de Segurança)

Este passo cria o Key Vault para armazenar a chave secreta do DI, seguindo as melhores práticas.

**1. Registrar o Provedor de Recursos:**
```bash
az provider register --namespace 'Microsoft.KeyVault'
```
**2. Criação do Key Vault:**
Utilizamos o SKU standard e desabilitamos a autorização RBAC inicial para usarmos as políticas de acesso legadas, que são mais simples de configurar neste contexto.

🔑 KeyVaultName: kvkauradocaisecprod002 (Nome que você usou em todo o CI/CD)

```bash
az keyvault create \
  --name "kvkauradocaisecprod002" \
  --resource-group "RG-KAURA-DOC-AI" \
  --location "brazilsouth" \
  --sku "standard" \
  --enable-rbac-authorization false
  ```
**3. Obter e Armazenar a Chave do Document Intelligence:**

Este é o passo mais importante: a chave do DI sai do Portal e entra no Key Vault.

- Passo Manual: Obtenha a Key 1 do seu recurso AI.

- Armazenar no KV: Substitua [CHAVE_DOCUMENT_INTELLIGENCE_AQUI] pelo valor copiado:

```bash
az keyvault secret set \
  --vault-name "kvkauradocaisecprod002" \
  --name "document-intelligence-key" \
  --value "[CHAVE_DOCUMENT_INTELLIGENCE_AQUI]"
  ```
**4. Definir a Política de Acesso para Teste Local (Opcional):**

Este passo define uma política de acesso que permite à sua conta de usuário (não o Service Principal) ler o segredo do Key Vault, sendo útil para testes de desenvolvimento local.

```bash
# 1. Obtém seu Object ID
OBJECT_ID=$(az ad signed-in-user show --query id -o tsv)
 
# 2. Define permissão 'get' e 'list' de segredos no Key Vault para sua conta
az keyvault set-policy \
  --name "kvkauradocaisecprod002" \
  --object-id "$OBJECT_ID" \
  --secret-permissions get list
 ```

---

### 1.3. Obter Credenciais Finais (Endpoint e IDs)
Este passo é necessário para obter o Endpoint (URL) (que não vai para o KV) e para documentar o Tenant/Subscription IDs, que são necessários para o CI/CD (OIDC) e para a fase inicial de teste na VM.

⚠️ ALERTA DE SEGURANÇA: O resultado destes comandos deve ser anotado em um local seguro e JAMAIS salvo publicamente neste repositório.

```bash
# 1. Obter o PONTO DE EXTREMIDADE (ENDPOINT)
echo "Anote o Ponto de Extremidade (AZURE_ENDPOINT):"
az cognitiveservices account show \
    --name $AI_SERVICE_NAME \
    --resource-group $RESOURCE_GROUP_NAME \
    --query endpoint -o tsv

# 2. Obter a CHAVE DE ACESSO (KEY1)
echo "Anote a Chave de Acesso (AZURE_KEY):"
az cognitiveservices account keys list \
    --name $AI_SERVICE_NAME \
    --resource-group $RESOURCE_GROUP_NAME \
    --query key1 -o tsv
```
## FASE 2: PROVISIONAMENTO IaaS (VM) E EXECUÇÃO (2 HORAS)
⚠️ ALERTA DE CUSTO: O custo da Máquina Virtual Standard_B2s inicia no momento em que o comando az vm create é executado.

2.1. Criação da VM e Rede

```bash
# -- 1. VARIÁVEIS DA VM --
VM_NAME="KAURA-VM-PROC-01"
VM_USERNAME="kaurauser"  # Nome de usuário para SSH
VM_PASSWORD="SuaSenhaForteAqui123!" # *** SUBSTITUA PELA SUA SENHA FORTE ***

# 2. CRIA A REDE VIRTUAL (VNet) e Sub-rede
echo "Criando Rede Virtual..."
az network vnet create \
    --resource-group $RESOURCE_GROUP_NAME \
    --name VNET-KAURA \
    --address-prefix 10.0.0.0/16 \
    --subnet-name Subnet-VM \
    --subnet-prefix 10.0.0.0/24

# 3. CRIA O GRUPO DE SEGURANÇA DE REDE (NSG) e abre a porta 22 (SSH)
echo "Criando Grupo de Segurança de Rede (NSG)..."
az network nsg create \
    --resource-group $RESOURCE_GROUP_NAME \
    --name NSG-KAURA-SSH

# Cria a regra para permitir acesso SSH
az network nsg rule create \
    --resource-group $RESOURCE_GROUP_NAME \
    --nsg-name NSG-KAURA-SSH \
    --name Allow-SSH \
    --protocol tcp \
    --direction Inbound \
    --priority 100 \
    --source-address-prefix Internet \
    --source-port-range "*" \
    --destination-address-prefix "*" \
    --destination-port-range 22

# 4. CRIA A MÁQUINA VIRTUAL (VM) - INÍCIO DA COBRANÇA
echo "Criando a VM (Ubuntu Server B2s) - CUSTO INICIADO..."
az vm create \
    --resource-group $RESOURCE_GROUP_NAME \
    --name $VM_NAME \
    --image UbuntuLTS \
    --size Standard_B2s \
    --admin-username $VM_USERNAME \
    --admin-password $VM_PASSWORD \
    --vnet VNET-KAURA \
    --subnet Subnet-VM \
    --nsg NSG-KAURA-SSH \
    --public-ip-sku Standard \
    --location $LOCATION

# 5. EXIBE O ENDEREÇO IP PÚBLICO (Para conexão via SSH)
echo "VM Criada! Obtendo o IP Público (Para SSH):"
az vm show -d --resource-group $RESOURCE_GROUP_NAME --name $VM_NAME --query publicIps -o tsv
```

### 2.2. Configuração de Segurança: Criando o `.gitignore`

**⚠️ CRUCIAL: SEGURANÇA**

Para evitar que chaves secretas do Azure, Tokens ou variáveis de ambiente sejam acidentalmente enviados ao GitHub, você deve criar um arquivo de exclusão.

**Ação:** Crie o arquivo **`.gitignore`** na **raiz** do seu repositório com o seguinte conteúdo:

Conteúdo do .gitignore:

```bash
# Configurações Essenciais de Segurança e Ambiente

# Variáveis de Ambiente e Chaves (Crucial para Azure Secrets!)
.env
.local
*.json.local

# Ambientes Python e Cache
__pycache__/
*.pyc
venv/
.pytest_cache/

# Arquivos de Sistema Ocultos
.DS_Store

# Saídas do Projeto (O GitHub Actions pode gerar)
output/
dados/

```

### 2.3. Criação dos Arquivos de Código e Automação (CI/CD)

**Contexto:** Estes arquivos devem ser criados na sua VM (acessada via SSH) para que você possa enviá-los ao GitHub. Utilize o editor de texto `nano` para criar/editar os arquivos. Este script é o coração do projeto. Ele se conecta ao Azure Document Intelligence, processa o documento de teste (`assets/lista-material-escolar.jpeg`) e imprime os resultados.

#### 2.3.1. Script Python (`src/analyze_doc_ai.py`)

Este script é o coração do projeto. Ele se conecta ao Azure Document Intelligence, processa o documento de teste, e imprime os resultados.

**Ação:** 1. Crie a pasta `src/`: `mkdir src`
2. Crie e edite o arquivo Python: `nano src/analyze_doc_ai.py`
3. Cole o código e salve (CTRL+X, S, ENTER).

> 💡 **Nota:** O código abaixo é um exemplo de *estrutura* para documentação. O código **final e funcional** que está no repositório é mais robusto: ele contém a lógica **unificada** para analisar tanto o `prebuilt-layout` quanto o `prebuilt-invoice` e salva dois arquivos diferentes (`.txt` e `.json`) como Artefatos.

```python
# CÓDIGO DO ANALYZE_DOC_AI.PY

import os
import argparse
import json
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env (útil para desenvolvimento local,
# mas no GitHub Actions, os secrets AZURE_* são usados diretamente)
load_dotenv()

# --- Configurações de Ambiente ---
endpoint = os.environ.get("AZURE_FORM_RECOGNIZER_ENDPOINT")
key = os.environ.get("AZURE_FORM_RECOGNIZER_KEY")
VM_IP = os.environ.get("VM_IP_PUBLICO", "SUA_VM_IP_AQUI")

# Define as configurações de caminho e extração para cada modelo
# --- Mapeamento de Campos e Configuração de Modelos ---
MODEL_CONFIG = {
    "prebuilt-layout": {
        "description": "Extração de Layout e Texto Puro.",
        "path": "dados/documento-teste.jpeg", 
        "extract_fields": False,
        "output_file": "dados_layout_extraidos.txt" 
    },
    "prebuilt-invoice": {
        "description": "Extração de Campos de Fatura.",
        "path": "dados/fatura-teste.pdf",
        "extract_fields": {
            "InvoiceId": "ID da Fatura",
            "CustomerName": "Nome do Cliente",
            "InvoiceTotal": "Total da Fatura"
        },
        "output_file": "dados_fatura_extraidos.json"
    }
}

def analyze_document(model_id, document_path):
    """
    Função unificada para análise de documentos com base no model_id.
    """
    if not endpoint or not key:
        print("ERRO: O ENDPOINT ou KEY não foi encontrado nas variáveis de ambiente.")
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

    # Verifica a existência do arquivo no workspace do GitHub Actions
    if not os.path.exists(document_path):
        print(f"ERRO: Arquivo de documento não encontrado no caminho: {document_path}")
        print("\n*** AÇÃO NECESSÁRIA ***")
        print(f"Confirme se o arquivo de teste ({document_path}) foi comitado para a pasta 'dados/' do repositório.")
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
        
        # ------------------------------------------------------------------
        # 3. Lógica de Extração e Output (Modelos Estruturados: Projeto 2 - Faturas)
        # ------------------------------------------------------------------
        if config['extract_fields']:
            dados_extraidos = {}
            
            if result.documents:
                doc = result.documents[0]
                
                for campo_nome, campo_descricao in config['extract_fields'].items():
                    campo = doc.fields.get(campo_nome)
                    
                    valor = None
                    confianca = "N/A"
                    
                    if campo and campo.value is not None:
                        confianca = f"{campo.confidence:.2f}"
                        
                        # Correção para o erro 'value_currency' (Projeto 2)
                        if campo_nome == "InvoiceTotal" and hasattr(campo, 'value_currency') and campo.value_currency:
                            valor_currency = campo.value_currency
                            valor = f"{valor_currency.amount} {valor_currency.currency_code or valor_currency.currency_symbol}"
                        else:
                            valor = str(campo.value)
                        
                        dados_extraidos[campo_nome] = {
                            "Valor": valor,
                            "Confianca": float(confianca) 
                        }
                        
                        print(f"**{campo_descricao}** ({campo_nome}): {valor or 'Não Encontrado'} (Confiança: {confianca})")

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
            # 1. Coleta e Imprime o Texto
            for page in result.pages:
                for line in page.lines:
                    output_text += line.content + "\n" # Acumula o texto
                    print(line.content) # Imprime no log
            
            # 2. Salvar em TXT (para Artefato do Projeto 1)
            if config['output_file']:
                with open(config['output_file'], "w", encoding="utf-8") as f:
                    # Salva a string completa no arquivo TXT
                    f.write(output_text) 
                print(f"\n✅ Resultado do layout salvo para Artefato: {config['output_file']}")
        
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

# FIM DO CÓDIGO PYTHON
```
#### 2.3.2. Arquivo de Workflow (.github/workflows/main.yml)

Este arquivo define o pipeline que o GitHub Actions executará a cada `git push`, executando os dois projetos de forma **independente** para isolamento de testes e geração de dois Artefatos.

**Ação:** 1. Crie a pasta do workflow: `mkdir -p .github/workflows` 
2. Crie e edite o arquivo YAML: `nano .github/workflows/main.yml` 
3. Cole o código abaixo e salve (CTRL+X, S, ENTER).

```yaml
name: Document AI Execution - CI

on:
  push:
    branches:
      - main

jobs:
  # --- JOB 1: PROJETO 2 - ANÁLISE DE FATURAS (JSON) ---
  analyze-fatura:
    name: Projeto 2 - Analisar Faturas
    runs-on: ubuntu-latest
    env:
      AZURE_FORM_RECOGNIZER_ENDPOINT: ${{ secrets.AZURE_FORM_RECOGNIZER_ENDPOINT }}
      AZURE_FORM_RECOGNIZER_KEY: ${{ secrets.AZURE_FORM_RECOGNIZER_KEY }}
    steps:
      - name: 1. Checkout code
        uses: actions/checkout@v4
      - name: 2. Set up Python and install dependencies
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      - name: 3. Run pip install -r requirements.txt
        run: pip install -r requirements.txt
          
      - name: 4. Execute Fatura Analysis Script
        run: python3 src/analyze_doc_ai.py --model-id prebuilt-invoice
    
      # Upload do Artefato JSON
      - name: 5. Upload Output Artifact (JSON) 📦
        uses: actions/upload-artifact@v4
        with:
          name: kaura-proj2-fatura-output-${{ github.run_id }}
          path: dados_fatura_extraidos.json
          
  # --- JOB 2: PROJETO 1 - ANÁLISE DE LAYOUT (TXT) ---
  analyze-layout:
    name: Projeto 1 - Analisar Layout/OCR
    runs-on: ubuntu-latest
    env:
      AZURE_FORM_RECOGNIZER_ENDPOINT: ${{ secrets.AZURE_FORM_RECOGNIZER_ENDPOINT }}
      AZURE_FORM_RECOGNIZER_KEY: ${{ secrets.AZURE_FORM_RECOGNIZER_KEY }}
    steps:
      - name: 1. Checkout code
        uses: actions/checkout@v4
      - name: 2. Set up Python and install dependencies
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      - name: 3. Run pip install -r requirements.txt
        run: pip install -r requirements.txt
          
      - name: 4. Execute Layout Analysis Script
        run: python3 src/analyze_doc_ai.py --model-id prebuilt-layout
        
      # Upload do Artefato TXT
      - name: 5. Upload Output Artifact (TXT) 📦
        uses: actions/upload-artifact@v4
        with:
          name: kaura-proj1-layout-output-${{ github.run_id }}
          path: dados_layout_extraidos.txt
   
   ``` 

### 2.4. Envio do Código e Início do Pipeline (Git Push)

Agora que todos os arquivos necessários (código em `src/`, workflow em `.github/`, dependências em `requirements.txt`, e o arquivo de segurança `.gitignore`) estão prontos, o último passo é enviá-los ao GitHub para disparar o pipeline de CI/CD.

Para enviar seu código da VM para o GitHub e disparar o pipeline de CI/CD, você precisa se autenticar e configurar quem está fazendo o commit.

**⚠️ Autenticação (SENHA):** A senha usada no `git push` não é sua senha do GitHub, mas sim o seu **Personal Access Token (PAT)**.

> **💡 Como Obter/Gerar o PAT:** Se você não souber como gerar ou configurar seu PAT, consulte a seção **FASE 4: Troubleshooting**, item 2 (**"Erro de Permissão do GitHub"**) para o passo a passo completo. Lembre-se de dar a permissão (`scope`) de **`workflow`** ao seu token.

1.  **Configurar Identidade Global (Uma Vez por VM):**

    ```bash
    # Substitua pelas suas credenciais do GitHub
    git config --global user.email "SEU_EMAIL_GITHUB"
    git config --global user.name "SEU_USUARIO_GITHUB"
    ```

2.  **Enviar para o GitHub (Dispara o CI/CD!):**

    ```bash
    # -- 1. Adicionar todos os arquivos ao rastreamento do Git --
    git add .

    # -- 2. Criar o commit de finalização do ambiente --
    git commit -m "feat: Adicionado pipeline CI/CD, script Python e documentacao final."

    # -- 3. Enviar. Use o PAT como a senha quando solicitado --
    git push origin main 
    ```
Em Resumo:

| Ação | Contexto de Execução | Documentação no SETUP.md |
| :--- | :--- | :--- |
| **Criação/Edição de Arquivos** | Dentro da VM (`nano`) | Instrução `nano` adicionada na FASE 2.3. |
| **`git clone`** | Dentro da VM (via SSH) | Instrução de `git clone` na FASE 2.1. |
| **`git push`** | Dentro da VM (via SSH) | Instrução de `git push` na FASE 2.4. |
| **Repositório** | Criado previamente no GitHub Web | Subentendido pelo `git clone` e `git push`. |

---
## 4. ⚙️ Projeto KAURA-DOC-AI-CUSTOM (Modelo Customizado)

Este projeto foca no treinamento de um modelo customizado para extrair dados de documentos não-padrão específicos do negócio (ex: formulário X, contrato Y).

### 4.1. 💾 Configuração do Azure Storage para Treinamento

O modelo customizado requer dados de treinamento armazenados em um contêiner específico no Azure Blob Storage.

| Recurso | Tipo | Descrição |
| :--- | :--- | :--- |
| **Conta de Storage** | Blob Storage (v2) | A mesma conta de Storage utilizada para entrada/saída de documentos (FinOps: Custo Zero). |
| **Contêiner** | `kaura-training-data` | Contêiner dedicado para armazenar os documentos de treinamento rotulados. |
| **Conteúdo** | `*.pdf`, `*.jpg`, `*.png` + arquivos `.json` de rótulo | Mínimo de **5 documentos** rotulados por tipo de documento customizado. |

### 4.2. 🤖 Processo de Treinamento no Document Intelligence Studio

O treinamento é realizado manualmente no Azure AI Document Intelligence Studio.

1.  **Acessar o Studio:** Navegar para o [Azure AI Document Intelligence Studio](https://formrecognizer.appliedai.azure.com/studio).
2.  **Criar Projeto:**
    * Selecionar **Modelos customizados** > **Criar um projeto**.
    * Ligar o projeto ao Recurso do Document Intelligence e ao Contêiner (`kaura-training-data`).
3.  **Rotulagem:** Fazer ou revisar a rotulagem dos campos no conjunto de documentos.
4.  **Treinamento:** Clicar em **Treinar**.
    * **Definir `Model ID` (Crucial):** O ID deve seguir o padrão `kaura-custom-seunome-vN` (ex: `kaura-custom-contrato-v1`).
    * **Modo de Treinamento:** Usar **Template** (para <10 docs e consistentes) ou **Neural** (para >10 docs e variados).
    * **Saída:** O `Model ID` treinado deve ser registrado no **Key Vault** como segredo para uso pelo pipeline de CI/CD.

### 4.3. 🔐 Regras de Permissão de Acesso (RBAC)

Para que o Recurso do Document Intelligence possa **ler** os documentos do Storage para o treinamento, é necessária uma atribuição de função (Role-Based Access Control - RBAC).

| Principal (Quem precisa da permissão) | Escopo (Onde a permissão se aplica) | Função (Qual permissão é concedida) | Descrição |
| :--- | :--- | :--- | :--- |
| **Identidade Gerenciada do Recurso Document Intelligence** | Conta de Azure Storage | **Blob Storage Data Reader** | Permite que o serviço leia os blobs (documentos e rótulos) necessários para o treinamento. |
| **Usuário/ML Engineer (Para rotulagem e treinamento manual)** | Conta de Azure Storage | **Storage Blob Data Contributor** | Permite o upload/download de documentos de treinamento e arquivos de rótulo (`.json`). |

**Passos para Configurar:**
1.  Vá para a Conta de Storage.
2.  Acesse **Controle de Acesso (IAM)**.
3.  Clique em **Adicionar** > **Adicionar atribuição de função**.
4.  Selecione a função **Blob Storage Data Reader**.
5.  Em **Membros**, selecione **Identidade gerenciada** e escolha o Recurso de Document Intelligence.

**Nota FinOps (Custo Zero):** A permissão é temporária para o treinamento, mas a Identidade Gerenciada é a forma mais segura e recomendada de acesso.

🏗️ SETUP.md: Provisionamento de Infraestrutura (FinOps e MLOps)
Este guia detalha os passos para provisionar a infraestrutura e configurar as permissões, garantindo o mínimo custo (FinOps) e a rastreabilidade (MLOps).

📝 Pré-requisito
Assuma que o Resource Group (RG-KAURA-DOC-AI) e o recurso de Document Intelligence (kaura-doc-ai-service-05) já estão criados.

Passo 1: Ativação da Identidade Gerenciada (Passo OBRIGATÓRIO)
A identidade gerenciada deve ser ativada antes de configurar o RBAC.

Navegue para o seu recurso de Document Intelligence: kaura-doc-ai-service-05.

No menu lateral, clique em Identity.

Na aba System assigned, mude o status para On (Ligado) e clique em Save.

Passo 2: Criação da Conta de Storage e Contêiner (FinOps)
Devido ao erro persistente SubscriptionNotFound no Azure CLI, este passo será executado via Portal Azure.

Crie a Conta de Storage kauradocaitrg002 no Portal Azure.

Project details: Use o Resource Group RG-KAURA-DOC-AI.

Instance details:

Storage account name: kauradocaitrg002.

Region: South America - Brazil South.

Redundancy (FinOps): Configure a Redundancy como Locally-redundant storage (LRS).

Após a criação, navegue até a Conta de Storage kauradocaitrg002 e vá para Containers.

Crie o contêiner de treinamento: kaura-training-data (Nível de acesso Private).

Passo 3: Atribuição de Permissões RBAC (IAM)
Este passo concede permissão de leitura ao Document Intelligence para acessar os documentos.

Navegue para a Conta de Storage kauradocaitrg002.

Vá para Access control (IAM) e clique em + Add role assignment.

Role (Função): Selecione Storage Blob Data Reader.

Member (Membro):

Selecione Managed identity.

Pesquise e selecione o recurso kaura-doc-ai-service-05 (Document Intelligence).

Finalize a atribuição em Review + assign.

💾 Passo 4: Upload dos Dados de Treinamento
Com a infraestrutura pronta, carregue os 9 documentos PDF para o contêiner.

Navegue para a Conta de Storage kauradocaitrg002 > Containers.

Clique no contêiner kaura-training-data.

Utilize o botão Upload para carregar os seus 9 documentos PDF (incluindo o documento de teste de robustez com a simulação de mancha de café).

A infraestrutura está completa.

## Após o Treino e Teste no Document Intelligence Studio vamos integrar a chamada para uma API

A adaptação é mínima. O principal a ser feito é:

1. Adicionar o modelo kaura-custom-viagem-v4 ao dicionário MODEL_CONFIG.
2. Incluir a lógica de extração para os 6 campos dentro da função analyze_document.
3. Configurar o GitHub Actions

---

## Código Python Adaptado (`analyze_doc_ai.py`)

Abaixo está o código atualizado. Substitua todo o seu dicionário `MODEL_CONFIG` e a lógica de extração de campos dentro da função `analyze_document`.

### 1. Modificação do `MODEL_CONFIG`
Adicione a configuração do seu modelo personalizado `kaura-custom-viagem-v4` ao dicionário `MODEL_CONFIG`, juntamente com os 6 campos que você treinou:

Python
```Python
# .... (Inicio do Codigo) ...
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
# ... (resto do código) ...

```

**Ação:** Lembre-se de colocar um documento de teste de viagem (por exemplo, o `KAURA_03.pdf`) na sua pasta `dados/` e renomeá-lo para `documento_viagem_teste.pdf` ou ajustar o campo `path`no `MODEL_CONFIG`.

### 2. Modificação da Lógica de Extração
Substitua o trecho `... (Lógica de loop e extração dos campos Try ... Except) ...` dentro da função `analyze_document` 

Python
```Python
 try:
    # 2. Executa a análise (Abre o arquivo e inicia o poller)
        with open(document_path, "rb") as f:
            poller = document_analysis_client.begin_analyze_document(
                model_id, document=f.read()
            )
            result = poller.result() # Esta linha pode gerar exceções de rede/API
            
        print(f"\n--- Resultado da Análise ({config['description']}) ---")

        # ------------------------------------------------------------------
        # 3. Lógica de Extração e Output (UNIFICADA)
        # ------------------------------------------------------------------

        # Se for um modelo que extrai campos estruturados (Viagem ou Fatura)
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
                            
                        
                        # Adiciona ao dicionário de saída (dentro do IF)
                        dados_extraidos[field_name] = {
                            "valor": valor,
                            "confianca": round(confianca, 2)
                        }
                        
                        # Imprime no console para debug
                        print(f"  {friendly_name}: {valor} (Confiança: {round(confianca, 2)})")
                            
                    else: # Este else está AGORA na indentação correta, correspondendo ao 'if field:'
                        print(f"  {friendly_name}: (Não encontrado)")
                        dados_extraidos[field_name] = {"valor": None, "confianca": "0.00"} # Adiciona ao dicionário mesmo que não encontrado

                # --- 4. Salvar em JSON (para Artefato) ---
                if config['output_file']:
                    # Cria a pasta 'outputs/' se não existir (garantindo que o salvamento funcione)
                    os.makedirs('outputs/', exist_ok=True)
                    with open(config['output_file'], "w", encoding="utf-8") as f:
                        json.dump(dados_extraidos, f, indent=4, ensure_ascii=False)
                    print(f"\n✅ Resultado da extração salvo para Artefato: {config['output_file']}")
                    
            else:
                print(f"Nenhum documento do tipo '{model_id}' detectado no arquivo.")
                
        # Se for um modelo de Layout/OCR (TXT)
        else: # Este else está no mesmo nível do 'if config['extract_fields']:' inicial
            output_text = ""
            
            # --- Lógica de loop e extração de texto (Layout) ---
            if result.pages:
                for page in result.pages:
                    if page.lines:
                        # Extrai o texto de cada linha e adiciona quebra de linha
                        output_text += "\n".join([line.content for line in page.lines]) + "\n"
            
            print("Conteúdo de texto extraído com sucesso.")

            # --- 4. Salvar em TXT (para Artefato) ---
            if config['output_file']:
                os.makedirs('outputs/', exist_ok=True)
                with open(config['output_file'], "w", encoding="utf-8") as f:
                    f.write(output_text)  
                print(f"\n✅ Resultado do layout salvo para Artefato: {config['output_file']}")
                
        print("---------------------------------------")
       
    except Exception as e:
        print(f"\nERRO DURANTE A ANÁLISE DO DOCUMENTO: {e}")

# ... (fim da função analyze_document) ...

```

## 3. Como Configurar o GitHub Actions
Para que o GitHub Actions consiga rodar o script e acessar o Key Vault, você precisa garantir que a **Identidade do GitHub** (o Service Principal) tenha permissão de **leitura (Get Secret)** no seu Key Vault.

O próximo passo seria:

1. **Criar/Verificar o Service Principal:** Garanta que o seu Service Principal (o "usuário" do Azure para o GitHub) está criado e sincronizado.
2. **Atribuir Permissão no Key Vault:** Ir no seu Key Vault (`kvkauradocaisecprod002`) e adicionar a permissão "Get" (Obter) de Secrets para o Service Principal.
3. **Configurar o Workflow:** Ajustar o arquivo `.yml `do GitHub Actions para incluir o passo que executa o python `analyze_doc_ai.py --model-id kaura-custom-viagem-v4`.

**🚀 Fluxo de Ação: Do Código ao GitHub Actions**
Para que seu script `analyze_doc_ai.py` funcione no GitHub Actions, a principal barreira é a autenticação para acessar o Key Vault (`kvkauradocaisecprod002.vault.azure.net`).

O fluxo ideal é:

1. Otimização do Setup de Segurança (Melhor Prática): Configurar o GitHub para usar a Workload Identity Federation para se conectar ao Azure. Isso elimina a necessidade de armazenar um segredo de Longa Duração (Service Principal Key) no GitHub, usando identidades de curta duração baseadas em certificados OpenID Connect (OIDC).
2. Permissão no Key Vault: Dar ao "usuário" do GitHub (a Workload Identity) permissão para ler (Get) o segredo `document-intelligence-key`.
3. Execução do Workflow: Adicionar o passo no arquivo `.yml` que executa o `python analyze_doc_ai.py --model-id kaura-custom-viagem-v4`.

### Configurar a Identidade OIDC
Para manter a segurança e a automação, vamos configurar a conexão segura via OIDC.

Você precisa de dois comandos principais no Azure CLI para criar a identidade que o GitHub vai usar. **Você consegue rodar estes comandos no seu terminal, autenticado via** `az login`?

**1. Atribuição da Função de Acesso**
Vamos dar permissão de leitor e de acesso ao Key Vault para a sua identidade de pipeline (substitua a `{resource-group-name} `pelo nome do seu grupo de recursos, onde o Key Vault e o Document Intelligence estão):

Bash
```Bash
# Se o seu Service Principal já existe, você pode pular este comando
# Se não, substitua {resource-group-name} pelo nome correto
az role assignment create --role "Reader" --assignee <CLIENT_ID_DO_SERVICE_PRINCIPAL> --scope /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/{resource-group-name}

# Dê permissão de acesso ao Key Vault (GET Secrets) para o Service Principal
# Substitua o nome do Key Vault e o ID do Service Principal
az keyvault set-policy --name kvkauradocaisecprod002 --secret-permissions get --spn <CLIENT_ID_DO_SERVICE_PRINCIPAL>
```

## 3. FASE 3: DESPROVISIONAMENTO E ESTRATÉGIA FINOPS (CUSTO ZERO ESTRUTURAL)

Esta é a estratégia de **FinOps** que garante o custo zero para o projeto. Ela elimina os únicos recursos que geram cobrança persistente (VM, Disco de S.O. e IP Público Standard), mantendo o serviço de **Document Intelligence F0 (GRÁTIS)** para futuros testes.

* **Recursos Mantidos (Custo Zero):** Document Intelligence F0, VNet, NSG.
* **Recursos Excluídos (Custo Eliminado):** Máquina Virtual (VM), Disco do S.O. e IP Público Standard.

### 3.1. Ação de Custo Zero (Método Recomendado: Portal do Azure)

Devido à inconsistência do Azure CLI em excluir recursos de armazenamento e rede, o método mais seguro para garantir o Custo Zero é a exclusão manual via Portal:

1.  **Excluir a VM:** Navegue até **Virtual Machines** e delete `KAURA-VM-PROC-01`. (Se ela já estiver como `Stopped (deallocated)`, a cobrança de computação já parou).
2.  **Excluir o IP Público:** Navegue até **Public IP addresses** e delete o recurso `KAURA-VM-PROC-01PublicIp`. (Este é o último custo de rede).
3.  **Excluir o Disco:** Navegue até **Disks** e delete o disco de S.O. (`KAURA-VM-PROC-01_OsDisk_1_...`) se ele não tiver sido excluído automaticamente. (Este é o último custo de armazenamento).

> ℹ️ **DICA:** Você pode verificar a lista final de recursos no Resource Group `RG-KAURA-DOC-AI` para garantir que apenas os itens de Custo Zero (Document Intelligence, VNet, NSG) permaneçam.

> 💡 **Nota Arquitetural (SSH e Custo Zero):** O SSH e o IP Público **foram eliminados** porque a execução do código foi migrada para o **GitHub Actions (CI/CD)**. O CI/CD usa **runners efêmeros** (máquinas virtuais temporárias gerenciadas pelo GitHub), que eliminam a necessidade de manter e pagar por uma VM persistente (IaaS), garantindo o **Custo Zero Estrutural** e a automação do pipeline.

### 3.2. Acesso às Credenciais (Para Próximos Testes)

Se você precisar do Endpoint ou das Keys para reconfigurar um teste futuro (local ou no CI/CD):

1.  Navegue até o Resource Group `RG-KAURA-DOC-AI` no Portal do Azure.
2.  Clique no serviço **Document Intelligence** (o nome atualizado é `kaura-doc-ai-service-05`).
3.  As credenciais estarão na seção **Keys and Endpoint**.

### 3.3. Opção: Limpeza Total (Excluir Resource Group)

Para zerar *absolutamente* o custo e deletar **TODOS** os recursos, execute este comando no Azure CLI. Ele excluirá o Document Intelligence F0 e todos os demais recursos:

```bash
echo "Excluindo o Resource Group e TODOS os recursos dentro dele."
# Usamos o nome fixo para máxima robustez
az group delete --name RG-KAURA-DOC-AI --yes --no-wait
```

## ⚠️ Solução de Problemas Comuns (Troubleshooting):


### 1. Erro de Credencial do Azure (401 - Unauthorized / ResourceNotFound)
#### Problema

Ao tentar executar o script, o Azure retorna um erro como `401 Unauthorized` ou `ResourceNotFound` (Recurso Não Encontrado). Isso pode ocorrer mesmo após criar o serviço Document Intelligence.

#### Causa
O serviço Doc AI (principalmente no Tier F0) pode não liberar imediatamente o nome de recurso após a exclusão, ou as credenciais antigas são rejeitadas.

#### Solução
1.  **Crie um novo serviço de Document Intelligence no Azure** (com um nome ligeiramente diferente, para evitar conflito).
2.  **Obtenha o novo ENDPOINT e KEY** (seção 1.2 do SETUP).
3.  **Atualize as credenciais nas Secrets do GitHub** (`AZURE_FORM_RECOGNIZER_ENDPOINT` e `AZURE_FORM_RECOGNIZER_KEY`) e no arquivo `.env` (se estiver testando localmente).

---
### 2. Erro de Permissão do GitHub (Remote Rejected)
#### Problema
Ao tentar enviar o arquivo de workflow (`.github/workflows/main.yml`) para o GitHub, você pode receber um erro: `refusing to allow a Personal Access Token to create or update workflow... without 'workflow' scope`.

#### Causa
O Personal Access Token (PAT) usado como "senha" para o comando `git push` não possui a permissão especial (`scope`) de **`workflow`**. Essa permissão é necessária para modificar arquivos dentro da pasta `.github/workflows/`.

#### Solução
1.  Acesse as configurações do seu PAT no GitHub (Settings -> Developer Settings -> Personal Access Tokens).
2.  Clique no token que você está usando (ou gere um novo se preferir).
3.  Na seção **Scopes (Permissões)**, certifique-se de que a caixa **`workflow`** esteja marcada, **além** da permissão `repo` que já deve estar selecionada.
4.  Clique em **Update Token** (Atualizar Token).
5.  Execute o comando `git push origin main` novamente, usando o Token atualizado como senha.

---

### 3. Erro de Dependência no CI/CD (`requirements.txt` não encontrado)

#### Problema
O GitHub Actions falha na etapa `Install dependencies` com o erro: `ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'`.

#### Causa
O *workflow* do GitHub Actions espera o arquivo `requirements.txt` na raiz do projeto para saber quais bibliotecas instalar (`azure-ai-formrecognizer`, `python-dotenv`).

#### Solução
1.  **Crie o arquivo `requirements.txt`** na **raiz** do projeto.
2.  **Liste as dependências** do Python, uma por linha:
    ```
    python-dotenv
    azure-ai-formrecognizer
    ```
3.  Comite e envie o arquivo para o GitHub. O CI/CD será acionado e encontrará as dependências.


