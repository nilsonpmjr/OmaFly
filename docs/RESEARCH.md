# Evidências e limites do planejamento

Consulta em 14 de setembro de 2026. Este registro separa o que foi observado nos arquivos, o que a literatura sustenta e as escolhas propostas para o produto. Não houve instalação, treinamento, simulação neural ou benchmark de GPU nesta etapa.

Este documento registra a etapa original de pesquisa. A implementação e os benchmarks realizados depois estão em [IMPLEMENTATION.md](IMPLEMENTATION.md) e [STATUS.md](../reports/STATUS.md).

## Inspeção local

A pasta contém aproximadamente 17 GB de arquivos, incluindo exportações com prefixos FAFB, BANC, MANC, MAOL e MCNS. A presença de vários conjuntos não demonstra que seus IDs, indivíduos ou versões sejam compatíveis.

| Arquivo | Observação confirmada |
|---|---|
| `fafb-neurons.csv.gz` | Campos incluem `root_id`, `nt_type`, `nt_type_score` e escores de neurotransmissores. |
| `fafb-classification.csv.gz` | Inclui classificação, fluxo, lado e nervo. |
| `fafb-consolidated_cell_types.csv.gz` | Mapeia `root_id` para tipo primário e tipos adicionais. |
| `fafb-connections_princeton.csv.gz` | Colunas `pre_root_id`, `post_root_id`, `neuropil`, `syn_count` e `nt_type`. |
| `fafb-sk_lod1_783_healed.zip` | Diretório central lista 139.273 entradas; a amostra inspecionada contém arquivos `.swc`. O ZIP não foi extraído nem verificado integralmente. |
| `banc-neurons.csv.gz` | Tem esquema próprio, incluindo `Root ID`, tipos celulares e previsões de neurotransmissores. |

Na tabela de tipos consolidados, a contagem de IDs únicos por correspondência exata ao tipo primário foi:

| Tipo | IDs únicos |
|---|---:|
| LC4 | 104 |
| LPLC2 | 210 |
| DNp01 | 2 |
| DNp02 | 2 |
| DNp11 | 2 |
| DNp09 | 2 |
| DNa01 | 2 |
| DNa02 | 2 |
| MDN | 4 |

Uma leitura sequencial da tabela Princeton, associando IDs a esses tipos, encontrou os seguintes registros. “Linhas” não significa pares neuronais únicos, pois a tabela inclui neuropil; a soma corresponde ao campo local `syn_count`, sem afirmar completude anatômica.

| Origem → destino | Linhas | Soma de `syn_count` |
|---|---:|---:|
| LC4 → DNp01 | 139 | 3.080 |
| LC4 → DNp02 | 137 | 2.188 |
| LC4 → DNp11 | 168 | 1.947 |
| LPLC2 → DNp01 | 140 | 1.177 |
| LPLC2 → DNp11 | 1 | 7 |

Esses resultados mostram material para investigar o circuito de fuga. Ainda faltam auditoria de versão, limiares de exportação, vizinhança do circuito, campos receptivos e parametrização funcional. A tabela não demonstra que uma sub-rede já gera um comportamento.

## Ambiente observado

| Componente | Resultado |
|---|---|
| Quickshell | 0.3.1. |
| Hyprland | Pacote 0.56.2-2. |
| Qt | `qt6-base` 6.11.2-3; `pyside6` 6.11.2-1. |
| Python | Pacote 3.14.7-1. |
| NumPy | Pacote 2.5.3-1, módulo encontrado. |
| Bibliotecas | PySide6 e `gi` encontrados; Brian2 e PyTorch não encontrados no Python consultado. |
| GPU | Dispositivo AMD Navi 33, PCI `1002:7480`; ROCm SMI identifica `gfx1102`. O nome comercial exato não foi confirmado. |
| VRAM | `mem_info_vram_total` informa 8.573.157.376 bytes, aproximadamente 8 GiB. |
| ROCm | `rocm-hip-runtime` 7.2.4-1 instalado. A consulta SMI foi parcial, com erro de identificação via libdrm. |
| CUDA | Ferramentas instaladas, mas `nvidia-smi` não conseguiu comunicar-se com um driver NVIDIA; nenhuma GPU NVIDIA foi identificada na listagem PCI consultada. |

A inspeção leu cabeçalhos com `gzip`/`csv`, IDs com conjuntos de strings e o diretório do ZIP com `zipfile`. As consultas de hardware foram `lspci`, `pacman`, leitura de sysfs e ROCm SMI. A enumeração de hardware e módulos não equivale a um teste de execução GPU; FF-033 continua aberto.

Os arquivos locais do Omarchy confirmam plugin de usuário e um padrão de overlay sem input:

- [README do shell](/usr/share/omarchy/shell/README.md): contrato de plugins e processo compartilhado do shell;
- [README dos plugins](/usr/share/omarchy/shell/plugins/README.md): instalação em configuração do usuário;
- [OSD](/usr/share/omarchy/shell/plugins/osd/Osd.qml:126): `PanelWindow`, camada overlay, nenhum foco e `mask: Region {}`;
- [Tray](/usr/share/omarchy/shell/plugins/bar/widgets/Tray.qml): host de itens da bandeja.

Esses links descrevem a instalação inspecionada; podem mudar após atualização do sistema.

## Fontes primárias e aplicação no projeto

### S1: conectoma e dinâmica neural

O modelo publicado usa dinâmica LIF, conectividade e previsões de neurotransmissores, com parâmetros e hipóteses adicionais. Os resultados incluem alimentação e limpeza antenal; não validam dez comportamentos de desktop. Serve de referência para o núcleo de simulação e para declarar a origem dos parâmetros. [Shiu e colaboradores, 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11446845/).

### S2: ajuste de redes com conectividade biológica

FlyVis ajusta propriedades desconhecidas de uma rede visual condicionada por conectividade para uma tarefa de movimento. É precedente para calibrar modelos, sem constituir evidência de que esconder-se ou retornar ao cursor emergirá do FlyWire. [Lappalainen e colaboradores, 2024](https://www.nature.com/articles/s41586-024-07939-3).

### S3: fuga e informação espacial

O estudo relaciona gradientes de conectividade visual à direção de fuga. Sustenta investigar LC4/LPLC2 e neurônios descendentes, preservando informação espacial. A saída desses neurônios ainda exige uma interpretação motora no nosso corpo 2D. [Synaptic gradients transform object location to action](https://www.nature.com/articles/s41586-022-05562-8).

### S4: imobilização dependente de contexto

Os experimentos associam controle descendente e velocidade prévia à imobilização defensiva. Justificam um cenário distinto de fuga e impedem tratar DNp09 como um indicador universal de medo. [Speed dependent descending control of freezing behavior, 2018](https://www.nature.com/articles/s41467-018-05875-1).

### S5: comandos descendentes recrutam redes

O trabalho mostra a importância da coativação de populações descendentes para comportamentos completos. A pesquisa ajuda a escolher candidatos de locomoção e grooming; localizar um tipo no CSV não demonstra que sua função esteja reproduzida. [Descending networks transform command signals into population motor control, 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11186778/).

### S6: acesso ao cursor e custo de consultas

O Hyprland documenta `cursorpos`, consultas de clientes/monitores e execução síncrona de `hyprctl`. Isso orienta o cache e o limite de consultas; as frequências no SPEC são propostas de benchmark. [Using hyprctl](https://wiki.hypr.land/Configuring/Advanced-and-Cool/Using-hyprctl/).

### S7: máscara de input e layer-shell no Quickshell

`QsWindow.mask` define a região de clique. `WlrLayershell` configura a camada da superfície. O recorte visual da mosca atrás de uma janela será implementado separadamente. [QsWindow](https://quickshell.org/docs/v0.3.0/types/Quickshell/QsWindow/) e [WlrLayershell](https://quickshell.org/docs/v0.3.0/types/Quickshell.Wayland/WlrLayershell/).

### S8: camadas não fornecem ordenação arbitrária entre janelas

O protocolo define camadas e deixa a ordem dentro de uma mesma camada indefinida. A oclusão simulada é uma decisão de projeto; posição real entre janelas exigiria outra integração. [Protocolo wlr-layer-shell](https://wayland.app/protocols/wlr-layer-shell-unstable-v1).

### S9: publicação e apresentação no systray

O Qt documenta `QSystemTrayIcon` e suporte a ambientes Linux com StatusNotifierItem. O serviço `SystemTray` do Quickshell expõe itens existentes. A proposta usa Qt para publicar e o Omarchy para apresentar o item. [QSystemTrayIcon](https://doc.qt.io/qt-6/qsystemtrayicon.html) e [SystemTray do Quickshell](https://quickshell.org/docs/v0.3.0/types/Quickshell.Services.SystemTray/SystemTray/).

### S10: eventos IPC do Hyprland

O socket de eventos informa mudanças de estado, mas não fornece todas as atualizações contínuas necessárias. `movewindow` informa mudança de workspace. O projeto combina invalidação por eventos e snapshots limitados. [IPC do Hyprland](https://wiki.hypr.land/IPC/).

### S11: BANC como possibilidade de expansão

Há publicação em 2026 de um conectoma que une cérebro e cordão nervoso ventral. Isso torna BANC uma linha de investigação relevante. A correspondência dos arquivos desta pasta com a publicação e a migração do modelo ainda precisam de auditoria. [Distributed control circuits across a brain-and-cord connectome](https://pubmed.ncbi.nlm.nih.gov/42259917/).

### S12: backend AMD e verificação de compatibilidade

PyTorch com HIP reaproveita nomes da API `torch.cuda`. A versão ROCm, os operadores e o dispositivo precisam ser verificados juntos; não foi confirmado suporte funcional da pilha instalada ao nosso modelo. A página da matriz AMD teve acesso limitado durante a consulta, portanto o plano não afirma certificação desta configuração. [Semântica HIP no PyTorch](https://docs.pytorch.org/docs/main/notes/hip.html) e [matrizes AMD](https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/docs/compatibility/compatibility.html).

### S13: alternativa de inferência com Vulkan compute

Vulkan oferece computação geral com buffers de armazenamento. Um worker neural próprio é tecnicamente uma rota de implementação, que exige kernels e sincronização a desenvolver e testar. O tutorial não fornece um simulador FlyWire pronto. [Documentação Khronos sobre compute shaders](https://docs.vulkan.org/tutorial/latest/11_Compute_Shader.html).

### S14: medição de trabalho assíncrono na GPU

A documentação de desempenho do CuPy explica aquecimento e medição com eventos/sincronização. O princípio orienta nosso benchmark; não implica escolher CuPy para a GPU AMD. [Performance best practices](https://docs.cupy.dev/en/stable/user_guide/performance.html).

## Lacunas que permanecem

Não foi encontrado nem demonstrado um modelo pronto que una dez respostas de desktop, os circuitos locais e GPU AMD. Também não foi validado o runtime com janelas em movimento, escala fracionária ou fullscreen. Faltam acesso funcional ao backend GPU, aferição de latência e definição do orçamento final.

Os IDs e caminhos completos de grooming e pouso ainda não foram auditados. A origem dos arquivos e suas licenças não foi estabelecida pelos nomes. Campos receptivos, parâmetros elétricos e comportamento do modelo são trabalho futuro. A arte pixel art e o ícone ainda não foram produzidos.

Os dois levantamentos de pesquisa contribuíram com a distinção entre circuito e política neural, a separação entre máscara de input e oclusão, e a necessidade de publicar um item de bandeja. As fontes não demonstram o produto completo; os tickets P0 existem para resolver essas lacunas. As medidas de desempenho e dimensões de arte nos documentos são metas propostas, não resultados observados.
