# TODO e tickets do FruitFly

Entrega de `/to-tickets`, atualizada em 14 de setembro de 2026. Existe um protótipo de fuga/exploração, ainda sem fechar os critérios completos de M0. A execução está registrada em [IMPLEMENTATION.md](IMPLEMENTATION.md) e [relatório de progresso](../reports/STATUS.md).

FF-001, FF-002, FF-003, FF-005, FF-006, FF-008–FF-012, FF-014 e FF-033 têm implementação ou evidência parcial. Permanecem abertos até atenderem a todos os respectivos critérios. O requisito posterior de baixo consumo substitui a GPU obrigatória por comparação de backends e acrescenta F14.

Nesta iteração, FF-006, FF-012, FF-014, FF-019 e FF-026 ganharam evidências adicionais: SVG sugerido integrado, animação ligada ao comando de voo, exploração sem bloqueio nos cantos dos cenários automatizados e ablação no ciclo cérebro–corpo. Com a prova de ocultação, são 17 testes aprovados; esses tickets permanecem abertos para os demais critérios de aceite.

O [PRD](PRD.md) define o resultado e a [especificação](SPEC.md) define os contratos propostos. Os identificadores F e R abaixo apontam para requisitos e respostas do PRD.

## Ordem de execução

P0 resolve viabilidade e decisões que bloqueiam outras tarefas. P1 entrega o escopo completo da versão 1, incluindo as dez respostas. P2 contém expansões que podem esperar. O esforço indica tamanho relativo: S é uma tarefa delimitada, M envolve um componente e L envolve integração ou pesquisa com incerteza. Não são estimativas em dias.

| Etapa | Tickets | Saída |
|---|---|---|
| Primeiro | FF-001 e FF-005 | Ambiente registrado e dados auditados. |
| Provas independentes após ambiente | FF-002, FF-003 e FF-033 | Overlay/cursor, publicador de tray e backend GPU. |
| Provas dependentes | FF-004 e FF-006 | Oclusão demonstrada e comandos neurais úteis. |
| Fechar M0 | FF-007 | Arquitetura, orçamento e critérios de avanço registrados. |
| Fundação de M1 | FF-008–FF-014 | Runtime, sensores, cérebro, corpo, desenho e oclusão. |
| Primeira mosca neural | FF-015 e FF-019 | Fuga e exploração no mesmo modelo. |
| Completar M2 | Demais tickets FF-016–FF-024 | Dez respostas disponíveis e compatíveis. |
| Entregar M3 | FF-025–FF-028 | Integração, evidência causal, qualidade e instalação. |

O número FF-033 foi acrescentado quando o usuário autorizou o uso da GPU; sua prioridade é P0 e ele deve ser executado no começo.

## P0: urgente

### FF-001: registrar ambiente e restrições

- [ ] **P0 · S · Dependências: nenhuma · Requisitos: F04, F06, F08, F12, F13.** Registrar versões, GPU, driver, Python, APIs locais do Omarchy e layout de monitores, sem mudar a configuração do usuário.

**Aceite:** relatório em `reports/environment.md` com comandos reproduzíveis, distinção entre biblioteca instalada e API exercitada, lacunas de acesso e dependências propostas. Confirmar quais versões das bibliotecas atendem ao Python escolhido. Não registrar títulos nem conteúdo dos aplicativos.

### FF-002: provar overlay e aquisição do cursor

- [ ] **P0 · M · Dependências: FF-001 · Requisitos: F04, F08.** Desenhar um marcador transparente com Quickshell e obter cursor global por IPC limitado.

**Aceite:** marcador acima de aplicativo comum e fullscreen, cliques atravessando, foco intacto e coordenadas corretas em escala fracionária e origem negativa. Comparar frequências de consulta e medir latência/custo. Encerrar o marcador deixa a sessão como estava. Usar posicionamento de teste é permitido nesta prova visual; não conta como controle neural entregue.

### FF-003: provar ícone publicável no systray

- [ ] **P0 · M · Dependências: FF-001 · Requisitos: F06, F07, F11.** Publicar um StatusNotifierItem pelo supervisor Qt/PySide6 com ícone provisório e menu.

**Aceite:** “Mosca ligada” alterna estado; “Encerrar” remove o item. Testar ausência e reinício do host, ativação primária quando suportada e tentativa de segunda instância. Confirmar que o caminho publica um item real, em vez de apenas desenhar um widget na barra.

### FF-004: provar oclusão por uma janela

- [ ] **P0 · M · Dependências: FF-002 · Requisitos: F05, F08.** Recortar um sprite de teste na borda de uma janela opaca, mantendo o overlay na camada superior.

**Aceite:** ocultação parcial e total, seguida de reaparecimento; mover, redimensionar, fechar e trocar workspace não deixa resíduos. Registrar atraso, limitações de cantos/transparência e regra para janelas sobrepostas. Demonstrar separadamente que a máscara de input não é o mecanismo de recorte visual.

**Progresso de FF-004:** a prova com janela própria passou em oito etapas no compositor real, com comparação pixel a pixel: exposição, recorte parcial/total, movimento, redimensionamento, saída/retorno de workspace e fechamento. O componente está no desenho de produção; a escolha de abrigo permanece apenas roteirizada na prova. Faltam atraso durante arraste e casos de sobreposição/transparência. Evidências em [OCCLUSION.md](../reports/OCCLUSION.md).

### FF-005: auditar dados e extrair candidato de fuga

- [ ] **P0 · M · Dependências: nenhuma · Requisitos: F02, F09, F10.** Registrar origem e versão dos arquivos, selecionar IDs e extrair conexões relevantes de LC4/LPLC2 e descendentes, preservando lateralidade.

**Aceite:** ferramenta reproduzível, manifesto com hashes/licenças e relatório de cobertura, duplicações e descartes. IDs sobrevivem à passagem por JSON sem perda de precisão. Contagens da inspeção são reproduzidas ou diferenças são explicadas. Nenhum arquivo de outro conectoma é misturado ao grafo.

### FF-033: validar GPU AMD e escolher backend

- [ ] **P0 · L · Dependências: FF-001 · Requisitos: F13.** Verificar `gfx1102` com ROCm/HIP e ambiente de bibliotecas isolado; testar Vulkan compute se necessário.

**Aceite:** executar um kernel representativo de integração neural e uma projeção recorrente na GPU real, validar contra NumPy e registrar versões, compatibilidade e mecanismo de medição. Mostrar tempo de execução, ida/volta de dados e custo do contexto. Vulkan, se escolhido, tem pipeline reproduzível para kernels e importação de pesos. A presença de ROCm ou `nvidia-smi` não basta para fechar o ticket. Se houver bloqueio, documentar a causa e uma proposta concreta de resolução, sem marcar o backend como funcional.

**Progresso:** o kernel LIF HIP rodou na RX 7600 e foi comparado à referência C++, com diferença máxima de cerca de 0,0002 Hz. A GPU teve ciclo mais lento neste recorte e não é carregada pelo pet. Ainda faltam comparação de projeção recorrente, energia isolada e outras classes de hardware. A referência C++ substitui a referência NumPy neste ensaio.

### FF-034: limitar consumo sustentado e validar modos de repouso

- [ ] **P0 · M · Dependências: FF-002, FF-003, FF-006 · Requisitos: F14.** Comparar o custo completo dos processos, eliminar trabalho desligado e impedir que ciclos atrasados causem espera ocupada.

**Aceite:** teste prolongado ativo, repouso neural e desligado; orçamento de CPU documentado, nenhuma recuperação em rajada e redução de redesenhos. Medir custo adicional no compositor e em um dispositivo menos potente. O teste curto já confirma suspensão dos contadores e descanso sob atraso simulado; ele não fecha sozinho este ticket.

### FF-006: provar controle neural e estratégia de ajuste

- [ ] **P0 · L · Dependências: FF-005, FF-033 · Requisitos: F02, F10, F13.** Acoplar o circuito candidato a uma pequena rede recorrente numa arena sem UI, com referência CPU e execução GPU.

**Aceite:** a rede produz pelo menos movimento e uma resposta contextual à aproximação, sem um seletor externo de ações. Registrar parâmetros, entradas e comandos; uma ablação seletiva modifica a resposta. Definir como calibrar ou treinar os módulos que completarão as dez respostas. Uma animação movida por uma regra de distância não fecha a prova.

### FF-007: fechar viabilidade, contratos e orçamento

- [ ] **P0 · M · Dependências: FF-002, FF-003, FF-004, FF-006, FF-033 · Requisitos: F01–F13.** Consolidar as provas, medir execução concorrente e atualizar SPEC com decisões tomadas.

**Aceite:** backend, tamanho inicial da rede, passos temporais, estratégia de treino e coleta definidos; metas de CPU, RSS, VRAM e latência validadas ou revisadas com justificativa. Medir impacto no compositor usando a mesma GPU. Registrar limites suportados de oclusão e a decisão de avançar ou resolver cada bloqueio.

## P1: fundação da versão 1

### FF-008: implementar supervisor, tray e IPC

- [ ] **P1 · M · Dependências: FF-007 · Requisitos: F06, F07, F11.** Implementar instância única, publicação do tray e comandos idempotentes `enable`, `disable`, `status` e `quit`.

**Aceite:** estado confirmado pelo supervisor, interrupção de worker travado, controle acessível sem rede neural saudável e reconexão após reiniciar a barra. Desligar impede passos, polling e lançamentos na GPU; encerrar remove os processos. Testar retomada, preferências e indisponibilidade do tray.

### FF-009: implementar mundo e codificação sensorial

- [ ] **P1 · M · Dependências: FF-007 · Requisitos: F02, F08.** Implementar geometria, cursor relativo, expansão visual sintética, candidatos de abrigo e feedback corporal.

**Aceite:** unidades e timestamps documentados, entradas válidas em vários monitores, percepção reduzida atrás do abrigo e pausa em dados obsoletos. Nenhum campo codifica a ação recomendada. Os mesmos cenários alimentam treino, CPU, GPU e desktop.

### FF-010: implementar núcleo neural e pacote GPU

- [ ] **P1 · L · Dependências: FF-007 · Requisitos: F02, F09, F10, F13.** Implementar o backend escolhido, estado residente, sinapses esparsas e exportação/carregamento do pacote.

**Aceite:** equivalência com referência numérica dentro de tolerância fixada, teste de passo temporal, inicialização reproduzível e arrays fora da CPU durante os subpassos. Manifesto separa conexões biológicas e construídas. A UI recebe amostras compactas sem cópia integral da rede a cada quadro.

### FF-011: implementar política recorrente e calibração offline

- [ ] **P1 · L · Dependências: FF-009, FF-010 · Requisitos: F02, F03, F13.** Implementar memória, competição neural e decodificação motora, com ajuste reproduzível em arena.

**Aceite:** treino e avaliação separados, origem dos parâmetros registrada e controles contínuos exportados para a GPU. O decodificador não consulta desktop ou ameaça. Documentar como o circuito de fuga participa das escolhas e como impedir que a política aprenda a ignorá-lo. Não incluir treinamento no loop normal do desktop.

### FF-012: implementar corpo cinemático 2D

- [ ] **P1 · M · Dependências: FF-007 · Requisitos: F01, F02.** Implementar integração, avanço/recuo, giro, elevação, contato e esforço.

**Aceite:** entradas motoras reproduzidas produzem a mesma trajetória dentro da tolerância; contatos retornam feedback e não selecionam uma nova ação. A física não decide fugir nem explorar. Os limites impedem perda do corpo, com contadores que permitem detectar dependência indevida dessas proteções.

### FF-013: implementar renderização e abrigo visual

- [ ] **P1 · M · Dependências: FF-008, FF-009, FF-012 · Requisitos: F04, F05, F08.** Implementar overlay, snapshots, entrada/saída geométrica de abrigo e recorte por monitor.

**Aceite:** uma mosca atravessa monitores sem duplicação; abrigo segue a janela e reage a fechamento conforme SPEC. Cliques e foco permanecem corretos. O renderizador não escolhe abrigo nem define a duração da ocultação; imagens provisórias bastam até FF-014.

### FF-014: produzir atlas pixel art e ícone

- [ ] **P1 · M · Dependências: FF-007 · Requisitos: F01, F06.** Produzir arte frontolateral com caminhada, voo, repouso, pouso e limpeza, além de cabeça vista de cima para o tray.

**Aceite:** atlas com transparência e metadados, orientação consistente, escala inteira e visual legível no desktop. Ícone ligado/desligado distingue estado além da cor; verificar tamanhos efetivos do tray e temas claro/escuro. Registrar autoria/licença e integrar fases de animação ao contrato motor.

## P1: dez respostas neurais

Os tickets seguintes compartilham um critério: registrar entrada, atividade, comando e resultado; criar cenário positivo, controle negativo e conflito. Fixar métricas antes da calibração final e avaliar em pelo menos 20 sementes fora do treino. Se houver circuito biológico candidato, auditar antes de atribuir a ele o comportamento. O êxito de um ticket isolado não substitui a validação conjunta de FF-025.

### FF-015: R01, fuga rápida orientada

- [ ] **P1 · L · Dependências: FF-009, FF-010, FF-011, FF-012 · Requisitos: R01, F02, F10, F13.** Calibrar estímulo visual e participação do circuito de fuga, incluindo direção neural.

**Aceite:** separar aproximação, afastamento e passagem distante; medir latência e aumento de separação. Mostrar efeito de ablação de LC4/LPLC2 ou seus alvos dentro da política integrada. Preservar informação espacial ou documentar seu substituto sintético. Decolagem e giro de fuga integram esta resposta, sem inflar a contagem.

### FF-016: R02, imobilização defensiva

- [ ] **P1 · M · Dependências: FF-011, FF-012, FF-015 · Requisitos: R02.** Acrescentar resposta de imobilização dependente de contexto e investigar o candidato DNp09.

**Aceite:** mostrar contexto em que imobiliza e contexto em que foge, com trajetórias e estado inicial controlados. Imobilização deve ser uma saída neural mensurável, distinta de rede sem atividade ou falha no motor.

### FF-017: R03, desvio de obstáculo

- [ ] **P1 · M · Dependências: FF-009, FF-011, FF-012 · Requisitos: R03.** Calibrar giro neural diante de bordas e obstáculos virtuais.

**Aceite:** giro ocorre antes do contato em geometrias não usadas no treino. Testar os dois lados, mas contar uma resposta. Comparar com controle sem obstáculo e mostrar que a trajetória não depende do limitador de posição.

### FF-018: R04, recuo por contato

- [ ] **P1 · M · Dependências: FF-011, FF-012 · Requisitos: R04.** Integrar feedback frontal e comando reverso, auditando MDN se usado.

**Aceite:** contato produz deslocamento negativo no eixo corporal; espaço livre não dispara recuo indevido. Não aceitar um ajuste instantâneo da posição como comportamento. Testar reorientação após recuar junto com R03.

### FF-019: R05, exploração espontânea

- [ ] **P1 · M · Dependências: FF-011, FF-012 · Requisitos: R05.** Ajustar atividade espontânea e memória para iniciar locomoção sem roteiro externo.

**Aceite:** medir cobertura e duração de pausas em ambiente tranquilo com várias sementes. Atividade pode variar com ruído neural, mantendo replay com a mesma semente. Registrar que o movimento veio de comandos neurais, sem temporizador ou sorteio externo de ações.

### FF-020: R06, descanso e recuperação

- [ ] **P1 · M · Dependências: FF-015, FF-019 · Requisitos: R06.** Conectar esforço corporal a modulação neural de atividade.

**Aceite:** esforço alto reduz movimento em ambiente tranquilo e recuperação permite retomada. Ameaça urgente altera esse resultado. Publicar a equação de esforço e demonstrar que ela não contém uma escolha direta de descansar.

### FF-021: R07, pouso

- [ ] **P1 · M · Dependências: FF-011, FF-012, FF-015 · Requisitos: R07.** Implementar escolha neural de pouso e sua execução cinemática.

**Aceite:** a rede desacelera e reduz elevação diante de superfície válida; ausência de superfície e ameaça imediata são controles. A animação acompanha o comando e contato, sem iniciar o pouso por conta própria. Atribuição a circuito biológico depende de auditoria adicional.

### FF-022: R08, limpeza das antenas

- [ ] **P1 · M · Dependências: FF-009, FF-011, FF-012, FF-015 · Requisitos: R08.** Auditar candidatos de grooming e adicionar a resposta ao estímulo antenal virtual.

**Aceite:** irritação inicia comando de limpeza em baixo risco, ausência de irritação serve de controle e ameaça interrompe a ação. Classificar o módulo como biológico, projetado ou misto conforme as conexões efetivamente usadas.

### FF-023: R09, busca de abrigo

- [ ] **P1 · L · Dependências: FF-013, FF-015, FF-017, FF-019 · Requisitos: R09, F05.** Ajustar navegação, seleção de janela e acionamento neural de abrigo.

**Aceite:** sob ameaça persistente, a rede escolhe uma entrada alcançável e a cruza antes da ocultação. Testar ausência de abrigo, múltiplas janelas e geometria nova. Proibir seleção de janela pelo renderizador e desaparecimento instantâneo no centro do retângulo.

### FF-024: R10, saída do abrigo e retorno

- [ ] **P1 · L · Dependências: FF-020, FF-023 · Requisitos: R10, F05.** Ajustar memória neural e retomada de exploração após redução da ameaça.

**Aceite:** comparar históricos de perseguição distintos com a mesma observação final; a memória altera a saída conforme o comportamento alvo definido. A mosca reaparece por passagem geométrica válida e pode retornar à área antes ocupada. Não existe timer externo que manda sair ou teletransporta a mosca.

## P1: integração e entrega

### FF-025: integrar as dez respostas no desktop

- [ ] **P1 · L · Dependências: FF-008, FF-013, FF-014, FF-015–FF-024 · Requisitos: F01–F08, R01–R10.** Executar um único modelo com o repertório completo, incluindo conflitos entre fuga, descanso, pouso e limpeza.

**Aceite:** todos os cenários passam na mesma versão dos pesos, sem trocar modelos por comportamento. Sessão manual mostra as dez respostas e não interrompe cliques do usuário. Dez animações sem comandos neurais correspondentes não fecham o ticket.

### FF-026: entregar inspeção, replay e ablação

- [ ] **P1 · M · Dependências: FF-025 · Requisitos: F02, F10.** Oferecer ferramenta de desenvolvimento para visualizar atividade e comandos e repetir observações gravadas.

**Aceite:** comparar modelo completo, ablação seletiva e controles; registrar efeito sobre R01 e funções atribuídas aos módulos. Origem dos parâmetros fica consultável. Telemetria detalhada é opcional e não copia todos os neurônios da GPU a cada quadro no uso normal.

### FF-027: validar desempenho e estabilidade

- [ ] **P1 · M · Dependências: FF-025, FF-026 · Requisitos: F04, F07, F08, F11, F13.** Executar a matriz de desktop e os orçamentos fixados em FF-007.

**Aceite:** relatório com CPU, RSS, VRAM, tempo de GPU e latência ponta a ponta; uma hora de uso sem travamentos. Medir compositor sob carga, repouso, fullscreen, bloqueio, remoção de monitor e reinício do tray. Desligado apresenta zero polling, passos e kernels neurais; o tray continua funcionando quando o worker trava.

### FF-028: empacotar plugin e instalação por usuário

- [ ] **P1 · M · Dependências: FF-027 · Requisitos: F06, F07, F09, F12, F13.** Criar pacote compacto, integração Omarchy, opção de autostart e remoção.

**Aceite:** instalação local reproduzível, manifesto de dependências/modelo e documentação para ligar, desligar e diagnosticar. O plugin controla a mesma instância e o tray é único. Remoção elimina somente arquivos instalados pelo projeto, preserva dados brutos e configurações anteriores. Testar reinstalação, primeira abertura desligada e restauração da preferência.

## P2: depois da versão 1

### FF-029: adicionar campo virtual de CO₂

- [ ] **P2 · L · Dependências: FF-028 · Requisitos futuros.** Investigar circuitos olfativos e codificação espacial de odor.

**Aceite:** proposta com estímulo, contexto e evidência, sem pressupor aversão universal. Expansão não altera silenciosamente os testes visuais da versão 1.

### FF-030: ampliar fidelidade da oclusão

- [ ] **P2 · L · Dependências: FF-028 · Requisitos futuros.** Investigar cantos, transparência, animações e profundidade real no compositor.

**Aceite:** comparação visual e de custo com a oclusão retangular; distinguir recorte do sprite de ordenação real entre janelas. Qualquer dependência de plugin nativo do Hyprland recebe plano de manutenção próprio.

### FF-031: investigar BANC e ampliar circuitos biológicos

- [ ] **P2 · L · Dependências: FF-028 · Requisitos futuros.** Auditar os dados BANC locais e avaliar substituir módulos construídos por circuitos melhor fundamentados.

**Aceite:** compatibilidade e procedência verificadas, correspondências de tipos/IDs explícitas e regressão do repertório completo. Não concatenar conectomas de indivíduos distintos como continuidade neural.

### FF-032: investigar adaptação online e memória persistente

- [ ] **P2 · L · Dependências: FF-028 · Requisitos futuros.** Avaliar mudança de resposta à rotina de uso com aprendizado limitado e opção de reset.

**Aceite:** protocolo distingue estado recorrente, plasticidade e persistência; custo cabe no desktop e o usuário consegue restaurar o modelo original. Não afirmar reconhecimento pessoal do usuário a partir de simples habituação.

## Rastreabilidade da versão 1

| Requisito | Tickets principais |
|---|---|
| F01, pixel art e corpo | FF-012, FF-014, FF-025 |
| F02, decisão neural | FF-005, FF-006, FF-009–FF-012, FF-015–FF-026 |
| F03, dez respostas | FF-015–FF-025 |
| F04, overlay | FF-002, FF-013, FF-027 |
| F05, abrigo | FF-004, FF-013, FF-023–FF-025 |
| F06, systray | FF-003, FF-008, FF-014, FF-028 |
| F07, liga/desliga | FF-008, FF-027, FF-028 |
| F08, monitores/workspaces | FF-002, FF-004, FF-009, FF-013, FF-027 |
| F09, pacote local | FF-005, FF-010, FF-028 |
| F10, evidência FlyWire | FF-005, FF-006, FF-010, FF-015, FF-026 |
| F11, recuperação | FF-003, FF-008, FF-027 |
| F12, integração removível | FF-001, FF-028 |
| F13, GPU | FF-001, FF-033, FF-006, FF-007, FF-010, FF-011, FF-027, FF-028 |
| F14, baixo consumo | FF-034, FF-008, FF-010, FF-013, FF-027 |

Uma tarefa só muda para concluída quando sua evidência está anexada ao ticket ou salva em `reports/`. Pesquisa pode terminar com resultado negativo e novo bloqueio documentado; isso não libera automaticamente os tickets que exigem a funcionalidade. A versão 1 exige todos os P0/P1 concluídos com o escopo do PRD atendido.
