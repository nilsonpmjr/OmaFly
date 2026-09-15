# Primeiro protótipo: resultados e pendências

Em 14 de setembro de 2026 foi implementada uma versão experimental com núcleo neural, sprite frontolateral, systray e controle por CLI. Ela roda a partir do checkout e começa desligada. O teste gráfico encerrou sua própria instância ao terminar; nenhum autostart ou arquivo de configuração do Omarchy foi instalado.

## Etapa atual: abrigo neural, 15/09

Seleção recorrente de entradas, contato por cruzamento, ocultação e retorno foram integrados ao worker. Passaram **27 testes**, incluindo quatro bordas, duas frequências, múltiplas janelas, geometria alterada, históricos diferentes, ablação seletiva e pausa sem socket de eventos. A prova com uma janela real e cursor sintético completou entrada, ocultação total e reaparecimento. Evidências em [NEURAL-SHELTER.md](NEURAL-SHELTER.md).

A coleta agrupa eventos, faz snapshots de segurança a cada dois segundos e acompanha mudanças/abrigo em até cinco snapshots por segundo. A caminhada usa até dez redesenhos por segundo; o controle neural permanece em até 25 Hz. Ocultação total remove a superfície visível e interrompe quadros repetidos, mantendo a rede ativa.

Na medição final de caminhada exposta: **1,37% de um núcleo**, **185 MiB de PSS**, contadores estáveis ao desligar e socket de eventos fechado. A placa inteira marcou **17–18 W ativa e cerca de 5 W desligada**, diferença também observada na rodada anterior. A limitação de quadros não resolveu o custo gráfico; sua investigação permanece prioritária em FF-034. O teste curto não isola a energia do pet nem valida o pior caso de seleção. `desktop-smoke.json` contém esta rodada; `desktop-before-frame-gate.json` preserva a anterior.

Os critérios completos de FF-023/FF-024 continuam abertos: calibração, contextos mais variados e matriz gráfica. Dez respostas, passagem entre monitores e release empacotado permanecem pendentes.

## Prova geométrica de 14/09 (histórico)

A base de FF-004 foi implementada no renderizador e passou nas oito etapas da prova gráfica com janela própria. O recorte parcial/total e o reaparecimento foram comparados pixel a pixel, incluindo movimento, redimensionamento, saída/retorno do workspace e fechamento. O [relatório de ocultação](OCCLUSION.md) registra as capturas, limitações e reprodução.

São **17 testes automatizados aprovados**, incluindo a exploração corrigida e a ablação no ciclo cérebro–corpo da iteração com o SVG sugerido. O teste normal do aplicativo com o novo componente visual passou: cerca de **1,99% de um núcleo de CPU**, **175 MiB de PSS** e **341 MiB de RSS somada** durante oito segundos ativos. Desligado por três segundos, os contadores permaneceram estáveis e não houve incremento de CPU detectado; PSS de aproximadamente 53 MiB. A placa inteira marcou 26 W tanto ativa como desligada nesta rodada; o valor não isola consumo do pet. Essa é a medição histórica; o JSON atual corresponde à etapa de 15/09.

Na etapa de 14/09, a escolha de abrigo era roteirizada exclusivamente na prova. A integração neural foi realizada em 15/09, conforme a seção atual acima. FF-004 e FF-013 continuam abertos para integração e casos gráficos ainda não testados.

## Medições históricas do primeiro protótipo

| Ensaio | Resultado | Escopo |
|---|---|---|
| Núcleo CPU, cinco segundos | 0,60% de um núcleo; 0,24 ms por ciclo em média. | C++ e ctypes, sem interface. |
| Núcleo GPU, cinco segundos | 0,54 ms por ciclo, incluindo transferências. | HIP na Radeon RX 7600, 25 ciclos por segundo. |
| Concordância CPU/GPU | Diferença máxima de 0,000183 Hz nas taxas finais. | Mesmo circuito e estímulo constante. |
| Aplicativo ativo, cerca de oito segundos | 1,74% de um núcleo; aproximadamente 182 MiB de PSS e 347 MiB de RSS somada. | Supervisor, worker e Quickshell; não inclui CPU do compositor. |
| Desligado após uso, cerca de três segundos | Nenhum incremento de CPU detectado na resolução da amostra; contadores estáveis em 245 passos de controle e 250 consultas. | Supervisor e worker preservado; sobreposição encerrada. |
| Memória desligado | Aproximadamente 53 MiB de PSS e 102 MiB de RSS somada. | Estado neural preservado em RAM. |

A placa inteira reportou 16 W nas amostras ativas e desligadas da rodada final. A resolução e o ambiente compartilhado não permitem concluir consumo incremental zero nem atribuir watts ao pet. Outros ensaios foram descartados para a comparação de desligado porque houve cliques no ícone durante a sequência automática.

Os dados do núcleo ficam em `core-benchmark.json` e `gpu-benchmark.json`. `desktop-smoke.json` contém a rodada mais recente, descrita acima. O teste ativo é curto e não demonstra os orçamentos em sessões prolongadas, hardware diferente ou carga gráfica elevada.

## Evidência funcional

O extrator preserva IDs como strings e associa os registros à classificação local. Foram exportados 320 neurônios e 1.705 pares de conexão em cerca de 310 KiB. Hashes, critérios e limitações estão no próprio manifesto; a licença dos dados ainda precisa ser confirmada antes de distribuição.

Os testes numéricos verificam que agrupar subpassos não muda a simulação. Uma ablação seletiva remove entradas da fibra gigante mantendo o estímulo dos neurônios visuais: a atividade de saída muda, demonstrando influência causal neste modelo. Isso não constitui validação biológica da dinâmica escolhida.

O teste gráfico confirmou carregamento do sprite, aquisição do cursor, execução contínua e desligamento sem coleta residual. O processo pode ser encerrado pela CLI ou pelo tray. Os testes do worker usam um compositor simulado e confirmam pausa sem consultas e retomada com memória em RAM.

A primeira iteração passou em 11 testes automatizados; a atual passa em 27. Compilação Python, links dos documentos e dimensões das grades de sprites também foram verificados. O `qmllint` ainda emite avisos sobre tipos dinâmicos do Quickshell (`PanelWindow` e `margins`); a execução real carregou essa interface, sem erro de imagem na rodada final.

## Trabalho restante

M0 continua aberto. Ainda faltam calibração dos abrigos e demais casos gráficos da oclusão, auditoria de origem/licença dos dados, critérios funcionais mais completos da política e matriz de monitores/foco/fullscreen. A versão 1 também exige as dez respostas na mesma rede, empacotamento do plugin e validação prolongada de consumo.

A preferência por baixo consumo foi incorporada ao PRD como F14. Para este recorte, a CPU compilada é o padrão; a GPU permanece como experimento de aceleração. O worker limita trabalho e reserva descanso em dispositivos lentos, podendo reduzir a frequência efetiva em vez de ocupar continuamente um núcleo.
