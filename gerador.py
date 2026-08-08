import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser


# ============================================================
# PILLOW
# ============================================================

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_DISPONIVEL = True
except ImportError:
    PIL_DISPONIVEL = False


# ============================================================
# ESTILO
# ============================================================

from estilo import (
    configurar_estilo,
    aplicar_icone,
    criar_fundo,
    COR_CARD,
    COR_TEXTO,
    COR_TEXTO_SECUNDARIO,
    COR_STATUS,
    COR_BORDA,
    FONTE_SUBTITULO,
)


# ============================================================
# CONFIGURAÇÕES
# ============================================================

EXTENSOES = [
    "jpeg",
    "jpg",
    "m4a",
    "mp4",
    "ogg",
    "pdf",
    "png",
]

UNIDADES = [
    "KB",
    "MB",
    "GB",
]

# Blocos de 1 MB usados na gravação.
TAMANHO_BLOCO = 1024 * 1024

GITHUB_URL = (
    "https://github.com/ericasouzaqa/GeradorArquivosTeste"
)

LINKEDIN_URL = (
    "https://www.linkedin.com/in/erica-souza/"
)


# ============================================================
# DIRETÓRIO DA APLICAÇÃO
# ============================================================

def obter_diretorio_aplicacao():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(
        os.path.abspath(__file__)
    )


DIRETORIO_APLICACAO = obter_diretorio_aplicacao()

CAMINHO_CAPA = os.path.join(
    DIRETORIO_APLICACAO,
    "capa.png"
)

CAMINHO_ICONE = os.path.join(
    DIRETORIO_APLICACAO,
    "icone.ico"
)


# ============================================================
# VARIÁVEIS GLOBAIS
# ============================================================

janela = None

combo_extensao = None
combo_unidade = None
campo_tamanho = None
campo_nome = None
campo_pasta = None
label_status = None

gerar_todas = None

fundo_canvas = None


# ============================================================
# CONVERSÃO DE TAMANHO
# ============================================================

def converter_para_bytes(tamanho, unidade):
    """
    Converte o valor informado para bytes.

    1 KB = 1024 bytes
    1 MB = 1024² bytes
    1 GB = 1024³ bytes

    Não existe limite máximo artificial.
    """

    multiplicadores = {
        "KB": 1024,
        "MB": 1024 ** 2,
        "GB": 1024 ** 3,
    }

    unidade = unidade.upper().strip()

    if unidade not in multiplicadores:
        raise ValueError(
            f"Unidade inválida: {unidade}"
        )

    return int(
        tamanho * multiplicadores[unidade]
    )


# ============================================================
# FORMATAÇÃO
# ============================================================

def formatar_tamanho(bytes_total):
    """
    Formata bytes usando a maior unidade adequada.
    """

    if bytes_total >= 1024 ** 3:
        return (
            f"{bytes_total / (1024 ** 3):.2f} GB"
        )

    if bytes_total >= 1024 ** 2:
        return (
            f"{bytes_total / (1024 ** 2):.2f} MB"
        )

    if bytes_total >= 1024:
        return (
            f"{bytes_total / 1024:.2f} KB"
        )

    return f"{bytes_total} bytes"


# ============================================================
# FORMATAÇÃO NA UNIDADE ESCOLHIDA
# ============================================================

def formatar_tamanho_na_unidade(bytes_total, unidade):
    """
    Exibe o tamanho exatamente na unidade selecionada
    pelo usuário.
    """

    unidade = unidade.upper().strip()

    if unidade == "KB":
        valor = bytes_total / (1024 ** 1)

    elif unidade == "MB":
        valor = bytes_total / (1024 ** 2)

    elif unidade == "GB":
        valor = bytes_total / (1024 ** 3)

    else:
        raise ValueError(
            f"Unidade inválida: {unidade}"
        )

    return f"{valor:.2f} {unidade}"


# ============================================================
# NOME
# ============================================================

def gerar_nome_base(extensao, tamanho, unidade):
    """
    Gera o nome usando a unidade selecionada.
    """

    return (
        f"{extensao}{tamanho:g}{unidade}"
    )


# ============================================================
# ATUALIZAR NOME
# ============================================================

def atualizar_nome_arquivo(event=None):
    if gerar_todas.get():
        campo_nome.configure(
            state="normal"
        )

        campo_nome.delete(
            0,
            tk.END
        )

        campo_nome.insert(
            0,
            "Gerado automaticamente para todas as extensões."
        )

        campo_nome.configure(
            state="disabled"
        )

        return

    extensao = combo_extensao.get().strip()
    unidade = combo_unidade.get().strip()
    valor = campo_tamanho.get().strip()

    if not extensao or not unidade or not valor:
        campo_nome.delete(
            0,
            tk.END
        )
        return

    try:
        tamanho = float(valor)

    except ValueError:
        campo_nome.delete(
            0,
            tk.END
        )
        return

    if tamanho <= 0:
        campo_nome.delete(
            0,
            tk.END
        )
        return

    nome_base = gerar_nome_base(
        extensao,
        tamanho,
        unidade
    )

    nome = f"{nome_base}.{extensao}"

    campo_nome.delete(
        0,
        tk.END
    )

    campo_nome.insert(
        0,
        nome
    )


# ============================================================
# NOME ÚNICO
# ============================================================

def gerar_nome_unico(pasta, nome_arquivo):

    caminho = os.path.join(
        pasta,
        nome_arquivo
    )

    if not os.path.exists(caminho):
        return caminho

    nome, extensao = os.path.splitext(
        nome_arquivo
    )

    contador = 1

    while True:

        novo_nome = (
            f"{nome}_{contador}{extensao}"
        )

        novo_caminho = os.path.join(
            pasta,
            novo_nome
        )

        if not os.path.exists(
            novo_caminho
        ):
            return novo_caminho

        contador += 1


# ============================================================
# PREENCHER ATÉ O TAMANHO EXATO
# ============================================================

def completar_arquivo(caminho, tamanho_bytes):
    """
    Garante que o arquivo tenha exatamente
    o número de bytes solicitado.
    """

    tamanho_atual = os.path.getsize(
        caminho
    )

    if tamanho_atual > tamanho_bytes:
        raise RuntimeError(
            "O arquivo base é maior que o tamanho solicitado."
        )

    restante = (
        tamanho_bytes -
        tamanho_atual
    )

    if restante <= 0:
        return

    with open(
        caminho,
        "ab"
    ) as arquivo:

        while restante > 0:

            tamanho_bloco = min(
                TAMANHO_BLOCO,
                restante
            )

            arquivo.write(
                os.urandom(
                    tamanho_bloco
                )
            )

            restante -= tamanho_bloco


# ============================================================
# IMAGENS
# ============================================================

def criar_imagem_com_nome(
    caminho,
    nome_arquivo,
    extensao,
    tamanho_bytes
):

    if not PIL_DISPONIVEL:
        raise RuntimeError(
            "A biblioteca Pillow não está instalada."
        )

    largura = 1000
    altura = 500

    imagem = Image.new(
        "RGB",
        (
            largura,
            altura
        ),
        "white"
    )

    desenho = ImageDraw.Draw(
        imagem
    )

    try:
        fonte = ImageFont.truetype(
            "arial.ttf",
            48
        )

    except OSError:
        fonte = ImageFont.load_default()

    caixa = desenho.textbbox(
        (0, 0),
        nome_arquivo,
        font=fonte
    )

    largura_texto = (
        caixa[2] - caixa[0]
    )

    altura_texto = (
        caixa[3] - caixa[1]
    )

    x = (
        largura - largura_texto
    ) // 2

    y = (
        altura - altura_texto
    ) // 2

    desenho.text(
        (
            x,
            y
        ),
        nome_arquivo,
        fill="black",
        font=fonte
    )

    if extensao == "png":

        imagem.save(
            caminho,
            "PNG"
        )

    else:

        imagem.save(
            caminho,
            "JPEG",
            quality=90
        )

    completar_arquivo(
        caminho,
        tamanho_bytes
    )


# ============================================================
# PDF
# ============================================================

def criar_pdf_com_nome(
    caminho,
    nome_arquivo,
    tamanho_bytes
):

    texto = (
        nome_arquivo
        .replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )

    conteudo = (
        "BT\n"
        "/F1 24 Tf\n"
        "100 700 Td\n"
        f"({texto}) Tj\n"
        "ET\n"
    ).encode(
        "latin-1",
        errors="replace"
    )

    objetos = [

        b"<< /Type /Catalog /Pages 2 0 R >>",

        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",

        (
            b"<< /Type /Page /Parent 2 0 R "
            b"/MediaBox [0 0 595 842] "
            b"/Resources << /Font << /F1 5 0 R >> >> "
            b"/Contents 4 0 R >>"
        ),

        (
            b"<< /Length "
            + str(len(conteudo)).encode()
            + b" >>\nstream\n"
            + conteudo
            + b"endstream"
        ),

        (
            b"<< /Type /Font /Subtype /Type1 "
            b"/BaseFont /Helvetica >>"
        ),
    ]

    pdf = bytearray(
        b"%PDF-1.4\n"
    )

    offsets = [0]

    for numero, objeto in enumerate(
        objetos,
        start=1
    ):

        offsets.append(
            len(pdf)
        )

        pdf.extend(
            f"{numero} 0 obj\n".encode()
        )

        pdf.extend(
            objeto
        )

        pdf.extend(
            b"\nendobj\n"
        )

    inicio_xref = len(pdf)

    pdf.extend(
        (
            f"xref\n"
            f"0 {len(objetos) + 1}\n"
        ).encode()
    )

    pdf.extend(
        b"0000000000 65535 f \n"
    )

    for offset in offsets[1:]:

        pdf.extend(
            f"{offset:010d} 00000 n \n".encode()
        )

    pdf.extend(
        (
            f"trailer\n"
            f"<< /Size {len(objetos) + 1} "
            f"/Root 1 0 R >>\n"
            f"startxref\n"
            f"{inicio_xref}\n"
            f"%%EOF\n"
        ).encode()
    )

    with open(
        caminho,
        "wb"
    ) as arquivo:

        arquivo.write(
            pdf
        )

    completar_arquivo(
        caminho,
        tamanho_bytes
    )


# ============================================================
# BINÁRIO
# ============================================================

def criar_arquivo_binario(
    caminho,
    tamanho_bytes
):

    restante = tamanho_bytes

    with open(
        caminho,
        "wb"
    ) as arquivo:

        while restante > 0:

            tamanho_bloco = min(
                TAMANHO_BLOCO,
                restante
            )

            arquivo.write(
                os.urandom(
                    tamanho_bloco
                )
            )

            restante -= tamanho_bloco


# ============================================================
# GERAR ARQUIVO
# ============================================================

def gerar_arquivo(
    caminho,
    tamanho_bytes,
    extensao,
    nome_arquivo
):

    if extensao in (
        "png",
        "jpg",
        "jpeg"
    ):

        criar_imagem_com_nome(
            caminho,
            nome_arquivo,
            extensao,
            tamanho_bytes
        )

        return

    if extensao == "pdf":

        criar_pdf_com_nome(
            caminho,
            nome_arquivo,
            tamanho_bytes
        )

        return

    criar_arquivo_binario(
        caminho,
        tamanho_bytes
    )


# ============================================================
# PASTA
# ============================================================

def selecionar_pasta():

    pasta = filedialog.askdirectory(
        title=(
            "Selecione o diretório "
            "onde os arquivos serão salvos"
        )
    )

    if pasta:

        campo_pasta.delete(
            0,
            tk.END
        )

        campo_pasta.insert(
            0,
            pasta
        )

        atualizar_status(
            "Pasta selecionada. Pronto para gerar."
        )


# ============================================================
# STATUS
# ============================================================

def atualizar_status(mensagem):

    label_status.config(
        text=mensagem
    )


# ============================================================
# MODO LOTE
# ============================================================

def alternar_geracao_lote():

    if gerar_todas.get():

        combo_extensao.configure(
            state="disabled"
        )

        campo_nome.configure(
            state="normal"
        )

        campo_nome.delete(
            0,
            tk.END
        )

        campo_nome.insert(
            0,
            "Gerado automaticamente para todas as extensões."
        )

        campo_nome.configure(
            state="disabled"
        )

        atualizar_status(
            "Modo lote ativado."
        )

    else:

        combo_extensao.configure(
            state="readonly"
        )

        campo_nome.configure(
            state="normal"
        )

        campo_nome.delete(
            0,
            tk.END
        )

        atualizar_nome_arquivo()

        atualizar_status(
            "Modo individual ativado."
        )


# ============================================================
# VALIDAÇÃO
# ============================================================

def validar_tamanho():

    valor = campo_tamanho.get().strip()

    if not valor:
        return False

    try:

        tamanho = float(
            valor
        )

        return tamanho > 0

    except ValueError:

        return False


# ============================================================
# GERAR
# ============================================================

def gerar():

    # --------------------------------------------------------
    # IMPORTANTE:
    # Captura NOVAMENTE os valores atuais da interface.
    # Isso evita qualquer valor antigo quando o usuário
    # estava no modo "todas as extensões".
    # --------------------------------------------------------

    unidade = (
        combo_unidade.get()
        .strip()
        .upper()
    )

    valor = (
        campo_tamanho.get()
        .strip()
    )

    pasta = (
        campo_pasta.get()
        .strip()
    )

    # --------------------------------------------------------
    # UNIDADE
    # --------------------------------------------------------

    if unidade not in UNIDADES:

        messagebox.showwarning(
            "Atenção",
            "Selecione a unidade do tamanho."
        )

        combo_unidade.focus()

        return

    # --------------------------------------------------------
    # TAMANHO
    # --------------------------------------------------------

    if not valor:

        messagebox.showwarning(
            "Atenção",
            "Digite o tamanho do arquivo."
        )

        campo_tamanho.focus()

        return

    try:

        tamanho = float(
            valor
        )

    except ValueError:

        messagebox.showerror(
            "Valor inválido",
            "Digite um número válido."
        )

        campo_tamanho.focus()

        return

    if tamanho <= 0:

        messagebox.showerror(
            "Valor inválido",
            "O tamanho deve ser maior que zero."
        )

        campo_tamanho.focus()

        return

    # --------------------------------------------------------
    # CONVERSÃO DEFINITIVA
    # --------------------------------------------------------

    try:

        tamanho_bytes = converter_para_bytes(
            tamanho,
            unidade
        )

    except ValueError as erro:

        messagebox.showerror(
            "Erro",
            str(erro)
        )

        return

    if tamanho_bytes <= 0:

        messagebox.showerror(
            "Valor inválido",
            "O tamanho informado é muito pequeno."
        )

        return

    # --------------------------------------------------------
    # PASTA
    # --------------------------------------------------------

    if not pasta:

        messagebox.showwarning(
            "Atenção",
            "Selecione uma pasta para salvar os arquivos."
        )

        selecionar_pasta()

        return

    if not os.path.isdir(pasta):

        messagebox.showerror(
            "Pasta inválida",
            "O diretório selecionado não existe."
        )

        return

    # --------------------------------------------------------
    # EXTENSÕES
    # --------------------------------------------------------

    if gerar_todas.get():

        extensoes = list(
            EXTENSOES
        )

    else:

        extensao = (
            combo_extensao.get()
            .strip()
            .lower()
        )

        if extensao not in EXTENSOES:

            messagebox.showwarning(
                "Atenção",
                "Selecione uma extensão."
            )

            combo_extensao.focus()

            return

        extensoes = [
            extensao
        ]

    # --------------------------------------------------------
    # PILLOW
    # --------------------------------------------------------

    if any(
        extensao in (
            "png",
            "jpg",
            "jpeg"
        )
        for extensao in extensoes
    ) and not PIL_DISPONIVEL:

        messagebox.showerror(
            "Biblioteca necessária",
            (
                "A biblioteca Pillow não está instalada.\n\n"
                "Execute:\n"
                "py -3.13 -m pip install Pillow"
            )
        )

        return

    # --------------------------------------------------------
    # INFORMAÇÕES PARA STATUS
    # --------------------------------------------------------

    tamanho_solicitado = (
        formatar_tamanho_na_unidade(
            tamanho_bytes,
            unidade
        )
    )

    arquivos = []

    atualizar_status(
        (
            f"Gerando {len(extensoes)} arquivo(s) "
            f"com {tamanho_solicitado}..."
        )
    )

    janela.update_idletasks()

    # --------------------------------------------------------
    # GERAÇÃO
    # --------------------------------------------------------

    try:

        for extensao in extensoes:

            # O tamanho_bytes usado aqui é EXATAMENTE
            # o calculado a partir da unidade atual.

            nome_base = gerar_nome_base(
                extensao,
                tamanho,
                unidade
            )

            nome = (
                f"{nome_base}.{extensao}"
            )

            caminho = gerar_nome_unico(
                pasta,
                nome
            )

            nome_final = os.path.basename(
                caminho
            )

            atualizar_status(
                f"Gerando: {nome_final}"
            )

            janela.update_idletasks()

            # GERAÇÃO REAL
            gerar_arquivo(
                caminho,
                tamanho_bytes,
                extensao,
                nome_final
            )

            # ------------------------------------------------
            # VALIDAÇÃO REAL NO DISCO
            # ------------------------------------------------

            tamanho_real = os.path.getsize(
                caminho
            )

            if tamanho_real != tamanho_bytes:

                raise RuntimeError(
                    (
                        f"O arquivo {nome_final} "
                        f"foi criado com "
                        f"{tamanho_real} bytes, "
                        f"mas o esperado era "
                        f"{tamanho_bytes} bytes."
                    )
                )

            arquivos.append(
                nome_final
            )

            atualizar_status(
                (
                    f"Concluído: {nome_final} "
                    f"({formatar_tamanho_na_unidade(tamanho_real, unidade)})"
                )
            )

            janela.update_idletasks()

        # ----------------------------------------------------
        # RESULTADO
        # ----------------------------------------------------

        quantidade = len(
            arquivos
        )

        atualizar_status(
            (
                f"✓ {quantidade} arquivo(s) "
                "gerado(s) com sucesso."
            )
        )

        if quantidade == 1:

            lista = (
                f"Arquivo: {arquivos[0]}"
            )

        else:

            lista = (
                "Arquivos gerados:\n\n"
                + "\n".join(
                    f"• {arquivo}"
                    for arquivo in arquivos
                )
            )

        messagebox.showinfo(
            "Arquivos gerados",
            (
                "Geração concluída com sucesso!\n\n"
                f"{lista}\n\n"
                f"Tamanho solicitado: "
                f"{tamanho_solicitado}\n"
                f"Tamanho em bytes: "
                f"{tamanho_bytes:,}\n"
                f"Local: {pasta}"
            )
        )

    except (
        OSError,
        RuntimeError,
        ValueError
    ) as erro:

        atualizar_status(
            "✕ Erro ao gerar arquivo(s)."
        )

        messagebox.showerror(
            "Erro ao gerar arquivo",
            (
                "Não foi possível concluir "
                f"a geração.\n\n{erro}"
            )
        )


# ============================================================
# LIMPAR
# ============================================================

def limpar():

    gerar_todas.set(
        False
    )

    combo_extensao.configure(
        state="readonly"
    )

    campo_nome.configure(
        state="normal"
    )

    combo_extensao.set(
        ""
    )

    combo_unidade.set(
        ""
    )

    campo_tamanho.delete(
        0,
        tk.END
    )

    campo_nome.delete(
        0,
        tk.END
    )

    campo_pasta.delete(
        0,
        tk.END
    )

    atualizar_status(
        "Preencha os campos para gerar um arquivo de teste."
    )

    combo_extensao.focus()


# ============================================================
# LINKS
# ============================================================

def abrir_github():

    webbrowser.open(
        GITHUB_URL
    )


def abrir_linkedin():

    webbrowser.open(
        LINKEDIN_URL
    )


# ============================================================
# RODAPÉ
# ============================================================

def criar_rodape():

    y = 615

    fundo_canvas.create_text(
        275,
        y,
        text="Erica de Souza",
        fill="#FFFFFF",
        font=("Segoe UI", 12, "bold"),
        anchor="center"
    )

    # --------------------------------------------------------
    # GITHUB
    # --------------------------------------------------------

    github_x1 = 425
    github_y1 = 590
    github_x2 = 535
    github_y2 = 640

    fundo_canvas.create_rectangle(
        github_x1,
        github_y1,
        github_x2,
        github_y2,
        fill="#7B2CBF",
        outline="#E8B8FF",
        width=2,
        tags=("github_bg",)
    )

    fundo_canvas.create_text(
        (github_x1 + github_x2) / 2,
        (github_y1 + github_y2) / 2,
        text="GitHub",
        fill="#FFFFFF",
        font=("Segoe UI", 11, "bold"),
        anchor="center",
        tags=("github_text",)
    )

    # --------------------------------------------------------
    # SEPARADOR
    # --------------------------------------------------------

    fundo_canvas.create_text(
        565,
        y,
        text="│",
        fill="#E8B8FF",
        font=("Segoe UI", 14, "bold"),
        anchor="center"
    )

    # --------------------------------------------------------
    # LINKEDIN
    # --------------------------------------------------------

    linkedin_x1 = 595
    linkedin_y1 = 590
    linkedin_x2 = 715
    linkedin_y2 = 640

    fundo_canvas.create_rectangle(
        linkedin_x1,
        linkedin_y1,
        linkedin_x2,
        linkedin_y2,
        fill="#7B2CBF",
        outline="#E8B8FF",
        width=2,
        tags=("linkedin_bg",)
    )

    fundo_canvas.create_text(
        (linkedin_x1 + linkedin_x2) / 2,
        (linkedin_y1 + linkedin_y2) / 2,
        text="LinkedIn",
        fill="#FFFFFF",
        font=("Segoe UI", 11, "bold"),
        anchor="center",
        tags=("linkedin_text",)
    )

    # --------------------------------------------------------
    # GITHUB HOVER
    # --------------------------------------------------------

    def github_entrar(event):

        fundo_canvas.config(
            cursor="hand2"
        )

        fundo_canvas.itemconfigure(
            "github_bg",
            fill="#9D4EDD"
        )

    def github_sair(event):

        fundo_canvas.config(
            cursor=""
        )

        fundo_canvas.itemconfigure(
            "github_bg",
            fill="#7B2CBF"
        )

    fundo_canvas.tag_bind(
        "github_bg",
        "<Button-1>",
        lambda event: abrir_github()
    )

    fundo_canvas.tag_bind(
        "github_text",
        "<Button-1>",
        lambda event: abrir_github()
    )

    fundo_canvas.tag_bind(
        "github_bg",
        "<Enter>",
        github_entrar
    )

    fundo_canvas.tag_bind(
        "github_text",
        "<Enter>",
        github_entrar
    )

    fundo_canvas.tag_bind(
        "github_bg",
        "<Leave>",
        github_sair
    )

    fundo_canvas.tag_bind(
        "github_text",
        "<Leave>",
        github_sair
    )

    # --------------------------------------------------------
    # LINKEDIN HOVER
    # --------------------------------------------------------

    def linkedin_entrar(event):

        fundo_canvas.config(
            cursor="hand2"
        )

        fundo_canvas.itemconfigure(
            "linkedin_bg",
            fill="#9D4EDD"
        )

    def linkedin_sair(event):

        fundo_canvas.config(
            cursor=""
        )

        fundo_canvas.itemconfigure(
            "linkedin_bg",
            fill="#7B2CBF"
        )

    fundo_canvas.tag_bind(
        "linkedin_bg",
        "<Button-1>",
        lambda event: abrir_linkedin()
    )

    fundo_canvas.tag_bind(
        "linkedin_text",
        "<Button-1>",
        lambda event: abrir_linkedin()
    )

    fundo_canvas.tag_bind(
        "linkedin_bg",
        "<Enter>",
        linkedin_entrar
    )

    fundo_canvas.tag_bind(
        "linkedin_text",
        "<Enter>",
        linkedin_entrar
    )

    fundo_canvas.tag_bind(
        "linkedin_bg",
        "<Leave>",
        linkedin_sair
    )

    fundo_canvas.tag_bind(
        "linkedin_text",
        "<Leave>",
        linkedin_sair
    )


# ============================================================
# INTERFACE
# ============================================================

def main():

    global janela
    global combo_extensao
    global combo_unidade
    global campo_tamanho
    global campo_nome
    global campo_pasta
    global label_status
    global gerar_todas
    global fundo_canvas

    janela = tk.Tk()

    janela.title(
        "Gerador de Arquivos de Teste"
    )

    janela.geometry(
        "900x650"
    )

    janela.resizable(
        False,
        False
    )

    # --------------------------------------------------------
    # ESTILO
    # --------------------------------------------------------

    configurar_estilo()

    # --------------------------------------------------------
    # ÍCONE
    # --------------------------------------------------------

    try:

        aplicar_icone(
            janela
        )

    except Exception:

        pass

    # --------------------------------------------------------
    # FUNDO
    # --------------------------------------------------------

    fundo = criar_fundo(
        janela,
        900,
        650
    )

    fundo_canvas = tk.Canvas(
        janela,
        width=900,
        height=650,
        bd=0,
        highlightthickness=0
    )

    fundo_canvas.place(
        x=0,
        y=0
    )

    if fundo:

        fundo_canvas.create_image(
            0,
            0,
            image=fundo,
            anchor="nw"
        )

        fundo_canvas.image = fundo

    # --------------------------------------------------------
    # RODAPÉ
    # --------------------------------------------------------

    criar_rodape()

    # --------------------------------------------------------
    # PAINEL
    # --------------------------------------------------------

    painel = tk.Frame(
        janela,
        bg=COR_CARD,
        highlightbackground=COR_BORDA,
        highlightthickness=1
    )

    painel.place(
        relx=0.5,
        rely=0.43,
        anchor="center",
        width=720,
        height=465
    )

    conteudo = tk.Frame(
        painel,
        bg=COR_CARD
    )

    conteudo.pack(
        fill="both",
        expand=True,
        padx=28,
        pady=20
    )

    # --------------------------------------------------------
    # CABEÇALHO
    # --------------------------------------------------------

    tk.Label(
        conteudo,
        text="Gerador de Arquivos de Teste",
        font=("Segoe UI", 20, "bold"),
        fg=COR_TEXTO,
        bg=COR_CARD
    ).pack(
        anchor="w"
    )

    tk.Label(
        conteudo,
        text=(
            "Gere arquivos de teste com extensão e tamanho "
            "definidos para apoiar atividades de QA."
        ),
        font=FONTE_SUBTITULO,
        fg=COR_TEXTO_SECUNDARIO,
        bg=COR_CARD
    ).pack(
        anchor="w",
        pady=(3, 12)
    )

    # --------------------------------------------------------
    # SEÇÃO
    # --------------------------------------------------------

    tk.Label(
        conteudo,
        text="Configuração do arquivo",
        font=("Segoe UI", 11, "bold"),
        fg=COR_TEXTO,
        bg=COR_CARD
    ).pack(
        anchor="w",
        pady=(0, 7)
    )

    # --------------------------------------------------------
    # CAMPOS
    # --------------------------------------------------------

    frame_campos = tk.Frame(
        conteudo,
        bg=COR_CARD
    )

    frame_campos.pack(
        fill="x"
    )

    frame_campos.columnconfigure(
        0,
        weight=1
    )

    frame_campos.columnconfigure(
        1,
        weight=1
    )

    frame_campos.columnconfigure(
        2,
        weight=1
    )

    # EXTENSÃO

    tk.Label(
        frame_campos,
        text="Extensão",
        font=FONTE_SUBTITULO,
        fg=COR_TEXTO_SECUNDARIO,
        bg=COR_CARD
    ).grid(
        row=0,
        column=0,
        sticky="w",
        padx=(0, 10)
    )

    combo_extensao = ttk.Combobox(
        frame_campos,
        values=EXTENSOES,
        state="readonly"
    )

    combo_extensao.grid(
        row=1,
        column=0,
        sticky="ew",
        padx=(0, 10)
    )

    # UNIDADE

    tk.Label(
        frame_campos,
        text="Unidade",
        font=FONTE_SUBTITULO,
        fg=COR_TEXTO_SECUNDARIO,
        bg=COR_CARD
    ).grid(
        row=0,
        column=1,
        sticky="w",
        padx=(0, 10)
    )

    combo_unidade = ttk.Combobox(
        frame_campos,
        values=UNIDADES,
        state="readonly"
    )

    combo_unidade.grid(
        row=1,
        column=1,
        sticky="ew",
        padx=(0, 10)
    )

    # TAMANHO

    tk.Label(
        frame_campos,
        text="Tamanho",
        font=FONTE_SUBTITULO,
        fg=COR_TEXTO_SECUNDARIO,
        bg=COR_CARD
    ).grid(
        row=0,
        column=2,
        sticky="w"
    )

    validacao = janela.register(
        lambda valor: (
            valor == ""
            or (
                valor.count(".") <= 1
                and valor.replace(
                    ".",
                    ""
                ).isdigit()
            )
        )
    )

    campo_tamanho = ttk.Entry(
        frame_campos,
        validate="key",
        validatecommand=(
            validacao,
            "%P"
        )
    )

    campo_tamanho.grid(
        row=1,
        column=2,
        sticky="ew"
    )

    # --------------------------------------------------------
    # MODO LOTE
    # --------------------------------------------------------

    gerar_todas = tk.BooleanVar(
        value=False
    )

    ttk.Checkbutton(
        conteudo,
        text="Gerar para todas as extensões",
        variable=gerar_todas,
        command=alternar_geracao_lote
    ).pack(
        anchor="w",
        pady=(9, 0)
    )

    tk.Label(
        conteudo,
        text="PNG, JPG, JPEG, PDF, MP4, M4A e OGG.",
        font=FONTE_SUBTITULO,
        fg=COR_TEXTO_SECUNDARIO,
        bg=COR_CARD
    ).pack(
        anchor="w",
        pady=(1, 8)
    )

    # --------------------------------------------------------
    # NOME
    # --------------------------------------------------------

    tk.Label(
        conteudo,
        text="Nome do arquivo",
        font=FONTE_SUBTITULO,
        fg=COR_TEXTO_SECUNDARIO,
        bg=COR_CARD
    ).pack(
        anchor="w",
        pady=(0, 3)
    )

    campo_nome = ttk.Entry(
        conteudo
    )

    campo_nome.pack(
        fill="x"
    )

    # --------------------------------------------------------
    # PASTA
    # --------------------------------------------------------

    tk.Label(
        conteudo,
        text="Diretório de destino",
        font=FONTE_SUBTITULO,
        fg=COR_TEXTO_SECUNDARIO,
        bg=COR_CARD
    ).pack(
        anchor="w",
        pady=(8, 3)
    )

    frame_pasta = tk.Frame(
        conteudo,
        bg=COR_CARD
    )

    frame_pasta.pack(
        fill="x"
    )

    campo_pasta = ttk.Entry(
        frame_pasta
    )

    campo_pasta.pack(
        side="left",
        fill="x",
        expand=True
    )

    ttk.Button(
        frame_pasta,
        text="Selecionar pasta",
        command=selecionar_pasta
    ).pack(
        side="left",
        padx=(8, 0)
    )

    # --------------------------------------------------------
    # BOTÕES
    # --------------------------------------------------------

    frame_botoes = tk.Frame(
        conteudo,
        bg=COR_CARD
    )

    frame_botoes.pack(
        fill="x",
        pady=(12, 8)
    )

    ttk.Button(
        frame_botoes,
        text="Limpar",
        command=limpar
    ).pack(
        side="left"
    )

    ttk.Button(
        frame_botoes,
        text="GERAR ARQUIVO(S)",
        command=gerar,
        style="Acao.TButton"
    ).pack(
        side="right"
    )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    frame_status = tk.Frame(
        conteudo,
        bg=COR_STATUS
    )

    frame_status.pack(
        fill="x"
    )

    label_status = tk.Label(
        frame_status,
        text=(
            "Preencha os campos para gerar "
            "um arquivo de teste."
        ),
        font=("Segoe UI", 9),
        fg=COR_TEXTO,
        bg=COR_STATUS,
        anchor="w"
    )

    label_status.pack(
        fill="x",
        padx=12,
        pady=7
    )

    # --------------------------------------------------------
    # EVENTOS
    # --------------------------------------------------------

    combo_extensao.bind(
        "<<ComboboxSelected>>",
        atualizar_nome_arquivo
    )

    combo_unidade.bind(
        "<<ComboboxSelected>>",
        atualizar_nome_arquivo
    )

    campo_tamanho.bind(
        "<KeyRelease>",
        atualizar_nome_arquivo
    )

    campo_tamanho.bind(
        "<Return>",
        lambda event: gerar()
    )

    combo_extensao.focus()

    # --------------------------------------------------------
    # EXECUÇÃO
    # --------------------------------------------------------

    janela.mainloop()


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

if __name__ == "__main__":
    main()