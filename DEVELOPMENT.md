# Desenvolvimento

Guia para quem vai rodar, testar e contribuir com o PSE-Image. Visão geral do
projeto e como criar nós: [README.md](README.md).

- [Requisitos](#requisitos)
- [Configuração (uma vez)](#configuração-uma-vez)
- [Rodando](#rodando)
- [Testes e verificação](#testes-e-verificação)
- [Executável](#executável)
- [Fluxo de trabalho (git)](#fluxo-de-trabalho-git)
- [Arquitetura](#arquitetura)
- [Estendendo os cards](#estendendo-os-cards)
- [Problemas comuns](#problemas-comuns)

## Requisitos

- **Python 3.12** via [pyenv](https://github.com/pyenv/pyenv) (Windows:
  [pyenv-win](https://github.com/pyenv-win/pyenv-win)). A versão é fixada em `.python-version`.
- **Node.js 20+** e npm.
- git e, para PRs, o [GitHub CLI](https://cli.github.com/) (opcional).

## Configuração (uma vez)

```bash
pyenv install 3.12 --skip-existing
python --version                       # dentro da pasta do projeto: 3.12.x

python -m venv .venv                   # ambiente virtual (já ignorado pelo git)
source .venv/bin/activate              # a cada terminal (Windows: .venv\Scripts\activate)
pip install -r requirements.txt -r requirements-dev.txt

cd frontend && npm ci                  # dependências do frontend (package-lock.json)
```

Se `python --version` não mostrar 3.12, o pyenv não está ativo no shell:
adicione `eval "$(pyenv init - zsh)"` (ou `bash`) ao `~/.zshrc` / `~/.bashrc`,
ou crie o ambiente com `pyenv exec python -m venv .venv`.

Dependências novas: Python em `requirements.txt` (execução) ou
`requirements-dev.txt` (testes/build); frontend com `npm install <pacote>` dentro
de `frontend/` (atualiza o `package-lock.json`, que vai no commit).

## Rodando

Dois terminais, a partir da raiz do repositório. Suba o backend primeiro.

```bash
# terminal 1: backend (FastAPI) em http://127.0.0.1:8000
source .venv/bin/activate
python -m pse.api                      # outra porta: python -m pse.api 8001

# terminal 2: frontend (Vite) em http://localhost:5173
cd frontend
npm run dev
```

Abra **http://localhost:5173**. O Vite repassa `/api/*` para o backend
(`frontend/vite.config.ts`), então não há CORS. Mudanças no frontend recarregam
sozinhas; mudanças no backend exigem reiniciar o `python -m pse.api`.

O estado do fluxo fica na memória do backend: reiniciar o backend e recarregar
a página começa um fluxo vazio.

`python main.py` faz o mesmo que `python -m pse.api` (porta 8000) e é o ponto
de entrada do executável.

## Testes e verificação

Rode antes de abrir um PR:

```bash
python -m pytest                       # backend: grafo, contrato dos nós, API, workspace

cd frontend
npm test                               # vitest
npm run build                          # typecheck (tsc) + build em frontend/dist
```

- Todo nó novo em `pse/nodes/` precisa de testes em `tests/test_nodes.py` com
  matrizes pequenas calculadas à mão. O teste de contrato roda sozinho para todo nó.
- No frontend, funções puras ficam em `src/lib/` e ganham um `*.test.ts` ao lado.

## Executável

```bash
python build.py                        # PyInstaller: dist/PSE-Image
```

Hoje o executável empacota só o backend (`main.py`). Embutir o frontend
(build do React servido pelo FastAPI) é uma tarefa pendente.

## Fluxo de trabalho (git)

- **Nunca** faça commit direto na `main`. Uma branch por mudança, um PR por branch.
- Nome da branch: `<tipo>/<assunto>`, por exemplo `feat/node-complement`,
  `fix/upload-png`, `docs/development`.
- Commits em português, no formato `<tipo>: <descrição>`. Tipos: `feat`, `fix`,
  `refactor`, `docs`, `test`, `chore`, `perf`, `ci`.
- PRs pequenos. Se um PR depende de outro ainda aberto, abra-o com a branch do
  outro como base (PRs empilhados) e mescle em ordem.
- O PR descreve o que muda e como foi testado; testes e build passando.
- Nós novos (`pse/nodes/<nome>.py` + testes) quase nunca conflitam entre si:
  dá para trabalhar em vários ao mesmo tempo.

## Arquitetura

```
navegador (React + React Flow)
   │  fetch /api/*            (Vite repassa para o backend em desenvolvimento)
   ▼
FastAPI  pse/api/app.py       rotas, validação (schemas.py, values.py), upload (uploads.py)
   ▼
Workspace  pse/api/workspace.py   Graph persistente; ajusta-se ao fluxo enviado
   ▼
Graph / Node  pse/core/        execução em ordem topológica, cache por nó
   ▼
nós  pse/nodes/*.py            NODE = NodeSpec(...) + execute(inputs, params)
```

O frontend é dono do fluxo (blocos, posições, ligações, valores). A cada
mudança, ele envia o fluxo inteiro (`PUT /api/workflow`, com debounce de 150 ms);
o backend cria, remove e atualiza nós e ligações, executa só o que mudou e
devolve o estado de cada nó. Cada imagem tem uma `version`, que só muda quando
a imagem muda: o frontend usa `...png?v=<version>` para recarregar só as
miniaturas alteradas.

### API

| Rota | Função |
|---|---|
| `GET /api/health` | `{"ok": true}` |
| `GET /api/node-types` | Lista de `NodeSpec` em JSON: monta a paleta e os cards |
| `POST /api/images` | Upload de PNG (multipart, campo `file`, até 20 MB) → `{path, name, width, height}` |
| `PUT /api/workflow` | `{nodes: [{id, type, values}], links: [{src, src_port, dst, dst_port}]}` → `{nodes: {id: {error, status, outputs, preview}}, rejected_links}` |
| `GET /api/nodes/{id}/preview.png` | Imagem exibida no card (`NodeSpec.preview`) |
| `GET /api/nodes/{id}/outputs/{porta}.png` | Imagem de uma porta de saída |
| `POST /api/nodes/{id}/actions/{nome}` | Dispara um parâmetro `action` (ex.: Salvar) → estado do nó |

O backend só escuta em `127.0.0.1` e só aceita os Hosts `127.0.0.1` e `localhost`.
Erros de validação voltam como HTTP 422 com `detail`.

## Estendendo os cards

O card de cada bloco (`frontend/src/components/PseNodeView.tsx`) é montado a
partir do `NodeSpec` que vem de `GET /api/node-types`:

| Parte do card | Vem de |
|---|---|
| Título, tooltip na paleta, seção da paleta | `title`, `description`, `category` |
| Alças à esquerda / direita | `inputs` / `outputs` |
| Widgets | `params` (um widget por `Param.kind`) |
| Miniatura | entrada indicada em `preview` |
| Mensagem vermelha / verde | erro do nó (`NodeError`) / `"_status"` devolvido por `execute` |

Há três níveis de extensão, do mais comum ao mais raro.

### 1. Bloco novo: só Python

Crie `pse/nodes/<nome>.py` (veja [Criando um nó](README.md#criando-um-nó)).
O card aparece sozinho, com os widgets dos tipos de parâmetro existentes.
**Nenhuma mudança no frontend.**

### 2. Tipo de parâmetro novo (ex.: matriz de pesos da convolução)

Exemplo: um tipo `kernel`, cujo valor é uma matriz de números.

1. **`pse/core/node.py`**: documente o tipo na docstring de `Param`.
2. **`tests/test_nodes.py`**: adicione o tipo ao conjunto `KINDS` (o teste de
   contrato recusa tipos desconhecidos).
3. **`pse/api/values.py`**: trate o tipo em `_coerce` (valide forma, limites e
   tamanho). Sem isso, o backend responde 422 "tipo de parâmetro não suportado".
4. **`frontend/src/types.ts`**: adicione o tipo a `ParamKind`. Se o valor não for
   número, texto ou booleano, amplie `ParamValue` (ex.: `number[][]`).
5. **Widget**: um caso novo no `switch` de
   `frontend/src/components/params/ParamField.tsx` ou, para algo maior, um
   componente próprio em `components/params/` (ex.: `KernelEditor.tsx`) ligado
   em `renderParam` de `PseNodeView.tsx`. O widget recebe o valor atual e chama
   `onChange(novoValor)`; a sincronização com o backend é automática.

### 3. Elemento novo no card (miniaturas das saídas, botão de download, histograma)

Mexa em `PseNodeView.tsx` e `src/index.css`. O resultado de cada nó já está na
store (`useWorkflow((s) => s.results[id])`), com `outputs[porta]` =
`{version, width, height, channels}`. A URL da imagem de uma saída é
`/api/nodes/{id}/outputs/{porta}.png?v={version}`; crie um helper em
`src/api/client.ts`, como o `previewUrl`. Se precisar de um dado que o backend
ainda não envia, altere primeiro `pse/api/workspace.py` (`_state`) e depois
`NodeResult` em `types.ts`.

### Regras do frontend

- Todo controle dentro do card usa a classe `nodrag`; sem ela, mexer no
  controle arrasta o bloco.
- A store (`src/store/workflow.ts`) nunca é mutada: crie objetos novos (veja
  `withValue` e `withFile`).
- Textos da interface em português.
- `src/types.ts` espelha `pse/api/schemas.py`: mudou um, mude o outro.

## Problemas comuns

| Sintoma | Causa e solução |
|---|---|
| `[Errno 98] address already in use` | Já existe um backend (porta 8000) ou Vite (porta 5173) rodando. Feche-o (`lsof -i :8000` mostra o processo) ou use outra porta: `python -m pse.api 8001`. Com outra porta, ajuste o `target` em `frontend/vite.config.ts`. |
| Página mostra "Backend indisponível" | O backend não está rodando. Suba `python -m pse.api` e recarregue. |
| `ImportError: ... libcrypto.so.3: version 'OPENSSL_3.3.0' not found` | O Python do pyenv foi compilado com um OpenSSL mais novo que o do sistema. Reinstale apontando para ele: `LDFLAGS="-Wl,-rpath,$(brew --prefix openssl@3)/lib" pyenv install --force 3.12`. Paliativo: `export LD_LIBRARY_PATH=$(brew --prefix openssl@3)/lib` no terminal. |
| `pip` reclama que o módulo `ssl` não está disponível | Mesma causa da linha acima. |
| `python --version` não é 3.12 | O pyenv não está ativo no shell; veja [Configuração](#configuração-uma-vez). |
| Ligação fica vermelha e tracejada | O backend recusou a ligação; o motivo aparece no rótulo dela. |
