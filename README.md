# 🧪 Gerador de Arquivos de Teste

Aplicação desktop desenvolvida em **Python** para geração de arquivos de teste com extensão e tamanho definidos.

O projeto foi criado com foco em atividades de **Quality Assurance (QA)**, principalmente para cenários que exigem testes de upload, limite de tamanho, formatos de arquivos e validações de comportamento.

---

## 🎯 Objetivo

Facilitar a criação de massas de arquivos para testes, reduzindo a necessidade de buscar arquivos na internet ou utilizar ferramentas externas.

A aplicação permite gerar arquivos de diferentes extensões e tamanhos de forma rápida e controlada.

---

## 🚀 Funcionalidades

- Geração de arquivos com tamanho definido.
- Suporte a KB, MB e GB.
- Geração individual por extensão.
- Geração em lote para todas as extensões.
- Criação automática do nome do arquivo.
- Evita sobrescrever arquivos existentes.
- Seleção do diretório de destino.
- Interface gráfica desktop.
- Aplicação empacotada como executável para Windows.

### Formatos disponíveis

- PNG
- JPG
- JPEG
- PDF
- MP4
- M4A
- OGG

---

## 🖥️ Tecnologias

- Python 3.13
- Tkinter
- Pillow
- PyInstaller

---

## 📸 Interface

A aplicação possui uma interface gráfica desenvolvida em Tkinter, com capa personalizada, painel de configuração e atalhos para os perfis profissionais da autora.
<img width="1128" height="864" alt="image" src="https://github.com/user-attachments/assets/37e21135-0737-4fea-85d0-2890992c0dbc" />
<img width="1122" height="847" alt="image" src="https://github.com/user-attachments/assets/445add7b-cedb-4d04-890b-4e30b0234e9f" />


---

## 📥 Download

A versão executável para Windows está disponível na área de **Releases** deste repositório.

Baixe o arquivo:

`GeradorArquivosTeste.exe`

Não é necessário instalar Python para utilizar a versão executável.

---

## ▶️ Como executar pelo código-fonte

### 1. Clonar o projeto

```bash
git clone https://github.com/ericasouzaqa/GeradorArquivosTeste.git
cd GeradorArquivosTeste
```

### 2. Instalar as dependências

```bash
py -3.13 -m pip install -r requirements.txt
```

### 3. Executar

```bash
py -3.13 gerador.py
```

---

## 📦 Gerar o executável

Para criar uma versão `.exe` para Windows:

```powershell
py -3.13 -m PyInstaller --onefile --windowed --name GeradorArquivosTeste --icon=icone.ico --add-data "capa.png;." gerador.py
```

O executável será criado em:

```text
dist/GeradorArquivosTeste.exe
```

---

## 🧪 Aplicação em QA

A ferramenta pode ser utilizada em cenários como:

- Testes de limite de tamanho de upload.
- Validação de extensões permitidas.
- Testes de arquivos grandes.
- Testes positivos e negativos de upload.
- Testes de mensagens de validação.
- Testes de performance relacionados ao processamento de arquivos.
- Criação de massa para testes manuais e automatizados.

---

## 📂 Estrutura do projeto

```text
GeradorArquivosTeste/
│
├── gerador.py
├── estilo.py
├── capa.png
├── icone.ico
├── README.md
├── .gitignore
├── requirements.txt
└── GeradorArquivosTeste.spec
```

Os diretórios `build/` e `dist/` são utilizados durante o processo de empacotamento e não fazem parte do código-fonte versionado.

---

## 👩‍💻 Autora

**Erica de Souza**

QA Analyst | Quality Assurance | Testes de Software

Desenvolvido como um projeto prático voltado à melhoria das atividades de testes e geração de massa para QA.

---

## 🔗 Contatos

- GitHub: [@ericasouzaqa](https://github.com/ericasouzaqa)
- LinkedIn: [Erica de Souza](https://www.linkedin.com/in/erica-souza/)

---

## 📄 Licença

Este projeto está disponível para fins de estudo, portfólio e demonstração técnica.
