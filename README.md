# KAURA-PROJ-DOC-AI-GERENCIAMENTO-HUMANO

<p align="center">
    <img width="150" src="https://github.com/monicacruzs/KAURA-Generative-AI-Portfolio/blob/main/assets/assets/Logo%20Kaura%20INPI%20Colorida.png" alt="Logotipo KAURA - AI & Data Innovation"> 
</p>

## ✨ Assistente de Gerenciamento de Documentos Centrado no Ser Humano (Doc Intelligence no Azure)

> 🧠 **Headline:** **Migração Estratégica para Azure: Pipeline de Processamento de Documentos, Foco em Automação e Redução da Carga Burocrática.**

Este projeto demonstra a construção de uma solução de **Processamento Inteligente de Documentos (IDP)**, migrando conceitos de OCR avançado para a plataforma Azure. O foco metodológico é o **Impacto Humano (KAURA)**: usar a IA para eliminar tarefas tediosas e liberar o tempo do colaborador para o **julgamento humano e a empatia**.

---

### 🎯 Proposta de Valor KAURA: A Essência do Projeto

O problema humano é claro: digitar dados de faturas ou contratos é tedioso e propenso a erros, desviando o foco do colaborador de tarefas mais estratégicas. A IA atua como o **"Filtro Inteligente"** que remove o ruído burocrático e repetitivo dos documentos, liberando o tempo do colaborador para tarefas que exigem **julgamento humano e empatia**.

---
### 🛡️ Evolução Arquitetural: Migração para OIDC e Key Vault (Melhores Práticas)

<p align="center">
    <img width="150" src="https://github.com/monicacruzs/KAURA-PROJ-DOC-AI-GERENCIAMENTO-HUMANO/blob/main/assets/assets/Diagrama.png" alt="Diagrama Arquitetural"> 
</p>

A configuração do pipeline CI/CD exigiu uma migração estratégica para as melhores práticas de segurança do Azure/GitHub.

| De onde viemos | Para onde fomos | Razão |
| :--- | :--- | :--- |
| Secrets (Endpoint e Key) | Key Vault (KV) | **Segurança.** Chaves de API sensíveis foram movidas para um serviço de gerenciamento de segredos dedicado (Key Vault), que é auditável e tem controle de acesso granular. |
| Autenticação via Chave Secreta | Autenticação via OIDC (OpenID Connect) | **Melhor Prática.** OIDC usa tokens de curta duração emitidos pelo GitHub e validados pelo Azure, eliminando a necessidade de gerenciar chaves secretas para o Service Principal. |

**Impacto no Pipeline:** Essa mudança implicou na alteração da maneira de conectar:
* O pipeline (`main.yml`) precisou adicionar a etapa de **Autenticação OIDC** (`azure/login@v1`) para que o Service Principal (SP) pudesse fazer o login.
* O script Python foi ajustado para acessar o **Key Vault** para obter a chave, em vez de ler uma variável de ambiente direta do GitHub.
* O Azure exigiu a criação de **Políticas de Acesso** no Key Vault para permitir que o SP realizasse a operação `Get` (Obter Segredo).
---

## 🚀 Projetos Atuais (Modelos Unificados e CI/CD)

Todos os projetos utilizam o script principal **`analyze_doc_ai.py`** e são executados de forma independente via GitHub Actions, gerando Artefatos de saída (TXT e JSON).

### ➡️ Projeto 3: Extração Estruturada e Validação Humana (JSON)

Este projeto demonstra a extração de campos estruturados usando o modelo `prebuilt-invoice` (fatura), com foco na **validação da confiança** e na regra de negócio.

#### Resultados da Extração e Nível de Confiança

| Campo | Valor Extraído | Confiança | Observações |
| :--- | :--- | :--- | :--- |
| `InvoiceId` | `003589851` | 94% | Confiança alta, o ID da fatura foi bem reconhecido. |
| `InvoiceTotal` | `219.99` | 94% | Confiança alta, valor monetário bem reconhecido. |
| `CustomerName` | `Monica da Cruz Silva` | 53% | Confiança moderada. O modelo identificou o nome, mas a baixa confiança pode exigir uma revisão manual deste campo. |

#### 💡 Análise de Confiança Moderada (53% no Nome)

Apesar da confiança moderada, o nome extraído **"Monica da Cruz Silva"** está correto. Essa é uma informação valiosa, pois no Processamento Inteligente de Documentos (IDP) a **validação humana** é crucial.

**Por que a Confiança é Baixa?**
A confiança moderada ocorre frequentemente, mesmo que o resultado esteja correto, devido a:
* **Variância de Layout:** O nome pode estar em uma fonte não padronizada ou em uma área da fatura que o modelo pré-construído não espera com tanta certeza (por exemplo, em um cabeçalho incomum).
* **Qualidade da Imagem:** Se o documento original for de baixa resolução, escaneado ou tiver algum ruído, isso afeta o algoritmo de confiança.

**Regra de Negócio e Aprimoramento:**
O fato de o dado ter sido validado significa que pode ser usado, mas a regra de negócio do IDP sugere:
* Se o limite de confiança para processamento automático for, digamos, 70%, o campo `CustomerName` deve ser **sinalizado para revisão manual**.
* Para aprimoramento, pode-se treinar um **Modelo Personalizado** que se adapte especificamente ao layout desse fornecedor, aumentando a confiança para 90% ou mais em execuções futuras.
* 
### ➡️ Projeto 1: Extração de Layout (OCR/Texto Puro)
Focado na extração bruta de texto (OCR) e informações de layout. Este projeto gera um Artefato de saída TXT e é ideal para documentos não estruturados como listas ou notas simples.

### ➡️ Projeto 2: Extração de Campos Chave-Valor
Focado na extração de pares chave-valor para dados semi-estruturados, como notas fiscais ou recibos, usando modelos pré-construídos que mapeiam dados específicos.

### ⚙️ Execução e Acesso ao Output (CI/CD)

A arquitetura de processamento de documentos é Serverless/On-Demand via **GitHub Actions**.

1.  **Gatilho:** O *workflow* é acionado por qualquer `git push` para a *branch* `main`.
2.  **Jobs Paralelos:** Os projetos 1 e 2 são executados em *Jobs* separados no `main.yml` (`analyze-layout` e `analyze-invoice`).
3.  **Output Persistido:** O resultado de ambos os *jobs* é salvo como **Artefatos** no GitHub.
4.  **Acesso ao Artefato:** Na aba **`Actions`**, você pode baixar o **Artefato JSON** (Projeto 2) e o **Artefato TXT** (Projeto 1) na página de resumo de cada execução.

---
## 📦 Resultados da Automação (Artefatos de Saída)

Abaixo estão os outputs dos modelos, persistidos na pasta `outputs/` do repositório, garantindo que o resultado da análise dos documentos seja imediato e acessível:

| Arquivo de Saída | Projeto | Modelo Azure | Conteúdo |
| :--- | :--- | :--- | :--- |
| **`dados_fatura_extraidos.json`** | Projeto 2 | `prebuilt-invoice` | Extração estruturada de campos-chave (Total, ID, Cliente) em formato JSON. |
| **`dados_layout_extraidos.txt`** | Projeto 1 | `prebuilt-layout` | Extração de texto puro e completo do documento (`documento-teste.jpeg`). |

➡️ **Ver Resultado JSON:** [Clique aqui para ver o dados_fatura_extraidos.json](outputs/dados_fatura_extraidos.json)
➡️ **Ver Resultado TXT:** [Clique aqui para ver o dados_layout_extraidos.txt](outputs/dados_layout_extraidos.txt)

---

### 🏗️ Arquitetura e Conceitos do Azure Demonstrados

O projeto é construído em uma arquitetura híbrida de IaaS e PaaS, demonstrando proficiência em:

| Conceito | Componente no Azure | Habilidade Comprovada |
| :--- | :--- | :--- |
| **IaaS & Segurança** | Máquina Virtual (VM) e NSG (Network Security Group) | Provisionamento de ambientes seguros e gerenciamento de rede (RDP/SSH). |
| **PaaS & Automação** | Azure Document Intelligence (F0/Free Tier) | Integração de serviços cognitivos e otimização de custos em PaaS. |
| **Engenharia de Prompt** | Prompt Mestre em `prompts/` | Planejamento de infraestrutura e arquitetura de solução usando Large Language Models (LLMs). |

#### ☁️ Plano de Arquitetura Azure: Visão Geral

| Parâmetro | Configuração | Motivo Estratégico |
| :--- | :--- | :--- |
| **VM (IaaS)** | Série B2s (Burstable), SO Ubuntu, Porta 22 (SSH) | Melhor custo-benefício e eficiência para execução de scripts Python. |
| **Serviço AI (PaaS)** | Azure Document Intelligence (F0) | Serviço robusto de OCR/IDP, mantendo o custo zero em desenvolvimento. |
| **Região** | Brazil South | Baixa latência e conformidade de dados para o público-alvo brasileiro. |

---

### ⏱️ Estimativa de Tempo para o Projeto (Caminho Otimizado)

O projeto foi segmentado para garantir entregas rápidas e demonstração contínua de progresso (Agilidade):

| Fase | Foco Principal | Estimativa | Status |
| :--- | :--- | :--- | :--- |
| **Fase 1: Configuração da Nuvem** | Azure CLI: RG e Document Intelligence (PaaS F0) | 1 a 2 Horas | CONCLUÍDA |
| **Fase 2: Desenvolvimento** | VM, Script Python: Autenticação, API Doc-Intel, Geração de CSV. | 1 a 2 Horas | CONCLUÍDA |
| **Fase 3: Documentação & GitHub** | Finalização do README, organização das pastas e commit final. | 1 a 2 Horas | CONCLUÍDA |

---

### 🏗️ Estrutura do Projeto no GitHub

Este repositório segue o **Padrão KAURA Unificado** para clareza e auditoria:

* **`.gitignore`**: **CRUCIAL** para segurança. Garante que as chaves (Keys) e variáveis de ambiente nunca sejam enviadas ao GitHub.
* **`SETUP.md`**: O guia completo de provisionamento e **FinOps** (estratégia de custo).
* **`dados/`**: Contém os arquivos de teste (ex: `fatura-teste.pdf`, `documento-teste.jpeg`) usados pelo pipeline de CI/CD.
* `assets/`: Artefatos visuais e a imagem de teste usada pelo CI/CD.
* `prompts/`: O Prompt Mestre usado para planejamento e arquitetura.
* `src/`: O script Python de integração com o Azure Document Intelligence (`analyze_doc_ai.py`).
* `requirements.txt`: Lista de dependências Python para o GitHub Actions.

---

## 👩‍💻 Expert (Contato)

<p>
    <img 
      align=left 
      margin=10 
      width=80 
      src=https://avatars.githubusercontent.com/u/71937997?v=4
    />
    <p>&nbsp&nbsp&nbspMônica Cruz<br>
    &nbsp&nbsp&nbsp
    <a href=https://github.com/monicacruzs>
    GitHub</a>&nbsp;|&nbsp;
    <a href=https://www.linkedin.com/in/m%C3%B4nicacruz/?locale=pt_BR>LinkedIn</a>
&nbsp;|&nbsp;
    <a href="SEU KAURA AQUI">
    KAURA - AI & Data Innovation</a>
&nbsp;|&nbsp;</p>
</p>
<br/><br/>
<p>
