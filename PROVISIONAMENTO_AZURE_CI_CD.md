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

## 🔑 II. Configuração de Identidade e Permissões para CI/CD

Esta seção foca na criação da identidade (Service Principal) e nas permissões necessárias para que o GitHub Actions possa se autenticar no Azure e ler o Key Vault com segurança OIDC.

### Passo 1: Criar o Service Principal (SP)

Este comando cria a identidade (`sp-kaura-doc-ai-oidc`) que o GitHub Actions irá assumir. Ele estabelece o **Client ID** (`3351acd5-3910-4697-884c-759b1836aa8d`) que será usado no pipeline.

**Comando Azure CLI:**
```bash
# Cria o SP
az ad sp create-for-rbac \
    --name "sp-kaura-doc-ai-oidc" \
    --role "Reader" \
    --scopes /subscriptions/581e9cfb-c00e-4754-9a01-2845c83d1e4b
```
NOTA: O Client ID retornado por este comando é: 3351acd5-3910-4697-884c-759b1836aa8d

### Passo 2: Configurar a Credencial de Identidade Federada (OIDC)
Este é o passo crucial que informa ao Azure que o seu repositório GitHub tem permissão para usar o Service Principal criado no Passo 1, através do token JWT de curta duração.

**Comando Azure CLI:**
```bash
az ad app federated-credential create \
    --id 3351acd5-3910-4697-884c-759b1836aa8d \
    --name "GITHUB.OIDC.DEV" \
    --issuer "[https://token.actions.githubusercontent.com](https://token.actions.githubusercontent.com)" \
    --subject "repo:monicacruzs/KAURA-PROJ-DOC-AI-GERENCIAMENTO-HUMANO:environment:dev" \
    --audiences "api://AzureADTokenExchange"
```
### Passo 3: Definir Política de Acesso no Key Vault
Concede a permissão Get (Obter Segredo) ao Service Principal (3351acd5-3910-4697-884c-759b1836aa8d), permitindo que o pipeline leia a chave do Document Intelligence.

**Comando Azure CLI:**

```bash
# Assumindo que o Key Vault se chama 'kvkauradocaisecprod002'
az keyvault set-policy \
    --name kvkauradocaisecprod002 \
    --spn 3351acd5-3910-4697-884c-759b1836aa8d \
    --secret-permissions get
```
### ⚙️ III. Configuração do GitHub Secrets e main.yml

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

    
