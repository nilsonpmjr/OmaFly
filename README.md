# FruitFly (Versão Experimental)

<p align="center">
  <img src="assets/fly.svg" width="128" alt="FruitFly">
</p>

Mosquinha experimental de desktop para Omarchy/Hyprland, com pixel art 2D e decisões comportamentais produzidas por uma rede neural que incorpora circuitos do FlyWire. A implementação prioriza baixo consumo; o circuito pequeno roda num núcleo nativo compilado para CPU, com prova comparativa na GPU já validada.

## Status Atual
O projeto encontra-se atualmente na fase de protótipo de viabilidade (V0.2). 
- **O que já funciona:** Há um protótipo de fuga e exploração (com rede neural funcional), interface visual em PySide6/QML, controle por ícone na bandeja do sistema (systray) e núcleo C++ otimizado (baixo impacto na CPU). Existe também uma prova de conceito funcional de oclusão visual (esconder-se atrás de janelas).
- **O que falta:** O catálogo completo das 10 respostas comportamentais, integração da detecção de abrigos nas decisões neurais da mosca e a instalação automática/empacotamento como plugin nativo no Omarchy.

## Visão Futura
O plano para a versão de lançamento (M3/V1.0) engloba testar e integrar todas as 10 respostas simultaneamente. Após a V1, há expansões planejadas (P2) que incluem novas respostas a ameaças visuais e CO2 virtual, rastreabilidade precisa com o banco de dados (BANC/FlyWire) e um sistema aprimorado de persistência neural entre inicializações.

Para preparar e executar no checkout:

```sh
python tools/build.py
python tools/build_assets.py
python tools/extract.py
./run.sh run
```

O comando abre somente o ícone; ligue a mosca pelo menu ou com `./run.sh enable`. `./run.sh disable` suspende a simulação e remove a sobreposição; `./run.sh quit` encerra a instância. Consulte [execução, testes e limites](docs/IMPLEMENTATION.md).

| Documento | Uso |
|---|---|
| [PRD](docs/PRD.md) | Experiência, requisitos, dez respostas comportamentais e prioridades de produto. |
| [Especificação técnica](docs/SPEC.md) | Arquitetura proposta, contratos e provas de viabilidade; entrega de `/to-spec`. |
| [TODO e tickets](docs/TODO.md) | Trabalho ordenado, dependências e critérios de aceite; entrega de `/to-tickets`. |
| [Evidências e limites](docs/RESEARCH.md) | Inspeção local, fontes consultadas e questões ainda sem confirmação. |
| [Implementação](docs/IMPLEMENTATION.md) | Como executar, proteções de consumo e o que ainda falta. |

Os comandos `/to-spec` e `/to-tickets` foram interpretados como entregáveis documentais locais. Não houve publicação de tickets em um serviço externo.
