# 📄 GUIA DE PROVISIONAMENTO AZURE PARA CI/CD COM OIDC (GITHUB ACTIONS)

Este guia documenta o processo correto e otimizado para configurar a autenticação OIDC (OpenID Connect) do GitHub Actions no Azure, eliminando segredos de longa duração e garantindo o acesso ao Key Vault.

## 📝 I. Informações Essenciais (IDs)

Estes são os IDs verificados da sua conta.

| ID | Valor Verificado | Onde Encontrar |
| :--- | :--- | :--- |
| **Tenant ID** (ID do Diretório) | `c0243fd8-d848-4840-a4f8-cdb4bd79b1cf` | Entra ID -> Overview |
| **Subscription ID** (ID da Assinatura) | `581e9cfb-c00e-4754-9a01-2845c83d1e4b` | Assinaturas -> Overview |
| **Client ID** (ID do Aplicativo SP) | `3351acd5-3910-4697-884c-759b1836aa8d` | Entra ID -> App registrations -> SP Overview |

---

## 🔑 II. Configuração do Service Principal (SP) e Permissões

A identidade do GitHub (SP: `sp-kaura-doc-ai-oidc`) precisa de permissões para fazer login e acessar o Key Vault.

### Passo 1: Atribuir Função `Leitor (Reader)` na Assinatura

O SP precisa desta função para listar assinaturas e Tenants no login OIDC.

**Comando Azure CLI:**
```bash
az role assignment create \
    --role "Reader" \
    --assignee 3351acd5-3910-4697-884c-759b1836aa8d \
    --scope /subscriptions/581e9cfb-c00e-4754-9a01-2845c83d1e4b
```
Passo 2: Configurar a Credencial de Identidade Federada (OIDC)
Cria a ponte de confiança, usando o ambiente dev configurado no seu YAML.

Configurações Necessárias: | Campo | Valor | | :--- | :--- | | Issuer (Emissor) | https://token.actions.githubusercontent.com | | Subject Identifier | repo:monicacruzs/KAURA-PROJ-DOC-AI-GERENCIAMENTO-HUMANO:environment:dev |

Comando Azure CLI:
```bash
az ad app federated-credential create \
    --id 3351acd5-3910-4697-884c-759b1836aa8d \
    --name "GITHUBOIDC" \
    --issuer "[https://token.actions.githubusercontent.com](https://token.actions.githubusercontent.com)" \
    --subject "repo:monicacruzs/KAURA-PROJ-DOC-AI-GERENCIAMENTO-HUMANO:environment:dev" \
    --audiences "api://AzureADTokenExchange"
```
🔒 III. Configuração do Key Vault
Movemos a KEY do Document Intelligence para o Key Vault.

Passo 3: Definir Política de Acesso no Key Vault
Concede a permissão Get (Obter Segredo) ao SP (3351acd5-3910-4697-884c-759b1836aa8d).

Comando Azure CLI:
``` bash
# Assumindo que o Key Vault se chama 'kvkauradocaisecprod002'
az keyvault set-policy \
    --name kvkauradocaisecprod002 \
    --spn 3351acd5-3910-4697-884c-759b1836aa8d \
    --secret-permissions get
```
⚙️ IV. Alterações no main.yml
As alterações concentraram-se na seção de login e na definição das variáveis de ambiente.

1. Correção e Estrutura Final do Login OIDC
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

    
