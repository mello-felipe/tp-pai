# PSE-Image

*Problem-Solving Environment* para processamento de imagens (TP de Processamento
e Análise de Imagens, PUC Minas). O usuário monta fluxos de processamento
ligando blocos num canvas, sem programar, parametriza os blocos e vê o
resultado de cada etapa.

- **Interface:** web, em React + [React Flow](https://reactflow.dev) (`frontend/`).
- **Backend:** Python + FastAPI (`pse/api/`), que executa o grafo de blocos (`pse/core/`, `pse/nodes/`).

## Início rápido

Requisitos: [pyenv](https://github.com/pyenv/pyenv) (Python 3.12) e Node.js 20+.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python -m pse.api                          # terminal 1: backend em 127.0.0.1:8000

cd frontend && npm ci && npm run dev       # terminal 2: abra http://localhost:5173
```

Passo a passo, testes, fluxo de git e problemas comuns: **[DEVELOPMENT.md](DEVELOPMENT.md)**.

## Documentação

| Arquivo | Para quê |
|---|---|
| [DEVELOPMENT.md](DEVELOPMENT.md) | Rodar, testar, contribuir, arquitetura, API e como estender os cards |
| [frontend/AGENTS.md](frontend/AGENTS.md) | Regras para agentes de IA (Claude Code, Codex...) que mexem **só** no frontend |

## Estrutura

```
pse/
  core/      NodeSpec/Param (esqueleto do nó), Node, Graph (execução em ordem topológica)
  nodes/     UM ARQUIVO POR NÓ, descoberto automaticamente e exibido na paleta
    _template.py     modelo para copiar (arquivos com "_" no início são ignorados)
    read_png.py      Ler PNG (imagem colorida, RGB)
    to_grayscale.py  Escala de Cinza
    display.py       Exibir (cinza ou RGB)
    save_png.py      Salvar PNG (cinza ou RGB)
  api/       backend FastAPI: rotas, validação, workspace (grafo persistente), upload
frontend/    React + Vite + React Flow + zustand
  src/
    api/          chamadas HTTP ao backend
    components/   paleta, canvas, card do bloco (PseNodeView) e widgets de parâmetro
    hooks/        sincronização do fluxo com o backend
    lib/          funções puras (com testes)
    store/        estado do fluxo (zustand)
tests/       testes do backend: grafo, contrato dos nós, API, workspace
main.py      ponto de entrada: sobe o backend (usado pelo executável)
```

## Criando um nó

Copie `pse/nodes/_template.py` para `pse/nodes/<nome>.py` (snake_case: o Python
não importa nomes com hífen). Todo nó tem o mesmo esqueleto, em duas partes:

```python
# ===== DEFINIÇÃO (como a "description" de um nó do n8n) =====
NODE = NodeSpec(
    title="Limiarização",
    category="Segmentação",           # vira uma seção na paleta
    description="Tooltip da paleta.",
    inputs=("imagem",),
    outputs=("binária", "máscara"),   # quantas saídas quiser
    params=(Param("t", "Limiar", "int", 128, 0, 255),),
)

# ===== EXECUÇÃO (como o execute.ts do n8n): o algoritmo fica aqui =====
def execute(inputs: dict, params: dict) -> dict:
    img = require_gray(inputs, "imagem")  # uint8 2D; mostra erro no nó se
                                          # desconectada ou colorida
    ...
    return {"binária": a, "máscara": b}
```

Não precisa registrar nada nem mexer no frontend: o arquivo aparece na paleta
e o card é montado a partir do `NodeSpec`. O `build.py` inclui o nó no
executável. Rode `pytest`: o teste de contrato valida o esqueleto de todo nó.

Imagens: cinza = `(altura, largura)`, colorida = `(altura, largura, 3)`, sempre
`uint8`. Os nós de processamento devem usar `require_gray` (o TP trabalha em tons
de cinza); para aceitar as duas, use `require_image`.

Regra do TP: nada de métodos prontos (OpenCV, `scipy.ndimage`, `PIL.ImageFilter`...).
Pillow só para ler/gravar PNG.

Tipos de parâmetro: `int`, `float` (sliders), `choice` (select, com `choices=(...)`),
`bool`, `text`, `dir` (texto), `file_open` (envio de PNG), `file_save` e
`action` (botão: ao clicar, `execute` roda uma vez com `params[nome] = True`).
`execute` pode devolver `"_status": "mensagem"` para mostrar um aviso verde no nó.
Para algo especial, como a matriz de pesos da convolução, crie um tipo novo:
veja [Estendendo os cards](DEVELOPMENT.md#estendendo-os-cards).

## Comportamento

- Cada mudança (ligação, parâmetro, arquivo) reavalia o fluxo; um nó só executa
  de novo se suas entradas ou parâmetros mudaram. Mover blocos não reavalia.
- Uma entrada aceita uma única ligação (a nova substitui a antiga); uma saída
  pode alimentar vários blocos.
- Ligações que formariam ciclo são bloqueadas no canvas e recusadas pelo backend.
- `Exibir` e `Salvar PNG` repassam a imagem, então podem ficar no meio do fluxo.
- `Salvar PNG` grava ao clicar em **Salvar**: `<Caminho>/<Nome>.png`. Caminho vazio =
  `./img` na raiz do projeto (no executável, ao lado do `.exe`); caminho relativo
  também parte da raiz. Arquivo existente é sobrescrito.

## Pendente (obrigatórios do TP)

- [x] Leitura PNG, conversão para cinza (nós separados), Exibição, Gravação
- [x] Processamento pontual (brilho/contraste)
- [ ] Convolução com máscara parametrizável + máscaras conhecidas (média, mediana, Laplaciano)
- [ ] Segmentação
- [x] Diferença entre imagens
- [ ] Operação morfológica (operação + elemento estruturante)
- [x] Complemento
- [ ] Executável com o frontend embutido, base de imagens, manual e vídeo
