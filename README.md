# ICMS Antecipado - Piauí

Automação com **Playwright (Python assíncrono)** para o portal DAR Web da SEFAZ-PI. Interface gráfica para carregar Excel de filiais e executar o fluxo em lote por I.E.

---

## Passo a passo do processo manual que a automação substitui

1. Acessar no navegador o portal DAR Web da SEFAZ-PI (`https://webas.sefaz.pi.gov.br/darweb/faces/views/index.xhtml`).
2. Clicar no **Menu ICMS** e, na tela de seleção, escolher **113011 - ICMS – ANTECIPAÇÃO PARCIAL** e clicar em **Avançar**.
3. Informar a Inscrição Estadual (I.E.) no campo e clicar em **Avançar**.
4. No formulário "Cálculos do Imposto", preencher **período de referência** (MM/AAAA), **data de vencimento** e **data de pagamento** (ex.: dia 15 do mês de referência), **valor principal** (coluna ATC da planilha).
5. Clicar em **Calcular Imposto**.
6. Clicar em **Avançar** para seguir ao pagamento (quando aplicável).
7. Fazer o **download do comprovante** da guia DAR gerada (quando disponível).
8. **Renomear o arquivo** no padrão desejado (ex.: por I.E. e competência).
9. Repetir os passos 1 a 8 para cada I.E./filial (em geral a partir de uma planilha Excel com I.E.s, coluna **ATC** e período).

A automação replica esse fluxo por I.E., preenchendo os campos a partir do Excel. Envio do formulário após "Calcular Imposto", download do comprovante e renomeação automática estão nos planos futuros.

---

## Vídeo do processo manual

Quando aplicável, vídeo do processo manual para referência futura:

- **[Pasta com vídeos do processo manual (ICMS ATC PI, etc.)](https://drive.google.com/drive/folders/1lXeoZHH2d5bk2gXDSO87DxaoDQdNA748)**

---

## Vídeo da automação funcionando

Vídeo mostrando o bot em execução (carregando Excel, preenchendo o portal e rodando em lote):

- **A adicionar** (será incluído quando a automação completa estiver pronta).

---

## O que a automação faz

- Acessa o portal DAR Web da SEFAZ-PI (página inicial `index.xhtml`).
- Para cada I.E. da planilha: clica no **Menu ICMS**, seleciona **113011 - ICMS – ANTECIPAÇÃO PARCIAL**, clica em **Avançar**, preenche a **I.E.** e clica em **Avançar**, preenche **período de referência**, **data de vencimento**, **data de pagamento** (dia 15 do mês de referência), **valor principal** (coluna ATC), clica em **Calcular Imposto**.
- Permite carregar um Excel de filiais (coluna I.E. = INSC.ESTADUAL e coluna **ATC**), visualizar os dados extraídos, escolher quais I.E. executar e rodar o fluxo em lote.
- Trata **datas passadas**: se a data de vencimento (dia 15 do mês de referência) já passou, a I.E. é ignorada e registrada com motivo "Data de vencimento no passado — portal não permite datas passadas".
- Em erro: registra log e salva screenshot na pasta de erros configurada.

## Planos futuros (a implementar)

- Assim que houver **nova planilha** com a etapa final definida, implementar o clique em **Avançar** após \"Calcular Imposto\" para ir ao passo de pagamento.
- Automatizar o **download do boleto/comprovante** gerado após o Avançar final.
- Fazer a **renomeação automática** dos arquivos (ex.: por I.E. e competência), **organizar em pastas** e devolver o pacote pronto para o usuário.
- Gravar o **vídeo da automação completa** (incluindo download, renomeação e organização) e adicionar o link na seção acima.
- Empacotar toda a automação em um executável (ex.: PyInstaller/Nuitka) para distribuição sem exigir instalação de Python.

---

## Regras de negócio

### Contexto

- **DAR** = Documento de Arrecadação: é a guia de pagamento que a empresa usa para pagar tributos no Piauí (como o ICMS).
- **ICMS Antecipado (113011)** = receita de antecipação parcial do ICMS que empresas precisam declarar e pagar à SEFAZ-PI.
- Na prática, quem tem várias **filiais** (cada uma com uma Inscrição Estadual — I.E.) precisa gerar **uma DAR por filial**, por período, no portal da SEFAZ-PI. O valor a recolher vem da coluna **ATC** da planilha de apuração.

### O que o bot faz na prática

- Você já tem uma **planilha Excel** de apuração de ICMS (típica de "APURAÇÃO DE ICMS PIAUÍ") com as filiais, o período (mês/ano) e o **valor ATC** (valor principal) de cada uma.
- O bot **lê essa planilha** e, para cada filial que tem valor ATC a pagar:
  - Acessa o portal DAR Web da SEFAZ-PI.
  - Seleciona o código **113011 - ICMS – ANTECIPAÇÃO PARCIAL** e avança.
  - Informa a I.E. da filial e avança.
  - Preenche **período de referência** (mês/ano da planilha), **data de vencimento** e **data de pagamento** (dia 15 do mês de referência) e **valor principal** (coluna ATC).
  - Clica em **Calcular Imposto**.
- I.E.s cuja data de vencimento já está no passado são **puladas** e listadas com motivo claro (portal não aceita datas passadas).
- Ou seja: o bot **replica no site** o que está na planilha, filial a filial, sem você precisar digitar cada I.E. e cada valor manualmente.

---

## Dependências

- **Python** 3.13+
- **Pacotes Python** (na raiz do projeto):
  ```bash
  pip install -r requirements.txt
  ```
  Inclui: `playwright`, `openpyxl`, `customtkinter`, `python-dotenv`.
- **Navegador Playwright** (Chromium):
  ```bash
  python -m playwright install chromium
  ```

O projeto pode ser executado diretamente pelo Python via módulo ou, preferencialmente, via comando instalado (`icms-atc-pi`).

### Instalação em modo editável (recomendado para uso diário)

Na raiz do projeto:

```powershell
pip install -e .
```

Após instalar, o comando padrão fica:

```powershell
icms-atc-pi
```

Se preferir rodar sem instalar, ainda é possível usar o módulo diretamente. No PowerShell, na raiz do projeto:

```powershell
$env:PYTHONPATH="src"
python -m sefaz_pi.gui_app
```

---

## Variáveis de ambiente necessárias

Copie `.env.example` para `.env` e preencha conforme necessário:

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `PASTA_SAIDA_RESULTADOS` | Não | Pasta para resultados (padrão: `resultados`). |
| `PASTA_CAPTURAS_DE_TELA_ERROS` | Não | Pasta para screenshots em caso de erro (padrão: `capturas_erros`). |

**Não commitar o arquivo `.env`.**

---

## Como executar

### Interface gráfica (Excel + lote)

1. No PowerShell, na raiz do projeto, execute:
   ```powershell
   $env:PYTHONPATH="src"
   python -m sefaz_pi.gui_app
   ```
2. Selecione um arquivo `.xlsx` com coluna de Inscrição Estadual (ex.: "INSC.ESTADUAL") e coluna **ATC**.
3. Use **Ver dados extraídos** para conferir a extração.
4. Use **Escolher IEs e executar** ou **Executar todas executáveis** para rodar a automação.

### Só automação (linha de comando)

Execute diretamente no PowerShell:
  ```powershell
  $env:PYTHONPATH="src"
  python -m sefaz_pi.main --excel "C:\caminho\para\icms.xlsx"
  $env:PYTHONPATH="src"
  python -m sefaz_pi.main --excel "C:\caminho\para\icms.xlsx" --headless
  ```

**Planilha Excel:** Cabeçalho com coluna de I.E. (ex.: "INSC.ESTADUAL") e coluna **ATC** (valor principal); dados lidos até a linha de TOTAL ou até a primeira I.E. vazia. Período de referência extraído da área do título (mês/ano). I.E. aceita formato com pontos e traço; é normalizada para 9 dígitos. Suporte a planilhas no formato **APURAÇÃO DE ICMS PIAUI**.

**Logs:** Terminal em INFO+; arquivo em `logs/` em DEBUG+.

---

## Estrutura do projeto

| Pasta/Arquivo | Função |
|---------------|--------|
| **`pyproject.toml`** | Metadados do projeto (nome, versão). |
| **`requirements.txt`** | Dependências para `pip install -r requirements.txt`. |
| **`.env`** | Variáveis sensíveis. **Não commitar.** |
| **`.env.example`** | Exemplo do `.env` sem valores reais. |
| **`logs/`** | Criada automaticamente; arquivos `.log` com timestamp. |
| **`src/sefaz_pi/main.py`** | Ponto de entrada CLI; GUI (padrão) ou lote com `--excel`; suporta `--headless`. |
| **`src/sefaz_pi/gui_app.py`** | Interface gráfica (CustomTkinter): upload Excel, extração I.E./ATC, execução em lote. |
| **`src/sefaz_pi/automacao_sefaz_pi.py`** | Classe principal `AutomacaoAntecipacaoParcialPI`; orquestra o fluxo por I.E. |
| **`src/sefaz_pi/configuracoes.py`** | Carrega `.env`; URLs, seletores, timeouts, pastas. |
| **`src/sefaz_pi/excel_filiais.py`** | Extração de dados do Excel (formato ICMS/filiais, coluna ATC). |
| **`src/sefaz_pi/logger.py`** | Logging: terminal INFO+, arquivo DEBUG+ em `logs/`. |
| **`src/sefaz_pi/navegacao/`** | Ações atômicas na página (aguardar, preencher data/valor mascarado, screenshot em erro). |
