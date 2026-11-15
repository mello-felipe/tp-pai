# AGENTS.md — frontend do PSE-Image

Instruções para agentes de IA (Claude Code, Codex, Cursor...) que trabalham em
`frontend/`. O escopo deste arquivo é **somente o frontend**.

## Escopo

- Edite apenas arquivos dentro de `frontend/`.
- **Não** edite `pse/`, `tests/`, `requirements*.txt` nem arquivos da raiz.
- `src/types.ts` espelha o contrato da API (`pse/api/schemas.py` e
  `pse/api/workspace.py`). Se a tarefa precisar de um dado ou rota que o backend
  não oferece, **pare e descreva a mudança de backend necessária** em vez de
  inventar campos no frontend ou alterar o backend.
- Blocos novos (nós de processamento) são feitos em Python, em `pse/nodes/`, e
  aparecem no frontend sem mudança nenhuma. Não crie blocos no frontend.

## Stack

React 19, TypeScript (strict), Vite, [React Flow](https://reactflow.dev)
(`@xyflow/react` v12) e zustand. Sem biblioteca de UI: estilos em `src/index.css`
com as variáveis de `:root`.

## Comandos (dentro de `frontend/`)

```bash
npm ci              # instalar dependências
npm run dev         # servidor de desenvolvimento (precisa do backend: python -m pse.api)
npm test            # vitest
npm run typecheck   # tsc
npm run build       # typecheck + build
```

Antes de terminar qualquer tarefa: `npm run typecheck`, `npm test` e
`npm run build` precisam passar.

## Mapa do código

| Caminho | Conteúdo |
|---|---|
| `src/App.tsx` | Carrega os tipos de nó, liga a sincronização, monta paleta + canvas |
| `src/api/client.ts` | Única camada que chama `fetch`; helpers de URL de imagem |
| `src/types.ts` | Tipos do contrato com o backend |
| `src/store/workflow.ts` | Store zustand: tipos, nós, ligações, resultados; helpers imutáveis |
| `src/hooks/useWorkflowSync.ts` | `PUT /api/workflow` com debounce quando o fluxo muda |
| `src/components/Palette.tsx` | Paleta por categoria; arrastar ou clicar para adicionar |
| `src/components/Canvas.tsx` | React Flow: drop, ligações, bloqueio de ciclos, ligações recusadas |
| `src/components/PseNodeView.tsx` | O card do bloco (tipo de nó `pse` no React Flow) |
| `src/components/params/` | Widgets de parâmetro: `ParamField`, `FileField`, `ActionButton` |
| `src/lib/` | Funções puras, cada uma com `*.test.ts` |

## Como o card é montado

Tudo vem do `NodeSpec` (`GET /api/node-types`): `title`, `inputs` e `outputs`
(alças), `params` (um widget por `kind`) e `preview` (miniatura). O resultado da
execução fica em `useWorkflow((s) => s.results[id])`: `error` (vermelho),
`status` (verde), `preview` e `outputs` com `{version, width, height, channels}`.

## Receitas

### Widget para um tipo de parâmetro

1. Confirme que o backend já aceita o tipo (`pse/api/values.py`, função `_coerce`).
   Se não aceita, pare e avise: é mudança de backend.
2. Adicione o tipo a `ParamKind` em `src/types.ts`. Se o valor não for número,
   texto ou booleano, amplie `ParamValue`.
3. Widget simples: um `case` novo em `src/components/params/ParamField.tsx`.
   Widget maior: um componente em `src/components/params/` (ex.: `KernelEditor.tsx`)
   chamado em `renderParam` de `PseNodeView.tsx`.
4. O widget recebe o valor e chama `onChange(novoValor)`. Não chame a API: a
   sincronização acontece sozinha quando a store muda.
5. Lógica não trivial (ex.: redimensionar uma matriz) vai para `src/lib/` com teste.

### Elemento novo no card

1. Edite `PseNodeView.tsx` e `src/index.css`.
2. Use dados que já estão em `results[id]`. URL de imagem sempre por helper em
   `src/api/client.ts`, com `?v=<version>` para o cache funcionar.
3. Se o dado não existe na resposta da API, pare e avise (mudança de backend).

## Convenções obrigatórias

- **Imutabilidade:** nunca mute a store nem objetos dela. Crie objetos novos
  (veja `withValue`, `withFile`, `connectEdge` em `src/store/workflow.ts`).
- **`nodrag`:** todo controle interativo dentro do card tem a classe `nodrag`.
- **Tipo de nó:** os nós do React Flow usam `type: "pse"`. Não use o tipo
  `default`: ele aplica estilos próprios ao invólucro do card.
- **Textos da interface em português** (rótulos, mensagens, `title`, `alt`).
- **Sem `console.log`.** Erros aparecem na interface (banner ou mensagem no card).
- **Chamadas HTTP só em `src/api/client.ts`.**
- **Testes:** toda função nova em `src/lib/` ou helper da store ganha teste
  (vitest, `*.test.ts` ao lado do arquivo).
- **Arquivos pequenos e focados**; componentes com mais de ~200 linhas devem
  ser divididos.
- **Dependências:** não adicione pacotes sem necessidade clara; se adicionar,
  `package-lock.json` vai no mesmo commit.

## Git

Uma branch por mudança (ex.: `feat/kernel-editor`), PR para a `main`, commits em
português no formato `<tipo>: <descrição>` (`feat`, `fix`, `refactor`, `docs`,
`test`, `chore`). Detalhes em `../DEVELOPMENT.md`.
