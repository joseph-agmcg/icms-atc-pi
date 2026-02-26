# ICMS-PI — Automação SEFAZ-PI

Automação para processos de **ICMS** no portal DAR Web da SEFAZ-PI: **ATC** (Antecipado), **Normal** e **Difal**.

---

## Visão geral

- **Interface gráfica** (CustomTkinter): carregar planilha Excel, visualizar I.E.s e valores, selecionar quais executar e rodar em lote.
- **Planilha**: colunas de Inscrição Estadual e ATC; extração automática de período e dados para DAR.
- **Processos**: ATC (113011) em uso; Normal e Difal em desenvolvimento.

---

## Estrutura do projeto

| Pasta/Arquivo | Função |
|---------------|--------|
| **`pyproject.toml`** | Metadados do projeto (nome, versão, entrypoint `icms_pi`). |
| **`requirements.txt`** | Dependências para `pip install -r requirements.txt`. |
| **`.env`** | Variáveis sensíveis. **Não commitar.** |
| **`.env.example`** | Exemplo do `.env` sem valores reais. |
| **`logs/`** | Criada automaticamente; arquivos `.log` com timestamp. |
| **`src/icms_pi/`** | Comando central: GUI, extração Excel e logger; orquestra ATC, Normal e Difal. |
| **`src/atc/`** | Automação do ICMS Antecipado (código 113011). |
| **`src/normal/`** | ICMS Normal — em construção. |
| **`src/difal/`** | ICMS Difal — em construção. |

---

## Documentação por módulo

| Módulo | Descrição | README |
|--------|-----------|--------|
| **ATC** (Antecipado) | Fluxo 113011 no DAR Web, passo a passo e automação. | [→ `src/atc/README.md`](src/atc/README.md) |
| **Normal** | ICMS Normal PI. | [→ `src/normal/README.md`](src/normal/README.md) |
| **Difal** | ICMS Difal PI. | [→ `src/difal/README.md`](src/difal/README.md) |

---

## Como rodar

1. Configurar `.env` a partir de `.env.example`.
2. Instalar dependências: `pip install -r requirements.txt` (ou `pip install -e .`).
3. Abrir a GUI:
   ```bash
   python -m icms_pi.gui_app
   ```
   Com o projeto instalado em modo editável (`pip install -e .`), também: `icms_pi`.
4. Na interface: selecionar a planilha Excel, revisar I.E.s e executar o processo desejado (ATC, Normal ou Difal).
