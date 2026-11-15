# PSE-Image

Ambiente gráfico para montar fluxos de processamento de imagens com blocos (Dear PyGui).

## Rodar

A versão do Python é fixada pelo [pyenv](https://github.com/pyenv/pyenv) no
arquivo `.python-version` (3.12). As dependências ficam em `requirements*.txt`
e são instaladas num ambiente virtual `.venv` criado com esse Python.

```bash
pyenv install 3.12 --skip-existing   # uma vez (Windows: pyenv-win)
python --version                     # dentro da pasta do projeto: 3.12.x
python -m venv .venv                 # uma vez
source .venv/bin/activate            # a cada terminal (Windows: .venv\Scripts\activate)
pip install -r requirements.txt -r requirements-dev.txt
python main.py
python -m pytest                     # testes
python build.py                      # executável em dist/PSE-Image
```

Se `python --version` não mostrar 3.12, o pyenv não está ativo no shell:
adicione `eval "$(pyenv init - zsh)"` (ou `bash`) ao `~/.zshrc` / `~/.bashrc`,
ou crie o ambiente com `pyenv exec python -m venv .venv`.

## Estrutura

```
pse/
  core/    NodeSpec/Param (esqueleto do nó), Node, Graph (execução em ordem topológica)
  nodes/   UM ARQUIVO POR NÓ — descobertos automaticamente e exibidos na paleta
    _template.py   modelo para copiar (arquivos com "_" no início são ignorados)
    read_png.py      Ler PNG (imagem colorida, RGB)
    to_grayscale.py  Escala de Cinza
    display.py       Exibir (cinza ou RGB)
    save_png.py      Salvar PNG (cinza ou RGB)
  ui/      Dear PyGui: paleta + canvas; gerado a partir dos NodeSpec
tests/     testes do grafo + teste de contrato que valida todo arquivo de nó
assets/    fonte com acentos (DejaVu Sans)
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

Não precisa registrar nada: o arquivo aparece na paleta ao abrir o app, e o
`build.py` o inclui no executável. Rode `pytest`: o teste de contrato
valida o esqueleto de todo nó.

Imagens: cinza = `(altura, largura)`, colorida = `(altura, largura, 3)`, sempre
`uint8`. Os nós de processamento devem usar `require_gray` (o TP trabalha em tons
de cinza); para aceitar as duas, use `require_image`.

Regra do TP: nada de métodos prontos (OpenCV, `scipy.ndimage`, `PIL.ImageFilter`...).
Pillow só para ler/gravar PNG.

Tipos de parâmetro: `int`, `float` (sliders), `choice` (combo, com `choices=(...)`),
`bool`, `text`, `dir` (texto + seletor de pasta), `file_open`, `file_save` e
`action` (botão: ao clicar, `execute` roda uma vez com `params[nome] = True`).
`execute` pode devolver `"_status": "mensagem"` para mostrar um aviso verde no nó.
Para algo especial, como a matriz de pesos da
convolução, adicione um tipo novo em `App._param_widget` (`pse/ui/app.py`).

## Comportamento

- Cada mudança (ligação, parâmetro, arquivo) reavalia o fluxo; um nó só executa
  de novo se suas entradas ou parâmetros mudaram.
- Uma entrada aceita uma única ligação; uma saída pode alimentar vários blocos.
- Ligações que formariam ciclo são ignoradas.
- `Exibir` e `Salvar PNG` repassam a imagem, então podem ficar no meio do fluxo.
- `Salvar PNG` grava ao clicar em **Salvar**: `<Caminho>/<Nome>.png`. Caminho vazio =
  `./img` na raiz do projeto (no executável, ao lado do `.exe`); caminho relativo
  também parte da raiz. Arquivo existente é sobrescrito.

## Pendente (obrigatórios do TP)

- [x] Leitura PNG, conversão para cinza (nós separados), Exibição, Gravação
- [ ] Processamento pontual (brilho/contraste)
- [ ] Convolução com máscara parametrizável + máscaras conhecidas (média, mediana, Laplaciano)
- [ ] Segmentação
- [ ] Diferença entre imagens
- [ ] Operação morfológica (operação + elemento estruturante)
- [ ] Complemento
