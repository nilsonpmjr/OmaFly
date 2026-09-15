# Primeira implementação e orçamento de execução

Esta é uma versão experimental de fuga e exploração. O catálogo completo de dez respostas, os esconderijos e o pacote instalável ainda estão em desenvolvimento. As escolhas da mosca no protótipo vêm do circuito extraído e de uma pequena rede recorrente construída; os pesos dessa rede estão identificados como parâmetros de engenharia em `brain.py`.

## SVG e exploração nesta iteração

O desenho fornecido em `ai_studio_code_v3.txt` é o sprite atual. Uma cópia integral fica em `assets/fly-source.svg`; o gerador produz poses de repouso, caminhada e voo sem alterar o original. No voo, as patas ficam recolhidas e somente as asas alternam. Na caminhada, as patas acompanham a distância percorrida. A orientação considera que o novo desenho olha originalmente para a esquerda.

O corpo recebe velocidade, giro e ativação de voo da rede. A animação usa dois quadros por ciclo, a 8 ciclos visuais por segundo durante o voo, dentro do mesmo loop limitado do worker. Essa frequência é uma convenção visual, não uma simulação da frequência biológica das asas. Não há timer adicional nem atualização de pose em repouso.

A exploração anterior perdia a oscilação e podia ficar presa em cantos com comandos de giro simétricos. A rede recorrente agora sustenta sua fase interna e recebe modulação bilateral dos sensores de borda. Seus pesos continuam sendo parâmetros construídos; o FlyWire fundamenta o recorte de fuga, não todo o comportamento espontâneo.

`tests/test_behavior.py` verifica exploração em janelas sucessivas de 30 segundos, durante três minutos simulados por cenário, com duas sementes/frequências e partidas no centro e em cantos. Também compara a mesma cena com e sem entradas da fibra gigante: a ablação elimina o comando de voo. Isso demonstra influência causal no protótipo, sem validar biologicamente seus parâmetros. `./run.sh status` expõe modo corporal, velocidade, giro, ativação de voo e taxa da fibra gigante na telemetria já existente.

## Base de ocultação por janela

O desenho aceita agora uma lista `clips` de até quatro retângulos locais. Ausência desse campo mantém a mosca exposta; uma lista vazia oculta o desenho inteiro. `occlusion.py` calcula a geometria a partir de um abrigo explícito, e `FlySprite.qml` aplica o recorte separado da máscara de input. O worker normal ainda não seleciona abrigos nem consulta janelas.

A prova `python tools/probe_occlusion.py` abre e manipula somente uma janela própria, usa o componente visual de produção e encerra sua instância temporária ao terminar. Oito etapas passaram com comparação de alfa pixel a pixel, incluindo movimento, redimensionamento, mudança de workspace e fechamento. As posições dessa prova são roteirizadas; a seleção e a entrada neural serão integradas depois. Resultados e limites estão em [OCCLUSION.md](../reports/OCCLUSION.md).

## Mudança de prioridade

O pedido mais recente coloca baixo consumo e funcionamento em outros dispositivos acima da preferência anterior pela GPU. A implementação mantém uma referência compilada para CPU e uma prova GPU comparável. O backend padrão do protótipo é CPU; nenhuma biblioteca ROCm, CUDA ou de treinamento é carregada durante seu uso normal.

O ensaio HIP foi executado na Radeon RX 7600 e concordou com a referência CPU, com erro máximo de cerca de 0,0002 Hz nas taxas finais. O ciclo de 40 ms neurais levou aproximadamente 0,24 ms na CPU e 0,54 ms no ensaio GPU, incluindo transferências. Essa comparação curta apoia manter o circuito pequeno na CPU; não mede isoladamente eficiência energética nem garante o mesmo resultado em outros dispositivos.

## Proteções já implementadas

- núcleo C++ esparso, sem threads de trabalho, alocações ou espera ocupada no passo neural;
- subpassos neurais agrupados em uma chamada, preservando o resultado do passo de 1 ms;
- coleta direta pelo IPC do Hyprland, sem criar um subprocesso `hyprctl` por amostra;
- ciclo sensorial de até 25 Hz em movimento e até 10 Hz em repouso;
- tempo de descanso adicional quando o trabalho excede o orçamento de CPU do worker;
- nenhuma recuperação de atraso por uma sequência de ciclos sem descanso;
- superfície de 64 × 64 pixels, evitando uma superfície do tamanho do monitor;
- emissão de novos quadros somente quando posição, orientação ou fase do sprite mudam;
- nenhum timer de animação contínuo no QML;
- ao desligar, destruição da sobreposição e suspensão do worker numa espera por comando;
- estado neural em RAM para religar, sem continuar simulação ou coleta em segundo plano;
- desligamento e encerramento acessíveis pelo systray e pela CLI.

O orçamento inicial do worker reserva descanso para visar até 2% de um núcleo no loop sustentado. Ele não é um limite imposto pelo kernel nem um teto sobre o compositor e o Qt. Se uma máquina precisar desse descanso adicional, a resposta pode ficar mais lenta; não há recuperação acelerada de tempo perdido. O comportamento em hardware lento precisa de validação própria.

## Preparar e executar

Na pasta do projeto, usando as dependências já instaladas no ambiente Omarchy inspecionado:

```sh
python tools/build.py
python tools/build_assets.py
python tools/extract.py
./run.sh run
```

A primeira execução abre somente o ícone na bandeja. Use a opção “Mosca ligada” para exibir o protótipo. A CLI controla a mesma instância:

```sh
./run.sh enable
./run.sh status
./run.sh disable
./run.sh quit
```

O runtime usa Python, PySide6, Quickshell e o núcleo compilado. A extração dos dados acontece uma vez, antes do uso. O modelo compacto contém 320 neurônios e 1.705 pares de conexão; a interface não lê os CSVs.

Esta fase roda a partir do checkout. Instalação via `pip`, autostart e integração empacotada em `~/.config/omarchy/plugins/` ainda não estão implementados. Nenhum arquivo de configuração do desktop foi alterado.

## Reproduzir as verificações

```sh
PYTHONPATH=src python -m unittest discover -s tests -v
python tools/environment.py
python tools/benchmark.py --seconds 5
python tools/smoke_desktop.py
```

O último comando abre uma instância temporária, liga e desliga a mosca e a encerra ao terminar. Não o execute enquanto estiver usando outra instância. O teste falha se o estado mudar durante a medição; interagir com o tray nesse período altera o resultado.

Os testes de unidade cobrem reprodução temporal, inibição de saídas sem identidade conhecida, precisão dos IDs, ablação seletiva, limites de carga e suspensão real do worker com um compositor simulado. O teste gráfico verifica carregamento do sprite, processos e estabilidade dos contadores ao desligar. Ele ainda não substitui testes de fullscreen, foco, transparência de input, múltiplos monitores ou uso prolongado.

Para repetir o ensaio de GPU AMD, somente após gerar `build/gpu-input.bin` pelo benchmark:

```sh
/opt/rocm/bin/hipcc -O2 --offload-arch=gfx1102 native/gpu_probe.cpp -o build/gpu-probe
build/gpu-probe build/gpu-input.bin build/gpu-output.bin
```

O alvo `gfx1102` é específico da máquina inspecionada; outros dispositivos exigem configuração e teste próprios. A prova roda por cinco segundos em 25 ciclos por segundo, com descanso entre ciclos. O executável GPU é uma ferramenta de comparação e ainda não é um backend selecionável do pet.

## Limites da versão experimental

As saídas dos cinco neurônios sem neurotransmissor definido têm eficácia zero, com a anatomia preservada no manifesto. O modelo assume sinais simplificados para os demais neurotransmissores, campos receptivos sintéticos e dinâmica LIF normalizada. Essas hipóteses não foram calibradas contra comportamento biológico.

Ainda faltam os dez comportamentos completos, integração neural da oclusão por janelas, persistência entre execuções, reconexão ao tray após falha do host, suspensão por bloqueio da sessão e migração entre monitores sem contenção na borda. Os estados de erro são visíveis no tooltip e na CLI. Esta versão não deve ser instalada como serviço permanente até esses casos serem verificados.

Os relatórios JSON em `reports/` guardam medições reproduzíveis. RSS soma páginas compartilhadas entre processos; PSS, quando disponível, ajuda a estimar o custo efetivo. As amostras de potência são da placa inteira, também usada pelo desktop e por outros aplicativos. Elas não permitem atribuir uma diferença de watts exclusivamente à mosca.
