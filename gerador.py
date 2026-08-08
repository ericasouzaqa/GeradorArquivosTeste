import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser

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

try:
    from PIL import Image, ImageDraw, ImageFont

    PIL_DISPONIVEL = True

except ImportError:
    PIL_DISPONIVEL = False


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

TAMANHO_BLOCO = 1024 * 1024
LIMITE_MAXIMO = 10 * (1024 ** 3)

GITHUB_URL = "https://github.com/ericasouzaqa"
LINKEDIN_URL = "https://www.linkedin.com/in/erica-souza/"


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
# ÍCONE DO WINDOWS
# ============================================================

def configurar_icone_windows():
    """
    Configura o identificador do aplicativo no Windows
    para melhorar a identificação na barra de tarefas.
    """

    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "EricaSouza.GeradorArquivosTeste"
            )

        except Exception:
            pass

    try:
        aplicar_icone(janela)

    except Exception:
        pass


# ============================================================
# UTILITÁRIOS
# ============================================================

def converter_para_bytes(tamanho, unidade):
    multiplicadores = {
        "KB": 1024,
        "MB": 1024 ** 2,
        "GB": 1024 ** 3,
    }

    return int(
        tamanho * multiplicadores[unidade]
    )


def formatar_tamanho(bytes_total):
    if bytes_total >= 1024 ** 3:
        return f"{bytes_total / (1024 ** 3):.2f} GB"

    if bytes_total >= 1024 ** 2:
        return f"{bytes_total / (1024 ** 2):.2f} MB"

    return f"{bytes_total / 1024:.2f} KB"


def gerar_nome_base(extensao, tamanho, unidade):
    return f"{extensao}{tamanho:g}{unidade}"


# ============================================================
# NOME AUTOMÁTICO
# ============================================================

def atualizar_nome_arquivo(event=None):
    if gerar_todas.get():
        campo_nome.configure(state="normal")

        campo_nome.delete(0, tk.END)

        campo_nome.insert(
            0,
            "Gerado automaticamente para todas as extensões."
        )

        campo_nome.configure(state="disabled")

        return

    extensao = combo_extensao.get()
    unidade = combo_unidade.get()
    valor = campo_tamanho.get().strip()

    if not extensao or not unidade or not valor:
        campo_nome.delete(0, tk.END)
        return

    try:
        tamanho = float(valor)

        if tamanho <= 0:
            campo_nome.delete(0, tk.END)
            return

    except ValueError:
        campo_nome.delete(0, tk.END)
        return

    nome = gerar_nome_base(
        extensao,
        tamanho,
        unidade
    )

    campo_nome.delete(0, tk.END)

    campo_nome.insert(
        0,
        f"{nome}.{extensao}"
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
        novo_nome = f"{nome}_{contador}{extensao}"

        novo_caminho = os.path.join(
            pasta,
            novo_nome
        )

        if not os.path.exists(novo_caminho):
            return novo_caminho

        contador += 1


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
        (largura, altura),
        "white"
    )

    desenho = ImageDraw.Draw(imagem)

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

    largura_texto = caixa[2] - caixa[0]
    altura_texto = caixa[3] - caixa[1]

    x = (largura - largura_texto) // 2
    y = (altura - altura_texto) // 2

    desenho.text(
        (x, y),
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

    tamanho_atual = os.path.getsize(caminho)

    if tamanho_atual < tamanho_bytes:
        with open(caminho, "ab") as arquivo:
            arquivo.write(
                os.urandom(
                    tamanho_bytes - tamanho_atual
                )
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
        offsets.append(len(pdf))

        pdf.extend(
            f"{numero} 0 obj\n".encode()
        )

        pdf.extend(objeto)

        pdf.extend(
            b"\nendobj\n"
        )

    inicio_xref = len(pdf)

    pdf.extend(
        f"xref\n0 {len(objetos) + 1}\n".encode()
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

    with open(caminho, "wb") as arquivo:
        arquivo.write(pdf)

        tamanho_atual = arquivo.tell()

        if tamanho_atual < tamanho_bytes:
            arquivo.write(
                os.urandom(
                    tamanho_bytes - tamanho_atual
                )
            )


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

    bloco = os.urandom(
        min(
            TAMANHO_BLOCO,
            tamanho_bytes
        )
    )

    restante = tamanho_bytes

    with open(caminho, "wb") as arquivo:
        while restante > 0:
            tamanho_bloco = min(
                len(bloco),
                restante
            )

            if tamanho_bloco == len(bloco):
                arquivo.write(bloco)

            else:
                arquivo.write(
                    os.urandom(
                        tamanho_bloco
                    )
                )

            restante -= tamanho_bloco


# ============================================================
# PASTA
# ============================================================

def selecionar_pasta():
    pasta = filedialog.askdirectory(
        title="Selecione o diretório onde os arquivos serão salvos"
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
        tamanho = float(valor)

        return tamanho > 0

    except ValueError:
        return False


# ============================================================
# GERAR
# ============================================================

def gerar():
    unidade = combo_unidade.get()
    valor = campo_tamanho.get().strip()
    pasta = campo_pasta.get().strip()

    if not unidade:
        messagebox.showwarning(
            "Atenção",
            "Selecione a unidade do tamanho."
        )

        combo_unidade.focus()

        return

    if not valor:
        messagebox.showwarning(
            "Atenção",
            "Digite o tamanho do arquivo."
        )

        campo_tamanho.focus()

        return

    if not validar_tamanho():
        messagebox.showerror(
            "Valor inválido",
            "Digite um tamanho numérico maior que zero."
        )

        campo_tamanho.focus()

        return

    tamanho = float(valor)

    tamanho_bytes = converter_para_bytes(
        tamanho,
        unidade
    )

    if tamanho_bytes > LIMITE_MAXIMO:
        messagebox.showerror(
            "Tamanho não permitido",
            "O tamanho máximo permitido é 10 GB."
        )

        campo_tamanho.focus()

        return

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

    if gerar_todas.get():
        extensoes = EXTENSOES

    else:
        extensao = combo_extensao.get()

        if not extensao:
            messagebox.showwarning(
                "Atenção",
                "Selecione uma extensão."
            )

            combo_extensao.focus()

            return

        extensoes = [extensao]

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
            "A biblioteca Pillow não está instalada.\n\n"
            "Execute no terminal:\n"
            "py -3.13 -m pip install Pillow"
        )

        return

    arquivos = []

    atualizar_status(
        "Gerando arquivo(s)..."
    )

    janela.update_idletasks()

    try:
        for extensao in extensoes:
            nome = (
                f"{gerar_nome_base(extensao, tamanho, unidade)}."
                f"{extensao}"
            )

            caminho = gerar_nome_unico(
                pasta,
                nome
            )

            nome_final = os.path.basename(
                caminho
            )

            gerar_arquivo(
                caminho,
                tamanho_bytes,
                extensao,
                nome_final
            )

            arquivos.append(
                nome_final
            )

            atualizar_status(
                f"Gerando: {nome_final}"
            )

            janela.update_idletasks()

        quantidade = len(arquivos)

        atualizar_status(
            f"✓ {quantidade} arquivo(s) gerado(s) com sucesso."
        )

        if quantidade == 1:
            lista = f"Arquivo: {arquivos[0]}"

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
            "Geração concluída com sucesso!\n\n"
            f"{lista}\n\n"
            f"Tamanho de cada arquivo: "
            f"{formatar_tamanho(tamanho_bytes)}\n"
            f"Local: {pasta}"
        )

    except (
        OSError,
        RuntimeError
    ) as erro:

        atualizar_status(
            "✕ Erro ao gerar arquivo(s)."
        )

        messagebox.showerror(
            "Erro ao gerar arquivo",
            f"Não foi possível concluir a geração.\n\n{erro}"
        )


# ============================================================
# LIMPAR
# ============================================================

def limpar():
    gerar_todas.set(False)

    combo_extensao.configure(
        state="readonly"
    )

    campo_nome.configure(
        state="normal"
    )

    combo_extensao.set("")
    combo_unidade.set("")

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
    webbrowser.open(GITHUB_URL)


def abrir_linkedin():
    webbrowser.open(LINKEDIN_URL)


# ============================================================
# RODAPÉ
# ============================================================

def criar_rodape():
    y = 615

    # Nome

    fundo_canvas.create_text(
        275,
        y,
        text="Erica de Souza",
        fill="#FFFFFF",
        font=("Segoe UI", 12, "bold"),
        anchor="center"
    )

    # GitHub

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

    # Separador

    fundo_canvas.create_text(
        565,
        y,
        text="│",
        fill="#E8B8FF",
        font=("Segoe UI", 14, "bold"),
        anchor="center"
    )

    # LinkedIn

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

    # ========================================================
    # HOVER GITHUB
    # ========================================================

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

    # ========================================================
    # HOVER LINKEDIN
    # ========================================================

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

    configurar_estilo()

    # ========================================================
    # ÍCONE
    # ========================================================

    configurar_icone_windows()

    # ========================================================
    # FUNDO
    # ========================================================

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

    # ========================================================
    # RODAPÉ
    # ========================================================

    criar_rodape()

    # ========================================================
    # PAINEL CENTRAL
    # ========================================================

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

    # ========================================================
    # CABEÇALHO
    # ========================================================

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

    # ========================================================
    # CONFIGURAÇÃO
    # ========================================================

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

    # ========================================================
    # EXTENSÃO
    # ========================================================

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

    # ========================================================
    # UNIDADE
    # ========================================================

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

    # ========================================================
    # TAMANHO
    # ========================================================

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
                and valor.replace(".", "").isdigit()
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

    # ========================================================
    # LOTE
    # ========================================================

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

    # ========================================================
    # NOME
    # ========================================================

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

    # ========================================================
    # PASTA
    # ========================================================

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

    # ========================================================
    # BOTÕES
    # ========================================================

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

    # ========================================================
    # STATUS
    # ========================================================

    frame_status = tk.Frame(
        conteudo,
        bg=COR_STATUS
    )

    frame_status.pack(
        fill="x"
    )

    label_status = tk.Label(
        frame_status,
        text="Preencha os campos para gerar um arquivo de teste.",
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

    # ========================================================
    # EVENTOS
    # ========================================================

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

    janela.mainloop()


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    main()