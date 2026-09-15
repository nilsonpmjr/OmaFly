# Primeiro protótipo: resultados e pendências

Em 14 de setembro de 2026 foi implementada uma versão experimental com núcleo neural, sprite frontolateral, systray e controle por CLI. Ela roda a partir do checkout e começa desligada. O teste gráfico encerrou sua própria instância ao terminar; nenhum autostart ou arquivo de configuração do Omarchy foi instalado.

## Etapa atual: prova de ocultação

A base de FF-004 foi implementada no renderizador e passou nas oito etapas da prova gráfica com janela própria. O recorte parcial/total e o reaparecimento foram comparados pixel a pixel, incluindo movimento, redimensionamento, saída/retorno do workspace e fechamento. O [relatório de ocultação](OCCLUSION.md) registra as capturas, limitações e reprodução.

São **17 testes automatizados aprovados**, incluindo a exploração corrigida e a ablação no ciclo cérebro–corpo da iteração com o SVG sugerido. O teste normal do aplicativo com o novo componente visual passou: cerca de **1,99% de um núcleo de CPU**, **175 MiB de PSS** e **341 MiB de RSS somada** durante oito segundos ativos. Desligado por três segundos, os contadores permaneceram estáveis e não houve incremento de CPU detectado; PSS de aproximadamente 53 MiB. A placa inteira marcou 26 W tanto ativa como desligada nesta rodada; o valor não isola consumo do pet. `desktop-smoke.json` contém esta medição mais recente.

A escolha e a entrada no abrigo ainda são roteirizadas exclusivamente na ferramenta de prova. O pet normal não consulta janelas nem escolhe abrigo nesta etapa. O próximo trabalho é conectar candidatos geométricos e comandos neurais de entrada/saída, com coleta de eventos limitada por orçamento. FF-004 e FF-013 continuam abertos para integração e casos gráficos ainda não testados.

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

A primeira iteração passou em 11 testes automatizados; a atual passa em 17. Compilação Python, links dos documentos e dimensões das grades de sprites também foram verificados. O `qmllint` ainda emite avisos sobre tipos dinâmicos do Quickshell (`PanelWindow` e `margins`); a execução real carregou essa interface, sem erro de imagem na rodada final.

## Trabalho restante

M0 continua aberto. Ainda faltam integração neural dos abrigos e demais casos gráficos da oclusão, auditoria de origem/licença dos dados, critérios funcionais mais completos da política e matriz de monitores/foco/fullscreen. A versão 1 também exige as dez respostas na mesma rede, empacotamento do plugin e validação prolongada de consumo.

A preferência por baixo consumo foi incorporada ao PRD como F14. Para este recorte, a CPU compilada é o padrão; a GPU permanece como experimento de aceleração. O worker limita trabalho e reserva descanso em dispositivos lentos, podendo reduzir a frequência efetiva em vez de ocupar continuamente um núcleo.
