# PRD do FruitFly

Versão 0.2, de 14 de setembro de 2026. Estado: primeira implementação experimental, com provas de viabilidade em andamento. Responsável pelo produto: Nilson.

O pedido mais recente prioriza baixo consumo em diferentes dispositivos. Para o recorte inicial, a CPU compilada passa a ser o padrão após comparação com a GPU AMD; essa decisão substitui a preferência inicial pela GPU. O estado atual e as limitações estão em [IMPLEMENTATION.md](IMPLEMENTATION.md).

## Objetivo e experiência

Criar uma mosquinha que conviva com o trabalho no desktop. Ela aparece em pixel art 2D, vista de um ângulo frontolateral, caminha e voa sobre os aplicativos, reage ao cursor e pode buscar abrigo atrás de uma janela. Um ícone na bandeja do sistema permite ligá-la e desligá-la.

O diferencial do produto é que a rede neural escolhe o comportamento. A primeira versão deve demonstrar dez respostas sensoriomotoras distinguíveis, com influência verificável dos circuitos extraídos do FlyWire nas respostas às quais eles forem associados. O corpo, a animação e a integração com o desktop executam os comandos da rede.

Este documento usa o estilo de especificação de produto, em português direto, para orientar Nilson e quem implementar o projeto. Os requisitos visuais e de interação vieram da conversa; as decisões técnicas abaixo são propostas a validar nas tarefas P0.

## Decisões e premissas

| Item | Definição | Origem |
|---|---|---|
| Aparência | Pixel art 2D, visão frontolateral da mosca. | Pedido do usuário. |
| Corpo | Corpo cinemático simplificado, representado pelo próprio sprite. | Pedido do usuário. |
| Comportamento | Todas as escolhas comportamentais devem vir da rede neural. | Preferência expressa pelo usuário, adotada como requisito. |
| Repertório | Pelo menos dez respostas distinguíveis na versão 1. | Pedido do usuário; catálogo proposto neste PRD. |
| Desktop | Sobreposição aos aplicativos com possibilidade de esconder-se atrás de janelas. | Pedido do usuário. |
| Controle | Ícone próprio no systray, com liga/desliga. | Pedido do usuário. |
| Ícone | Cabeça da mosca vista de cima como primeira proposta; corpo inteiro visto de cima é alternativa. | Escolha inicial dentro das opções do usuário. |
| Integração | Aplicativo independente com integração ao Omarchy por plugin. | Proposta para manter simulação e ciclo de vida separados do shell. |
| Processamento | Backend escolhido por custo medido; CPU compilada no protótipo e GPU opcional após demonstração de benefício. | Pedido posterior de baixo consumo e compatibilidade com outros dispositivos. |
| Ameaça inicial | Aproximação visual do cursor; CO₂ virtual fica para expansão. | Direção técnica da conversa anterior. |
| Oclusão | Esconder visualmente o sprite usando a geometria de uma janela escolhida pela rede. | Proposta sujeita à prova de viabilidade. |

## O que significa a rede decidir tudo

Sensores oferecem à rede medidas do ambiente e do corpo. A rede produz os comandos que determinam deslocamento, giro, voo, pouso, limpeza e uso de abrigos. A memória necessária para reagir ao histórico recente faz parte da dinâmica neural.

O modelo terá circuitos extraídos do FlyWire e módulos recorrentes construídos para completar as funções do desktop. Esses módulos podem ser calibrados ou treinados offline. A existência de um comportamento na versão final não prova que ele veio da mosca biológica. Cada módulo deve registrar sua origem: conectividade local, hipótese de modelagem ou parâmetros aprendidos. O estudo de modelos LIF e o trabalho FlyVis sustentam estratégias de modelagem e ajuste, sem demonstrar o produto completo proposto aqui. [S1 e S2](RESEARCH.md)

O corpo continua responsável por integrar velocidade, limitar aceleração, detectar contato e converter comandos em quadros de animação. A oclusão depende da posição do corpo e da janela. Esses mecanismos não escolhem fugir, explorar ou voltar. Liga/desliga, falhas, suspensão da sessão e remoção de um monitor são controles do aplicativo e têm precedência sobre a simulação.

Ficam vedadas decisões comportamentais externas como `se cursor perto, fugir`, `após cinco segundos, sair do abrigo` ou um sorteio externo que escolhe a próxima ação. Ruído neural com semente, adaptação e osciladores podem participar da rede. Estados de execução do corpo, como estar no ar, são permitidos; uma máquina de estados que arbitra as ações da mosca não atende ao requisito.

## Requisitos funcionais

| ID | Requisito da versão 1 | Aceite |
|---|---|---|
| F01 | Sprite frontolateral em pixel art com transparência, orientação coerente e animação de caminhada, voo, repouso e limpeza. | Movimento reconhecível nos dois sentidos, sem borrar pixels nem girar a imagem de forma que a perspectiva se desfaça. |
| F02 | Rede neural como única fonte de escolha comportamental. | Inspeção dos comandos, replay e intervenções na rede demonstram a origem das ações; sensores e renderizador não escolhem ações. |
| F03 | Dez respostas R01–R10 disponíveis na mesma versão. | Todas passam seus cenários e testes de competição, sem contar espelhamentos ou quadros de animação como respostas extras. |
| F04 | Sobreposição transparente sobre aplicativos comuns e fullscreen. | A mosca aparece onde previsto e os cliques e o foco seguem para o aplicativo abaixo. Limites entre superfícies do shell são documentados. |
| F05 | A rede pode conduzir a mosca para trás de uma janela e fazê-la reaparecer. | Há ocultação parcial na borda e total no interior do abrigo; mover, fechar ou trocar a janela de workspace não deixa pixels presos. |
| F06 | Ícone real no systray com menu de controle. | A bandeja registra o item; o estado ligado/desligado é legível, inclusive em tema claro ou escuro. |
| F07 | Ligar, desligar e encerrar são ações distintas. | Desligar remove o sprite e interrompe sensores e simulação, mantendo o tray; encerrar remove todos os processos e o item. |
| F08 | Suporte ao layout de monitores e workspaces do ambiente. | Escala fracionária, coordenadas negativas e remoção de monitor não duplicam nem perdem a mosca. |
| F09 | Execução local após instalar dependências e preparar o modelo. | O runtime usa um pacote neural compacto e não precisa abrir os CSVs ou baixar modelos durante o uso. |
| F10 | Evidência acessível sobre a participação do FlyWire. | Manifesto registra origem das conexões e parâmetros; ferramenta de inspeção mostra atividade, comandos e ablações. |
| F11 | Falhas deixam o controle disponível. | Uma falha no cérebro oculta a mosca, interrompe sua atividade e apresenta opção de religar no tray. |
| F12 | Instalação e remoção por usuário. | Integração não edita arquivos empacotados do Omarchy; autostart é opcional e os dados originais permanecem preservados. |
| F13 | Execução neural eficiente com referência CPU e opção de aceleração. | Comparar CPU/GPU antes de escolher o padrão; nenhuma GPU dedicada ou biblioteca de treinamento obrigatória para usar o pet. |
| F14 | Limitar trabalho sustentado e eliminar processamento desligado. | Sem espera ocupada ou recuperação acelerada de atraso; renderização somente quando necessária, orçamento de CPU e zero passos/consultas ao desligar. |

## Catálogo das dez respostas

“Reflexos” é tratado aqui como o pedido de um repertório observável. Exploração, descanso e retorno são comportamentos mais amplos que um reflexo biológico. A meta da versão 1 é entregar as dez respostas abaixo; a pesquisa ainda precisa determinar quais podem ter circuitos biológicos suficientemente bem fundamentados. Não há promessa de dez circuitos completos já validados.

| ID | Resposta | Estímulo ou contexto de teste | Resultado observável | Origem proposta |
|---|---|---|---|---|
| R01 | Fuga rápida orientada | Cursor em trajetória de aproximação; controles com passagem distante e afastamento. | A rede inicia uma arrancada ou decolagem e escolhe movimento que aumenta a separação. | LC4/LPLC2 e descendentes candidatos, com modelo sensorial e saída motora a calibrar. |
| R02 | Imobilização defensiva | Ameaça com corpo inicialmente lento, comparada à condição de movimento. | Redução sustentada do movimento em um contexto distinto da fuga; nova aproximação pode interromper a imobilização. | Circuito candidato envolvendo DNp09 e contexto neural; disponibilidade funcional ainda não auditada. |
| R03 | Desvio de obstáculo | Parede virtual ou limite do monitor na direção do movimento. | A rede gira antes do contato; esquerda e direita constituem uma só resposta. | Rede projetada, com investigação posterior de DNa01/DNa02. |
| R04 | Recuo por contato | Contato frontal virtual com pouco espaço para avançar. | Movimento para trás seguido de reorientação, sem correção por teletransporte. | MDN como candidato; leitura motora e feedback projetados. |
| R05 | Exploração espontânea | Ambiente tranquilo, corpo descansado e caminhos livres. | A rede inicia caminhadas e mudanças de direção sem agenda externa de ações. | Dinâmica recorrente e motivação projetadas. |
| R06 | Descanso e recuperação | Feedback de esforço acumulado sem ameaça imediata. | Atividade locomotora diminui e volta com a recuperação; aproximação urgente pode prevalecer. | Estado corporal simplificado e seleção neural projetada. |
| R07 | Pouso | Mosca em voo, baixa ameaça e superfície de pouso virtual disponível. | A rede reduz voo, desacelera e estabelece contato; o corpo executa a transição. | Rede projetada; investigar circuito de pouso antes de atribuir origem biológica. |
| R08 | Limpeza das antenas | Sinal virtual de irritação antenal em condições de baixo risco. | A rede inicia limpeza e pode interrompê-la diante de ameaça. | Circuitos de grooming como candidatos; confirmar IDs e conexões locais. |
| R09 | Busca de abrigo | Ameaça persistente com borda de janela acessível. | A rede aproxima o corpo de uma entrada e solicita abrigo; o sprite fica oculto conforme cruza a borda. | Comportamento de produto aprendido ou projetado na rede. |
| R10 | Saída do abrigo e retorno | Queda de ameaça após históricos de perseguição diferentes. | A rede faz a mosca reaparecer e retomar exploração, podendo voltar à região de trabalho com segurança. | Memória neural e motivação projetadas, sem temporizador externo de saída. |

As associações de R01, R02 e R04 são hipóteses de implementação apoiadas em literatura; uma classe celular não funciona como botão isolado de ação. Os estudos mostram participação de redes e dependência de contexto. [S3, S4 e S5](RESEARCH.md)

Cada resposta deve ter ao menos um cenário positivo, um controle negativo e um conflito com outra resposta. Os cenários R09 e R10 avaliam adaptação ao desktop. Não serão apresentados como reprodução de uma mosca escondendo-se atrás de aplicativos.

## Aparência e corpo 2D

A arte base proposta ocupa uma célula de até 32 × 32 pixels por quadro, com transparência e ampliação inteira configurável. O tamanho é uma hipótese de produção visual, a validar na tela real. A mosca mantém a vista frontolateral durante deslocamentos diagonais; quadros orientados e espelhamento tratam mudanças de sentido. Voo usa batimento de asas e elevação aparente, mantendo a leitura da perspectiva.

O corpo armazena posição, velocidade e orientação no plano. Uma variável de elevação permite distinguir caminhada e voo sem simular anatomia muscular ou uma cena 3D. A rede recebe informações de contato, esforço e movimento efetivamente realizado, fechando o ciclo entre percepção e ação.

O ZIP local contém esqueletos neuronais SWC, que servem para análise da anatomia. Os sprites e o ícone serão produzidos como arte própria e versionados separadamente. Não precisamos extrair todo o ZIP para animar o corpo.

## Sobreposição e esconderijos

Enquanto está exposta, a mosca será desenhada numa superfície transparente acima dos aplicativos. Ao escolher abrigo, ela cruza uma borda elegível de janela; o renderizador recorta a parte que deveria estar atrás dessa janela. A rede continua rodando durante a ocultação.

Essa solução simula a oclusão no próprio desenho. Ela não coloca uma janela Wayland arbitrariamente entre outras janelas. Na versão 1, janelas opacas retangulares são a referência inicial; cantos arredondados, transparências e animações do compositor precisam de teste e podem exigir aproximações declaradas. A máscara que permite atravessar cliques é independente desse recorte visual. [S7 e S8](RESEARCH.md)

A seleção neural de um abrigo usa candidatos geométricos em coordenadas locais. O aplicativo não passa o nome do programa, texto da janela ou uma instrução pronta para fugir. Fullscreen continua compatível com a mosca exposta; uma janela que cobre toda a tela pode não oferecer entrada de abrigo acessível.

“Sobre tudo” significa sobre os aplicativos do desktop, inclusive fullscreen quando o compositor permitir a superfície. O projeto não tenta desenhar sobre a tela de bloqueio. Na sessão bloqueada, o runtime pausa; ao desbloquear, retoma apenas se estava ligado. A precedência em relação a menus e outras sobreposições será fixada na prova P0.

## Bandeja e ciclo de vida

O tray permanece visível enquanto o aplicativo estiver aberto. Um menu oferece “Mosca ligada” como opção marcada/desmarcada e “Encerrar”. A ativação primária do ícone deve alternar o estado quando o host oferecer esse gesto; o menu é o caminho obrigatório e verificável. Tooltip: “FruitFly: ligada”, “FruitFly: desligada” ou “FruitFly: erro”.

O primeiro início após a instalação fica desligado, com o ícone disponível. Inícios seguintes restauram a última escolha. Desligar congela a simulação e preserva a memória neural em RAM, remove a superfície visível e cessa a coleta do cursor e das janelas. Religá-la retoma a memória com geometria atualizada, sem executar o tempo que passou desligada. Encerrar descarta a sessão neural; persistência do cérebro entre execuções fica para uma expansão.

Se a bandeja não estiver disponível, o processo deve informar o problema e manter uma forma de desligar por CLI. Não deve iniciar uma mosca visível sem um controle acessível. O registro do tray e a reconexão após reinício do host fazem parte da prova P0.

## Metas de qualidade propostas

As metas abaixo são critérios de produto, não medições já obtidas. O ticket FF-007 registra o hardware, a carga de trabalho e a viabilidade antes de fixá-las para a versão 1.

| Medida | Meta inicial | Como verificar |
|---|---|---|
| Renderização em movimento | 60 FPS quando suportado; modo econômico de 30 FPS. | Registrar intervalo entre quadros com a mosca ativa e aplicativos em uso. |
| Latência da reação urgente | Até 100 ms no percentil 95 entre a observação disponível e o movimento visível. | Replay instrumentado e medição do caminho completo, separando amostragem e decisão. |
| CPU ativa | Alvo de até 3% de um núcleo em média para todos os processos do pet no hardware de referência. | Sessão de referência de dez minutos; informar picos e custo do compositor separadamente. O teste curto não fecha esse requisito. |
| CPU em repouso | Alvo de até 1% de um núcleo, sem redesenhos de uma pose inalterada. | Medir um período de repouso escolhido pela rede. |
| Memória de CPU | Até 500 MiB de RSS somada como alvo inicial, sujeito ao custo do backend GPU. | Medir runtime, bibliotecas e UI após aquecimento e uso prolongado. |
| Memória de GPU | Até 512 MiB de VRAM adicional para o pet. | Separar contexto do backend, arrays neurais e recursos gráficos. |
| Tempo de GPU | Até 4 ms por ciclo de controle no percentil 95, como orçamento inicial. | Cronometrar execução com sincronização correta e medir também o caminho completo. |
| Desligado | Zero passos neurais e zero consultas de cursor/janelas. | Contadores permanecem estáveis durante um minuto; tray e controle continuam ativos. |
| Controle | Desligar remove a mosca em até 500 ms. | Acionar menu sob carga e com cérebro travado. |
| Confiabilidade | Uma hora sem travamento, processo órfão ou perda de controle. | Sessão com fullscreen, troca de workspace e mudanças de monitor. |

## Prioridades e marcos

| Marco | Prioridade | Entrega e condição de passagem |
|---|---|---|
| M0: viabilidade | P0, urgente | Comprovar backend GPU, overlay com cursor, tray publicável, oclusão possível e rede com comandos úteis; medir custo e registrar limites. |
| M1: primeira mosca neural | P1, necessário | Sprite frontolateral, liga/desliga e circuito de fuga acoplado ao corpo, com exploração neural básica. É uma versão de desenvolvimento. |
| M2: repertório | P1, necessário | R01–R10 funcionam juntos, com competição neural e esconderijo. |
| M3: versão 1 | P1, necessário | Todos os requisitos F01–F14 passam, pacote instalável, documentação e desempenho verificados. |
| Expansões | P2, depois da versão 1 | CO₂ virtual, fidelidade maior de oclusão, investigação BANC e adaptação online. |

O caminho crítico passa pela aquisição do cursor, pelo custo do cérebro e pela capacidade da rede de escolher ações sem regras externas. A arte inicial e a auditoria de dados podem avançar em paralelo com essas provas. Uma dificuldade na política neural não autoriza substituí-la silenciosamente por regras nem reduzir o requisito das dez respostas.

A inspeção identificou uma GPU AMD Navi 33, alvo `gfx1102`, com aproximadamente 8 GiB de VRAM. O ensaio HIP posterior identificou a Radeon RX 7600 e executou o núcleo neural com resultado próximo da referência CPU. Ainda falta validar uma pilha de treinamento e outras configurações. A presença de ferramentas CUDA no sistema não implica hardware NVIDIA disponível.

A CPU compilada também é um backend de uso, escolhido para o primeiro recorte após medição. A prova GPU funcionou na RX 7600, mas teve ciclo mais lento nessa configuração. Circuitos maiores podem justificar outra decisão. O teste precisa incluir outros aplicativos usando a mesma GPU e verificar se o pet aumenta o consumo em repouso.

## Fora da primeira versão e riscos

Não estão previstos: corpo biomecânico 3D, cérebro inteiro, treinamento durante o uso normal, múltiplas moscas, controle de cliques do usuário ou serviço em nuvem. BANC está presente na pasta e é uma possibilidade de pesquisa futura, cuja compatibilidade precisa ser auditada; arquivos com prefixos diferentes não serão concatenados como um único grafo. [S11](RESEARCH.md)

Os maiores riscos são a rede ficar inativa ou instável, a informação sensorial ser insuficiente para escolher abrigo e a oclusão não acompanhar bem janelas animadas. As provas P0 precisam produzir resultados reproduzíveis e alternativas concretas. Quando houver lacuna científica, o manifesto registra a hipótese usada. Quando houver limite técnico, o relatório apresenta o comportamento realmente alcançado e a mudança necessária no escopo.

## Conclusão da versão 1

A entrega exige as dez respostas na mesma mosca, comandos rastreáveis à rede, participação causal demonstrada do circuito FlyWire de fuga e origem declarada das demais funções. Exige também controle confiável no systray e ocultação atrás de janelas nos casos suportados. O [TODO](TODO.md) descreve as evidências necessárias para fechar cada tarefa.
