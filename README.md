# KAURA-PROJ-DOC-AI-GERENCIAMENTO-HUMANO

<p align="center">
    <img width="150" src="https://github.com/monicacruzs/KAURA-Generative-AI-Portfolio/blob/main/assets/assets/Logo%20Kaura%20INPI%20Colorida.png" alt="Logotipo KAURA - AI & Data Innovation"> 
</p>

## ✨ Assistente de Gerenciamento de Documentos Centrado no Ser Humano (Doc Intelligence no Azure)

> 🧠 **Migração Estratégica para Azure: Pipeline de Processamento de Documentos, Foco em Automação e Redução da Carga Burocrática.**

Este projeto demonstra a construção de uma solução de **Processamento Inteligente de Documentos (IDP)**, migrando conceitos de OCR avançado para a plataforma Azure. O foco metodológico é o **Impacto Humano (KAURA)**: usar a IA para eliminar tarefas tediosas e liberar o tempo do colaborador para o **julgamento humano e a empatia**.

---

### 🎯 Proposta de Valor KAURA: A Essência do Projeto

O problema humano é claro: digitar dados de faturas ou contratos é tedioso e propenso a erros, desviando o foco do colaborador de tarefas mais estratégicas. A IA atua como o **"Filtro Inteligente"** que remove o ruído burocrático e repetitivo dos documentos, liberando o tempo do colaborador para tarefas que exigem **julgamento humano e empatia**.

---

## 🚀 Projetos Atuais (Modelos Unificados e CI/CD)

Todos os projetos utilizam o script principal **`analyze_doc_ai.py`** e o parâmetro `--model-id` para selecionar a funcionalidade de análise de documentos (Azure Document Intelligence). O processamento é executado em um pipeline de **Custo Zero Estrutural (FinOps)** via GitHub Actions.

| Projeto | Nome | Objetivo Principal | Modelo Azure DI | Script de Execução | Output Persistido |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Projeto 1** | DOC-AI-HUMANO | Extração de **texto bruto e layout** para validação de OCR. | `prebuilt-layout` | `--model-id prebuilt-layout` | Logs (Console) |
| **Projeto 2** | **KAURA-DOC-AI-FIN** | **Automatizar a extração de dados financeiros de Faturas (InvoiceId, Total, Cliente).** | **`prebuilt-invoice`** | **`--model-id prebuilt-invoice`** | **JSON (Artefato)** |

### ⚙️ Execução e Acesso ao Output (CI/CD)

A arquitetura de processamento de documentos é Serverless/On-Demand via **GitHub Actions**.

1.  **Gatilho:** O *workflow* é acionado por qualquer `git push` para a *branch* `main`.
2.  **Credenciais:** As chaves do Azure são injetadas com segurança via **GitHub Secrets** (`AZURE_FORM_RECOGNIZER_ENDPOINT`, `AZURE_FORM_RECOGNIZER_KEY`).
3.  **Output (Projeto 2):** O resultado em JSON da fatura é salvo como um **Artefato** na página de resumo da execução, permitindo o download direto do resultado (ex: `kaura-proj2-fatura-output-XXXXX.zip`).

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
* **`dados/`**: Contém os arquivos de teste (ex: `fatura-teste.pdf`) usados pelo pipeline de CI/CD.
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
