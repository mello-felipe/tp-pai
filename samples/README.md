# Base de imagens

Imagens de teste do PSE-Image (256×256, PNG). São sintéticas e reproduzíveis:
`python scripts/generate_samples.py` gera todas de novo, idênticas (semente fixa).

| Imagem | Conteúdo | Blocos para testar |
|---|---|---|
| `colorida.png` | Formas coloridas (RGB) | Ler PNG + Escala de Cinza |
| `gradiente.png` | Degradê horizontal de 0 a 255 | Brilho/contraste, Complemento |
| `baixo_contraste.png` | Formas com tons entre 100 e 150 | Brilho/contraste |
| `ruido_gaussiano.png` | Formas + ruído gaussiano (σ = 25) | Convolução: Média, Gaussiana |
| `ruido_sal_pimenta.png` | Formas + 10% de pixels pretos/brancos | Convolução: Mediana |
| `xadrez.png` | Tabuleiro 32×32 | Convolução: Laplaciano, Sobel |
| `formas_binarias.png` | Formas brancas com buracos e pontos soltos | Segmentação, Morfologia (abertura e fechamento) |
| `cena_a.png`, `cena_b.png` | Mesma cena; em `b` um círculo mudou de lugar e há um objeto novo | Diferença entre imagens |

Fotos reais também podem ser usadas: qualquer PNG funciona no bloco Ler PNG.
