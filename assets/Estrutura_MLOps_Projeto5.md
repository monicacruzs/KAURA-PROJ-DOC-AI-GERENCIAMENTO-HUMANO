### ⚙️ Estrutura MLOps para Custo Zero (Recursos Efêmeros)
O objetivo é concentrar o uso dos recursos pagos (Azure Storage e, se necessário, a execução da análise) em um bloco de tempo muito pequeno e automatizado.

Abordagem utilizada: 
Essa abordagem de "Provisionar, Executar e Desprovisionar" (ou Spin-up, Run, Tear-down) é perfeitamente alinhada com a filosofia FinOps de Custo Zero e o conceito de Recursos Efêmeros.

1. Estratégia de Repositório e Código
Recomendação: Continuaremos usando o repositório existente: KAURA-PROJ-DOC-AI-GERENCIAMENTO-HUMANO

Item|Ação Sugerida|Justificativa
Repositório,Manter o existente.,"O Document Intelligence (Customizado ou Pré-Pronto) usa o mesmo Recurso de Azure e o mesmo Key Vault (Projeto 3). A mudança é no model_id, não no serviço base."
SETUP.md,Atualizar/Complementar.,"O SETUP.md é a documentação central. Deve-se adicionar uma seção específica (como a Seção 4 que propus) para o Modelo Customizado, mantendo as informações dos modelos pré-prontos."
codigo.py,Criar um novo arquivo: analyze_custom.py,"O código para análise customizada é diferente o suficiente para garantir clareza (diferentes modelos, diferentes campos de saída). Usar um novo arquivo facilita o pipeline de CI/CD para chamar especificamente o modelo customizado."

2. Fluxo de Execução Otimizado para Custo Zero
Este fluxo garante que o único recurso persistente e de custo seja o Recurso de Document Intelligence (que deve estar na Free Tier).

Etapa,Ação,Recurso Pago?,FinOps (Custo Zero)
A. Treinamento (Preparação),"Criar o projeto no Studio, rotular os 5-10 documentos e clicar em Treinar.",NÃO (O treinamento é gratuito),O model_id gerado é persistente e não tem custo de manutenção.
B. Provisionamento do Storage,Pipeline CI/CD (Job 1): Provisionar o contêiner kaura-training-data no Azure Storage e fazer o upload dos documentos e rótulos.,SIM (Storage),"O provisionamento e upload são rápidos, minimizando o tempo de existência do contêiner e o volume de dados."
C. Execução da Análise,"Pipeline CI/CD (Job 2): Executar o script analyze_custom.py contra documentos de teste, usando o model_id treinado.",SIM (Análise/Página),Deve-se usar um número muito limitado de documentos (Free Tier). O código deve fazer o log do sucesso/falha da extração e das métricas de confiança.
D. Desprovisionamento (Tear-down),Pipeline CI/CD (Job 3): Excluir o contêiner kaura-training-data do Azure Storage e/ou remover os documentos.,SIM (Storage),Crucial para o FinOps: Elimina o custo de armazenamento de forma imediata após o teste.
E. Manutenção do model_id,"O model_id treinado fica disponível no Recurso de Document Intelligence para futuras execuções, sem custo de manutenção.",NÃO,O sucesso do projeto (o modelo treinado) é o artefato persistente sem custo.

Resumo para o Portfólio KAURA

Fase/Recurso,Recurso Pago?,Custo Estimado (Portfólio),Estratégia FinOps (Custo Zero)
Treinamento do Modelo,NÃO,Zero,(Treinamento é gratuito)
Azure Storage,SIM,Centavos/mês,Manter baixo volume de dados de treinamento.
Execução da Análise,SIM,Zero (se usar Free Tier ou testes limitados),Utilizar a camada gratuita e limitar a análise a testes de validação.

Conclusão: Você pode executar o Projeto 4 com custo muito próximo de zero, desde que utilize a camada gratuita do Azure AI Document Intelligence e mantenha seu volume de dados de treinamento no Storage baixo. O único custo significativo seria o de análise em um cenário de produção com alto volume de documentos.
