# FruitFly

Mosquinha experimental de desktop para Omarchy/Hyprland, com pixel art 2D e decisões comportamentais produzidas por uma rede neural que incorpora circuitos do FlyWire. A implementação prioriza baixo consumo; o circuito pequeno roda na CPU compilada e há uma prova comparativa na GPU.

Já existe um protótipo de fuga/exploração com ícone no systray e liga/desliga. Os dez comportamentos completos, os esconderijos e a instalação como plugin ainda não estão concluídos.

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
