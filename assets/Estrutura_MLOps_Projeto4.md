⚙️ Estrutura MLOps para Custo Zero (Recursos Efêmeros)
O objetivo é concentrar o uso dos recursos pagos (Azure Storage e, se necessário, a execução da análise) em um bloco de tempo muito pequeno e automatizado.

Abordagem utilizada: Essa abordagem de "Provisionar, Executar e Desprovisionar" (ou Spin-up, Run, Tear-down) é perfeitamente alinhada com a filosofia FinOps de Custo Zero e o conceito de Recursos Efêmeros.

Estratégia de Repositório e Código Recomendação: Continuaremos usando o repositório existente: KAURA-PROJ-DOC-AI-GERENCIAMENTO-HUMANO
Item|Ação Sugerida|Justificativa Repositório,Manter o existente.,"O Document Intelligence (Customizado ou Pré-Pronto) usa o mesmo Recurso de Azure e o mesmo Key Vault (Projeto 3). A mudança é no model_id, não no serviço base." SETUP.md,Atualizar/Complementar.,"O SETUP.md é a documentação central. Deve-se adicionar uma seção específica (como a Seção 4 que propus) para o Modelo Customizado, mantendo as informações dos modelos pré-prontos." codigo.py,Criar um novo arquivo: analyze_custom.py,"O código para análise customizada é diferente o suficiente para garantir clareza (diferentes modelos, diferentes campos de saída). Usar um novo arquivo facilita o pipeline de CI/CD para chamar especificamente o modelo customizado."

Fluxo de Execução Otimizado para Custo Zero Este fluxo garante que o único recurso persistente e de custo seja o Recurso de Document Intelligence (que deve estar na Free Tier).
Etapa,Ação,Recurso Pago?,FinOps (Custo Zero) A. Treinamento (Preparação),"Criar o projeto no Studio, rotular os 5-10 documentos e clicar em Treinar.",NÃO (O treinamento é gratuito),O model_id gerado é persistente e não tem custo de manutenção. B. Provisionamento do Storage,Pipeline CI/CD (Job 1): Provisionar o contêiner kaura-training-data no Azure Storage e fazer o upload dos documentos e rótulos.,SIM (Storage),"O provisionamento e upload são rápidos, minimizando o tempo de existência do contêiner e o volume de dados." C. Execução da Análise,"Pipeline CI/CD (Job 2): Executar o script analyze_custom.py contra documentos de teste, usando o model_id treinado.",SIM (Análise/Página),Deve-se usar um número muito limitado de documentos (Free Tier). O código deve fazer o log do sucesso/falha da extração e das métricas de confiança. D. Desprovisionamento (Tear-down),Pipeline CI/CD (Job 3): Excluir o contêiner kaura-training-data do Azure Storage e/ou remover os documentos.,SIM (Storage),Crucial para o FinOps: Elimina o custo de armazenamento de forma imediata após o teste. E. Manutenção do model_id,"O model_id treinado fica disponível no Recurso de Document Intelligence para futuras execuções, sem custo de manutenção.",NÃO,O sucesso do projeto (o modelo treinado) é o artefato persistente sem custo.

Resumo para o Portfólio KAURA

Fase/Recurso,Recurso Pago?,Custo Estimado (Portfólio),Estratégia FinOps (Custo Zero) Treinamento do Modelo,NÃO,Zero,(Treinamento é gratuito) Azure Storage,SIM,Centavos/mês,Manter baixo volume de dados de treinamento. Execução da Análise,SIM,Zero (se usar Free Tier ou testes limitados),Utilizar a camada gratuita e limitar a análise a testes de validação.

Conclusão: Você pode executar o Projeto 4 com custo muito próximo de zero, desde que utilize a camada gratuita do Azure AI Document Intelligence e mantenha seu volume de dados de treinamento no Storage baixo. O único custo significativo seria o de análise em um cenário de produção com alto volume de documentos.

💰 Análise de Custos para o KAURA-DOC-AI-CUSTOM Os custos associados ao Projeto 4 (Modelo Customizado) se dividem em três áreas principais:

📂 Azure Storage (Custo Baixo) Onde é Usado: Armazenar os documentos de treinamento e os arquivos de rótulo (.json).
Tem Recurso Pago? Sim.

O Azure Storage cobra por volume de dados armazenados e por transações de leitura/escrita.

Estratégia FinOps (Custo Zero):

Para o ambiente de desenvolvimento/teste, mantenha o volume de dados de treinamento muito baixo (apenas o mínimo de 5-10 documentos).

Use a camada de armazenamento mais barata (como "Hot" ou "Cool" se for raramente acessado) ou explore a camada Standard LRS (Low-Redundancy Storage) para minimizar custos de redundância, se for aceitável para o ambiente de portfólio.

Conclusão: O custo será geralmente muito baixo (centavos por mês), mas não estritamente zero.

🧠 Treinamento do Modelo Customizado (Custos ZERO para o Treinamento) Onde é Usado: O tempo de processamento gasto pelo Azure para criar o seu model_id customizado.
Tem Recurso Pago? Não.

O Azure Document Intelligence não cobra pelo treinamento de modelos customizados. O treinamento é gratuito.

Estratégia FinOps (Custo Zero): Nenhuma ação necessária. O treinamento é uma operação gratuita.

🔎 Análise de Documentos (O Uso em Produção - Recurso Principalmente Pago) Onde é Usado: A execução do seu código Python (Seção "b") para analisar um documento usando o model_id customizado.
Tem Recurso Pago? Sim, é o principal recurso pago.

O custo é baseado na quantidade de páginas analisadas por mês, usando o modelo customizado.

O preço de análise de uma página com um modelo customizado é geralmente mais alto do que com um modelo pré-construído (como prebuilt-invoice).

Estratégia FinOps (Custo Zero):

Teste Limitado: Para manter o custo zero, limite severamente a quantidade de documentos analisados. Utilize o modelo apenas para testes pontuais e essenciais.

Camada Gratuita: O Recurso de Document Intelligence possui uma camada gratuita (Free Tier) que oferece um limite de páginas gratuitas por mês (ex: 500 páginas). Se você estiver usando a camada gratuita, e não ultrapassar o limite, este custo será Zero.

Monitoramento: Se você estiver usando a camada paga (Standard), é crucial monitorar o uso via Azure Cost Management para garantir que o consumo de páginas permaneça dentro do seu orçamento de FinOps.

Resumo para o Portfólio KAURA

-- Tabela

Fase/Recurso,Recurso Pago?,Custo Estimado (Portfólio),Estratégia FinOps (Custo Zero) Treinamento do Modelo,NÃO,Zero,(Treinamento é gratuito) Azure Storage,SIM,Centavos/mês,Manter baixo volume de dados de treinamento. Execução da Análise,SIM,Zero (se usar Free Tier ou testes limitados),Utilizar a camada gratuita e limitar a análise a testes de validação.

Conclusão: Você pode executar o Projeto 4 com custo muito próximo de zero, desde que utilize a camada gratuita do Azure AI Document Intelligence e mantenha seu volume de dados de treinamento no Storage baixo. O único custo significativo seria o de análise em um cenário de produção com alto volume de documentos.

Passo a Passo:
1. 📂 Preparação do Conjunto de Dados de Treinamento
O objetivo é garantir que você tenha a quantidade mínima necessária de documentos rotulados para iniciar o treinamento.

1.1. Coleta e Rotulagem dos Documentos
Ação: Reúna seus documentos não-padrão (mínimo de 5, idealmente 10-15 para maior precisão, especialmente se usar o modo Neural).

Formato: Salve-os em um formato aceito (ex: PDF, JPG, PNG).

Rotulagem:

Opção A (Recomendada): Faça a rotulagem diretamente no Azure AI Document Intelligence Studio. Isso garante que os campos e os arquivos de rótulo .json sejam gerados corretamente e associados aos documentos.

Opção B: Se for usar uma ferramenta externa, garanta que os arquivos .json de rótulo sejam gerados e estejam prontos para upload.

1.2. Estratégia do Recurso Persistente (Custo Zero)
Recurso: O Azure AI Document Intelligence Resource é o seu recurso persistente.

Ação: Garanta que ele esteja na camada gratuita (Free Tier) para não incorrer em custos de análise futura.

Artefato Chave: É essencial que a Identidade Gerenciada deste recurso já tenha a função Blob Storage Data Reader atribuída à sua Conta de Storage, conforme documentado no SETUP.md. Isso é o que permite o treinamento.

2. 🤖 Treinamento e Geração do model_id (Passo Sem Custo)
Com os documentos prontos, você pode realizar o treinamento.

2.1. Fluxo de Ação no Studio
Acesse o Studio: Navegue até o Azure AI Document Intelligence Studio.

Crie o Projeto:

Crie um novo projeto customizado e conecte-o à sua Conta de Storage e ao Contêiner onde os documentos de treinamento estão localizados.

Upload/Rotulagem: Se ainda não o fez, use a interface para fazer o upload e a rotulagem dos documentos. Verifique se todos os documentos estão rotulados.

Treinar:

Clique em Treinar (Train).

Defina um Model ID claro (ex: kaura-custom-seunome-v1).

Escolha o Modo de Treinamento (Template ou Neural).

Sucesso: Aguarde o treinamento ser concluído.

2.2. Ação Imediata após o Sucesso
Após o sucesso do treinamento:

1. Obtenha o Artefato: Registre o Model ID que foi gerado. Este é o seu artefato de ML mais importante.

2. Atualize o Key Vault: Armazene o Model ID no seu Key Vault (Projeto 3) como um segredo. Isso garante que o analyze_custom.py e o pipeline de CI/CD possam acessá-lo com segurança para a fase de execução.
