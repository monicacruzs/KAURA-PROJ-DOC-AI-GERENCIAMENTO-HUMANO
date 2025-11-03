# KAURA-PROJ-DOC-AI-GERENCIAMENTO-HUMANO

<p align="center">
    <img width="150" src="https://github.com/monicacruzs/KAURA-Generative-AI-Portfolio/blob/main/assets/assets/Logo%20Kaura%20INPI%20Colorida.png" alt="Logotipo KAURA - AI & Data Innovation"> 
</p>

## ✨ Assistente de Gerenciamento de Documentos Centrado no Ser Humano (Doc Intelligence no Azure)

> 🧠 **Headline:** **Migração Estratégica para Azure: Pipeline de Processamento de Documentos, Foco em Automação e Redução da Carga Burocrática.**

Este projeto demonstra a construção de uma solução de **Processamento Inteligente de Documentos (IDP)**, migrando conceitos de OCR avançado para a plataforma Azure. O foco metodológico é o **Impacto Humano (KAURA)**: usar a IA para eliminar tarefas tediosas e liberar o tempo do colaborador para o **julgamento humano e a empatia**.

---

### 🎯 Proposta de Valor KAURA: A Essência do Projeto

O problema humano é claro: digitar dados de faturas ou contratos é tedioso e propenso a erros, desviando o foco do colaborador de tarefas mais estratégicas.

#### Metáfora Central (Vibe Writing)

A IA atua como o **"Filtro Inteligente"** que remove o ruído burocrático e repetitivo dos documentos, liberando o tempo do colaborador para tarefas que exigem **julgamento humano e empatia**. Construímos a ponte da máquina para a mente, transformando papéis em tempo livre para o que realmente importa.

---

### 🏗️ Arquitetura e Conceitos do Azure Demonstrados

O projeto é construído em uma arquitetura híbrida de IaaS (Infraestrutura como Serviço) e PaaS (Plataforma como Serviço), demonstrando proficiência em:

| Conceito | Componente no Azure | Habilidade Comprovada |
| :--- | :--- | :--- |
| **IaaS & Segurança** | Máquina Virtual (VM) e NSG (Network Security Group) | Provisionamento de ambientes seguros e gerenciamento de rede (RDP/SSH). |
| **PaaS & Automação** | Azure Document Intelligence (F0/Free Tier) | Integração de serviços cognitivos e otimização de custos em PaaS. |
| **Engenharia de Prompt** | Prompt Mestre em `prompts/` | Planejamento de infraestrutura e arquitetura de solução usando Large Language Models (LLMs). |

#### ☁️ Plano de Arquitetura Azure: Visão Geral

O plano detalhado da infraestrutura, projetado usando um LLM (Prompt Mestre), é:

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
| **Fase 1: Configuração da Nuvem** | Azure CLI: RG, Document Intelligence e VM. | 2 a 4 Horas | EM ANDAMENTO |
| **Fase 2: Desenvolvimento** | Script Python: Autenticação, API Doc-Intel, Geração de CSV. | 3 a 6 Horas | PENDENTE |
| **Fase 3: Documentação & GitHub** | Finalização do README, organização das pastas e commit final. | 2 a 4 Horas | EM ANDAMENTO |

---

### 🏗️ Estrutura do Projeto no GitHub

Este repositório segue o **Padrão KAURA Unificado** para clareza e auditoria:

* `assets/`: Artefatos visuais e de branding.
* `output/`: O produto final (CSV/JSON com dados extraídos).
* `prompts/`: O Prompt Mestre usado para planejamento e arquitetura.
* `code/`: O script Python de integração com o Azure Document Intelligence.

---

## 💻 Próximo Passo de Implementação

O **Grupo de Recursos (`RG-KAURA-DOC-AI`)** e o **Serviço de Document Intelligence (`doc-intel-kaura-proc`)** foram criados. O próximo passo é provisionar a VM e a Rede Virtual para a execução segura do script.

**[LINK para o script de criação da VM na pasta `infra/` ou `code/`]**
