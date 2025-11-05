# 🛠️ SETUP.md: Provisionamento e Desprovisionamento Azure CLI (KAURA)

Este documento detalha o passo a passo técnico para provisionar e desprovisionar os recursos do Azure necessários para o projeto **Assistente de Gerenciamento de Documentos Centrado no Ser Humano (Doc Intelligence no Azure)**, usando a linha de comando (Azure CLI).

**⚠️ ESTRATÉGIA DE CUSTO (FINOPS):**
O projeto segue uma rigorosa política de **Custo Zero**. O provisionamento é dividido em duas fases:
1.  **Fase 1 (Custo Zero - PaaS):** Criação do Grupo de Recursos e do Serviço de IA (Document Intelligence) em Tier Gratuito (F0).
2.  **Fase 2 (Custo por Hora - IaaS):** Criação da Máquina Virtual (VM) para execução do script, com a meta de execução e **desprovisionamento total em no máximo 2 horas**.

---

## 1. FASE 1: PROVISIONAMENTO (CUSTO ZERO)

Estes comandos criam o "container" do projeto e o serviço de Inteligência Artificial. Eles devem ser executados no **Azure Cloud Shell** ou em um ambiente com o Azure CLI instalado.

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
### 1.2. Obter Credenciais (Passo de Segurança)
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
3. Cole o código abaixo e salve (CTRL+X, S, ENTER).

```python
# CÓDIGO DO ANALYZE_DOC_AI.PY (Substitua pelo seu código final de análise)
# (Este bloco deve conter o código Python que usa as variáveis de ambiente)
# Exemplo básico de estrutura:

import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# 1. Variáveis de Ambiente (Configuradas no GitHub Secrets)
endpoint = os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
key = os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_KEY")
document_path = os.path.join("assets", "lista-material-escolar.jpeg")

if not endpoint or not key:
    print("ERRO: Credenciais não encontradas. Verifique o GitHub Secrets.")
    exit(1)

# 2. Conexão com o Azure
document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

# 3. Análise do Documento
print(f"Iniciando análise do documento: {document_path}")

try:
    with open(document_path, "rb") as f:
        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-document", document=f.read() # Use seu modelo customizado ou prebuilt
        )
    result = poller.result()
    
    # 4. Impressão dos Resultados
    print("--- RESULTADO DA ANÁLISE ---")
    for doc in result.documents:
        print(f"Tipo de Documento: {doc.doc_type}")
        # A lógica de extração detalhada deve ir aqui
        
except FileNotFoundError:
    print(f"ERRO: Arquivo não encontrado em {document_path}. Verifique a pasta assets.")

# FIM DO CÓDIGO PYTHON
```
#### 2.3.2. Arquivo de Workflow (.github/workflows/main.yml)

Este arquivo define o pipeline que o GitHub Actions executará a cada git push.

Ação: 
1. Crie a pasta do workflow: mkdir -p .github/workflows 
2. Crie e edite o arquivo YAML: nano .github/workflows/main.yml 
3. Cole o código abaixo e salve (CTRL+X, S, ENTER).

```bash

# CÓDIGO DO MAIN.YML (Workflow de CI/CD) :
name: Document AI Execution - CI

# Quando o workflow deve ser executado (a cada push na branch main)
on:
  push:
    branches:
      - main

# Define os trabalhos (jobs) que o workflow deve executar
jobs:
  analyze-document:
    # O ambiente onde o código será executado (ambiente Linux hospedado no GitHub)
    runs-on: ubuntu-latest

    # Variáveis de ambiente secretas (para o Azure)
    env:
      # O GitHub Actions NÃO LÊ o arquivo .env.
      # Você precisa adicionar estas variáveis nas "Secrets" do seu repositório no GitHub.
      AZURE_FORM_RECOGNIZER_ENDPOINT: ${{ secrets.AZURE_FORM_RECOGNIZER_ENDPOINT }}
      AZURE_FORM_RECOGNIZER_KEY: ${{ secrets.AZURE_FORM_RECOGNIZER_KEY }}

    # As etapas (steps) para executar o código
    steps:
      # 1. Checkout: Clona o código do seu repositório
      - name: Checkout code
        uses: actions/checkout@v4

      # 2. Configura o Python: Garante que a versão correta do Python está instalada
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      # 3. Instala as dependências: Instala os pacotes necessários (do requirements.txt)
      - name: Install dependencies
        run: |
          python3 -m pip install --upgrade pip
          pip install -r requirements.txt
          
      # 4. Executa o script principal: Roda o analyze_doc_ai.py
      - name: Execute Document Analysis Script
        run: |
          python3 src/analyze_doc_ai.py
    
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


