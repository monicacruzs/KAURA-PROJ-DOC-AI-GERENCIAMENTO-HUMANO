# 📄 GUIA DE PROVISIONAMENTO AZURE PARA CI/CD COM OIDC (GITHUB ACTIONS)

Este guia documenta o processo correto e otimizado para configurar a autenticação OIDC (OpenID Connect) do GitHub Actions no Azure, eliminando segredos de longa duração e garantindo o acesso ao Key Vault.

## 💰 Custo e Recursos Utilizados

Os custos de provisionamento e teste são mantidos baixos, utilizando serviços de baixo custo ou gratuitos (Free Tier).

[Recursos utilizados no Azure, incluindo Document Intelligence e Key Vault](assets/Azure_RecursosUtilizados_free.png)

| Custo | Valor (em R$) |
| :--- | :--- |
| **Current Cost (Custo Atual)** | R$1.00 |
| **Custos por Recurso (Exemplos)** | Document Intelligence (R$0.62); Key Vault (R$0.11 - Outros) |

## 📝 I. Informações Essenciais (IDs)

Estes são os IDs verificados da sua conta.

| ID | Valor Verificado | Onde Encontrar |
| :--- | :--- | :--- |
| **Tenant ID** (ID do Diretório) | `c0243fd8-d848-4840-a4f8-cdb4bd79b1cf` | Entra ID -> Overview |
| **Subscription ID** (ID da Assinatura) | `581e9cfb-c00e-4754-9a01-2845c83d1e4b` | Assinaturas -> Overview |
| **Client ID** (ID do Aplicativo SP) | `3351acd5-3910-4697-884c-759b1836aa8d` | Entra ID -> App registrations -> SP Overview |

## 🔑 II. Configuração do Service Principal (SP) e Permissões

### Passo 0: Configuração de Segurança: Azure Key Vault

Para garantir o **FinOps (Custo Zero Estrutural)** e seguir as melhores práticas de segurança, o projeto utiliza o **Azure Key Vault** para armazenar a chave de acesso do Document Intelligence, substituindo o uso direto de secrets no GitHub Actions.

#### Premissas de Segurança

1.  A aplicação utiliza o **Azure Identity SDK** e a `DefaultAzureCredential`.
2.  A identidade (Usuário/Service Principal/Managed Identity) que executa a aplicação deve ter a permissão `get` e `list` para Segredos no Key Vault.

**1. Registrar o Provedor de Recursos**

Você precisa usar o comando az provider register para ativar o Key Vault na sua assinatura.

Execute o comando abaixo no Azure CLI:

``` bash
az provider register --namespace 'Microsoft.KeyVault'
```
**2. Verifique se o registro foi concluído (deve estar em estado Registered):***

``` bash
az provider show --namespace 'Microsoft.KeyVault' --query "registrationState"
```
**3. Verifique a Assinatura Atual**

``` bash
az account show
```
**4. Liste as Assinaturas Disponíveis**
Se a assinatura exibida não for a correta, liste todas as suas assinaturas para encontrar o nome ou ID da assinatura onde o seu grupo de recursos reside:

``` bash
az account list --output table
```
**5. Selecione a Assinatura Correta** [Substitua [NOME_OU_ID_DA_ASSINATURA_CORRETA]]
Use o nome ou ID da assinatura correta (onde o RG - Resource Group está) para ativá-la no seu CLI:

``` bash
az account set --subscription "[NOME_OU_ID_DA_ASSINATURA_CORRETA]"
```
**6. Liste os Recursos da Assinatura**

``` bash
az group list --output table
```

**7. Localizar o Recurso Document Intelligence (Alternativa)**
Se você souber o nome do recurso Document Intelligence (que no seu print é kaura-doc-ai-service-05), você pode tentar encontrá-lo, o que lhe dirá o nome do grupo de recursos correto.

``` bash
# Se o nome do recurso Document Intelligence for 'kaura-doc-ai-service-05'
az resource list --resource-type Microsoft.CognitiveServices/accounts --name "kaura-doc-ai-service-05" --query "[0].resourceGroup" -o tsv
```

**8. Criação do Key Vault:**

🔑 Sugestão para KeyVaultName: `kvkauradocaisecprod002`

Explicação da Estrutura

Elemento|Significado|Seu Valor|
| :--- | :--- | :--- |
kv|Tipo de Recurso (Key Vault)|Padronização|
kauradocaisec|Carga de Trabalho/Projeto (KAURA-DOC-AI-SEC)|Contexto do Projeto|
prod|Ambiente (Produção/Principal)|Contexto de Uso|
001|Instância|Número da Instância (ajuda a garantir a unicidade) 

Regras do Azure Key Vault para Nomes

- Deve ter entre 3 e 24 caracteres.
- Pode conter apenas letras minúsculas (a-z), números (0-9) e não pode conter hifens (-).
- Deve começar com uma letra e terminar com uma letra ou um número.

Execute os comandos abaixo no Azure CLI

``` bash
az keyvault create \
  --name "kvkauradocaisecprod002" \
  --resource-group "RG-KAURA-DOC-AI" \
  --location "brazilsouth" \
  --sku "standard" \
  --enable-rbac-authorization false
```

💰 Custo do Registro vs. Custo do Recurso

- Registro (az provider register): Este comando é apenas uma ação administrativa que habilita sua assinatura a usar um tipo de serviço do Azure. Não há custo associado a habilitar ou desabilitar um provedor de recursos.

- Key Vault (o Recurso): O Azure Key Vault em si tem um custo, mas é extremamente baixo e flexível.

    - SKU Standard (que você está usando): Este SKU tem um custo por operações e transações. Se você fizer poucas chamadas por mês (o que será o caso no desenvolvimento e CI/CD), o custo será de centavos de dólar por mês.

    - A boa notícia é que você não paga pela existência do Key Vault, apenas pelas transações que ele processa.
 
🎉 O Key Vault foi criado com SUCESSO!

O JSON de retorno confirma que:

 - Key Vault Name: kvkauradocaisecprod002
 - Resource Group: RG-KAURA-DOC-AI
 - Provisioning State: "Succeeded"
 - Vault URI (URL que você usará no código Python):
   https://kvkauradocaisecprod002.vault.azure.net/
           
o GitHub Actions irá usar o OpenID Connect (OIDC), que é a forma mais segura de autenticar seu pipeline no Key Vault sem usar segredos no GitHub

🔑 Próximos Passos: Obter e Armazenar a Chave

1. Obter a Chave do Portal
    - No portal do Azure, clique no recurso kaura-doc-ai-service-05 dentro do Resource Group RG-KAURA-DOC-AI.
    - No menu de navegação à esquerda, clique em "Keys and Endpoint" (Chaves e Ponto de Extremidade).
    - Copie o valor da Key 1 (Chave 1).

2. Armazenar a Chave no Key Vault
Com a chave copiada, use o comando Azure CLI abaixo para armazená-la de forma segura no seu novo Key Vault.

    ```bash
    # Substitua [CHAVE_DOCUMENT_INTELLIGENCE_AQUI] pelo valor que você copiou.
    az keyvault secret set \
      --vault-name "kvkauradocaisecprod002" \
      --name "document-intelligence-key" \
      --value "[CHAVE_DOCUMENT_INTELLIGENCE_AQUI]"
         ```
3. Definir a Política de Acesso (Permitir acesso à sua conta)
Para que você possa testar o script Python localmente, execute novamente os comandos de política de acesso para a sua identidade:

    ```bash
    # 1. Obtém seu Object ID
    OBJECT_ID=$(az ad signed-in-user show --query id -o tsv)
    
    # 2. Define permissão 'get' e 'list' de segredos no Key Vault
    az keyvault set-policy \
      --name "kvkauradocaisecprod002" \
      --object-id "$OBJECT_ID" \
      --secret-permissions get list
    ```
Com o Key Vault provisionado, o segredo armazenado e a política de acesso definida para sua conta, a camada de segurança (Fase 1) está praticamente completa.

🚀 Próxima Fase: Segurança de Pipeline (OIDC)
Tudo no código está pronto. Agora, para atingir o objetivo de FinOps e Segurança do seu projeto, vamos configurar o OpenID Connect (OIDC) no GitHub Actions.

Este processo envolve três etapas principais:
    
- Criação do Service Principal (SP) no Azure: A identidade que o GitHub Actions irá assumir.
- Configuração da Credencial Federada: Informar ao Azure que o seu repositório GitHub tem permissão para usar esse SP.
- Atualização da Política de Acesso do Key Vault: Dar permissão de leitura de segredos para o novo SP.

Agora, vamos configurar a infraestrutura de identidade para o seu pipeline no GitHub Actions.

O objetivo é que o pipeline consiga se autenticar no Azure e ler o Key Vault sem usar segredos persistentes no GitHub, como AZURE_CLIENT_SECRET.

### Passo 1: Atribuir Função `Leitor (Reader)` na Assinatura

O SP precisa desta função para listar assinaturas e Tenants no login OIDC.

**Comando Azure CLI:**
```bash
az role assignment create \
    --role "Reader" \
    --assignee 3351acd5-3910-4697-884c-759b1836aa8d \
    --scope /subscriptions/581e9cfb-c00e-4754-9a01-2845c83d1e4b
```

### Passo 1: Obter o ID da Assinatura e do Tenant
Precisaremos do seu ID de Assinatura e ID de Tenant (Diretório) para configurar o Service Principal.

Execute os comandos abaixo no Azure CLI para obter os valores necessários:

 ```bash
# 1. Obtém o ID da Assinatura (Subscription ID)
AZURE_SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# 2. Obtém o ID do Tenant (Tenant ID)
AZURE_TENANT_ID=$(az account show --query tenantId -o tsv)

echo "ID da Assinatura (Subscription ID): $AZURE_SUBSCRIPTION_ID"
echo "ID do Tenant (Tenant ID): $AZURE_TENANT_ID"
```
Anote esses dois valores. Eles serão usados no próximo comando e no GitHub Actions.

### Passo 2: Criar o Service Principal (SP) e Credencial Federada
Este comando faz duas coisas essenciais de uma só vez, criando a nova identidade segura:

- Cria o Service Principal (SP) chamado sp-kaura-doc-ai-oidc.
- Configura uma Credencial Federada que permite que o seu repositório GitHub acesse esse SP.

Atenção: Substitua [SEU_NOME_DE_USUARIO_GITHUB] e [SEU_REPOSITORIO_GITHUB] pelos seus dados reais.

  A identidade do GitHub (SP: `sp-kaura-doc-ai-oidc`) precisa de permissões para fazer login e acessar o Key Vault.

### Passo 2: Configurar a Credencial de Identidade Federada (OIDC)
Cria a ponte de confiança, usando o ambiente dev configurado no seu YAML.

**Configurações Necessárias:**

| Campo | Valor |
| :--- | :--- |
| **Issuer (Emissor)** | `https://token.actions.githubusercontent.com` |
| **Subject Identifier** | `repo:monicacruzs/KAURA-PROJ-DOC-AI-GERENCIAMENTO-HUMANO:environment:dev` |

**Comando Azure CLI:**
```bash
az ad app federated-credential create \
    --id 3351acd5-3910-4697-884c-759b1836aa8d \
    --name "GITHUBOIDC" \
    --issuer "[https://token.actions.githubusercontent.com](https://token.actions.githubusercontent.com)" \
    --subject "repo:monicacruzs/KAURA-PROJ-DOC-AI-GERENCIAMENTO-HUMANO:environment:dev" \
    --audiences "api://AzureADTokenExchange"
```
Nota: Microsoft Entra ID ->  App Registrations ->  View all aplication in the directory (botão) > sp-kaura-doc-ai-oidc -> Certificates & Secrets: Você poderá ver a Federated Credentials

## 🔒 III. Configuração do Key Vault
### Passo 3: Definir Política de Acesso no Key Vault
Concede a permissão Get (Obter Segredo) ao SP.

**Comando Azure CLI:**

``` bash
# Assumindo que o Key Vault se chama 'kvkauradocaisecprod002'
az keyvault set-policy \
    --name kvkauradocaisecprod002 \
    --spn 3351acd5-3910-4697-884c-759b1836aa8d \
    --secret-permissions get
```
### ⚙️ IV. Configuração do GitHub Secrets e main.yml

### Passo 4: Configurar Secrets no GitHub
Localização: Settings -> Secrets and variables -> Actions.

[Configuração de Secrets no GitHub, mostrando Tenant ID e Endpoint](assets/GitHub_ActionseSecrets.png)

### Passo 5: Atualizar o .github/workflows/main.yml
O pipeline deve usar os IDs corretos e o Secret para o Tenant ID.
A estrutura final no seu main.yml é a seguinte (usando o Secret para o Tenant ID, que é a melhor prática):

```yaml
# Arquivo: .github/workflows/main.yml
# ...
jobs:
  analyze_document:
    # O ambiente deve corresponder ao Subject OIDC configurado no Azure
    environment: dev 
    # ...
    steps:
      # ...
      - name: Azure Login via OIDC
        uses: azure/login@v1
        with:
          # 1. CLIENT ID (ID do Aplicativo SP)
          client-id: 3351acd5-3910-4697-884c-759b1836aa8d
          # 2. TENANT ID (ID do Diretório - Usando Secret para segurança)
          tenant-id: ${{ secrets.AZURE_TENANT_ID }} 
          # 3. SUBSCRIPTION ID (ID da Assinatura - String literal verificada)
          subscription-id: 581e9cfb-c00e-4754-9a01-2845c83d1e4b
          
      # --- DEFINIÇÃO DO ENDPOINT E KEY VAULT URI (Variáveis de ambiente) ---
      # Acesso ao Endpoint (via Secret) e Key Vault URI (Hardcoded)
      - name: Set Environment Variables
        run: |
          # ENDPOINT (Via Secret do GitHub)
          echo "AZURE_FORM_RECOGNIZER_ENDPOINT=${{ secrets.AZURE_FORM_RECOGNIZER_ENDPOINT }}" >> $GITHUB_ENV
          # URI do Key Vault (Hardcoded, pois é público)
          echo "AZURE_KEY_VAULT_URI=https://kvkauradocaisecprod002.vault.azure.net/" >> $GITHUB_ENV
      
      # ...
```

    
