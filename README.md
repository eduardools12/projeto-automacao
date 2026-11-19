# 🛒 Automação de Coleta e Comparação de Preços

Automação em Python que pesquisa um produto na **Amazon** e no **Magazine Luiza**, coleta nome, preço, avaliação e link de cada resultado, trata os dados e gera um **relatório em Excel**. Cada execução também é guardada em um **histórico de preços**, então, rodando todo dia, dá para acompanhar como o preço muda.

```text
Selenium (coleta)  →  tratamento (Regex, texto → número)  →  histórico (CSV)  →  relatório (Excel)
```

## O que o relatório traz

Um único arquivo `.xlsx`, com uma aba para cada análise:

| Aba | Conteúdo |
|---|---|
| **Produtos** | Todos os produtos coletados, do mais barato ao mais caro |
| **Resumo** | Total coletado, mais barato, mais caro e preço médio por loja |
| **Faixas de preço** | Cada produto comparado a um valor de referência (opcional: `--valor-base`) |
| **Filtrados** | Produtos que passaram nos filtros de preço, nota, loja e marca (opcional) |
| **Histórico** | Menor preço e preço médio por loja em cada execução anterior |

Os preços ficam salvos como número, formatados em reais, então dá para somar, filtrar e montar gráficos direto no Excel.

## Como funciona

1. Abre o Chrome (o Selenium baixa o ChromeDriver certo sozinho).
2. Busca o produto em cada loja e espera os cards carregarem (`WebDriverWait`).
3. Lê os dados de cada card com seletores CSS. Se o seletor do preço ou da avaliação falha, usa um **plano B com Regex** no texto do card.
4. Converte o preço de texto ("R$ 1.299,90") para número (1299.9) e calcula o resumo.
5. Acrescenta os preços ao `historico_precos.csv` e gera o relatório.

Se uma loja falhar (site fora do ar, demora, mudança de layout), o erro é registrado no log e a automação continua com a outra.

## Instalação

```bash
git clone https://github.com/eduardools12/projeto-automacao.git
cd projeto-automacao
python -m venv venv
venv\Scripts\activate          # Windows  (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
```

Precisa do Python 3.10 ou mais novo e do Google Chrome instalado.

## Como usar

```bash
# Busca simples nas duas lojas
python main.py "fone bluetooth"

# Com faixas de preço e filtros
python main.py "fone bluetooth" --valor-base 300 --nota-min 4 --marca jbl

# Só na Magalu, 10 produtos, sem abrir a janela do navegador
python main.py "air fryer" --lojas magalu --limite 10 --headless
```

Os arquivos vão para a pasta `relatorios/`. Todas as opções: `python main.py --help`.

| Opção | Para que serve |
|---|---|
| `--lojas` | Onde buscar: `amazon`, `magalu` (padrão: as duas) |
| `--limite` | Máximo de produtos por loja (padrão: 20) |
| `--valor-base` | Valor de referência para a aba de faixas de preço |
| `--preco-min`, `--nota-min`, `--loja`, `--marca` | Filtros da aba Filtrados |
| `--saida` | Pasta dos relatórios (padrão: `relatorios`) |
| `--headless` | Roda sem abrir a janela do navegador |

## Rodar todo dia automaticamente (Windows)

Como a automação não pede nada durante a execução, ela pode ser agendada. No **Agendador de Tarefas** do Windows, crie uma tarefa diária com:

- **Programa:** caminho do `python.exe` dentro da pasta `venv\Scripts`
- **Argumentos:** `main.py "fone bluetooth" --headless`
- **Iniciar em:** a pasta do projeto

A cada dia, a aba **Histórico** do novo relatório mostra a evolução do preço.

## Testes

```bash
pip install -r requirements-dev.txt
python -m pytest
```

Os testes cobrem o tratamento dos dados, o histórico, o relatório e o fluxo completo do `main.py` com um navegador falso, ou seja, rodam sem internet.

## Estrutura

```text
projeto-automacao/
├── main.py                 # linha de comando: lê as opções e conduz o fluxo
├── comparador/
│   ├── coleta.py           # Selenium: navegador e leitura dos cards de cada loja
│   ├── tratamento.py       # conversão de preço e nota, resumo, faixas e filtros
│   ├── historico.py        # histórico de preços em CSV
│   └── relatorio.py        # relatório em Excel (openpyxl)
├── tests/                  # testes automatizados (pytest)
├── requirements.txt
└── requirements-dev.txt
```

## Limitações

- Os seletores dependem do layout dos sites. Se a Amazon ou a Magalu mudarem a página, a coleta daquela loja precisa ser ajustada.
- Projeto feito para estudo. Use com moderação e respeite os termos de uso de cada site.

## Possíveis melhorias

- Guardar o histórico em um banco de dados (SQLite ou PostgreSQL)
- Dashboard com a evolução dos preços
- Alerta por e-mail quando o preço cair abaixo de um valor

## Autor

Eduardo Gonçalves Dutra · [github.com/eduardools12](https://github.com/eduardools12)
