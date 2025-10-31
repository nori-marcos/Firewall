#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path
import pypandoc

ROOT = Path(__file__).parent.resolve()

DEFAULT_CSL = ROOT / "ieee.csl"
DEFAULT_BIB = ROOT / "references.bib"
CODE_STYLE  = ROOT / "code-style.tex"

# Conjuntos de fontes (main, sans, mono) em ordem de preferência.
# Escolheremos o primeiro trio que exista no sistema.
FONT_CANDIDATES = [
    ("Libertinus Serif", "Libertinus Sans", "DejaVu Sans Mono"),
    ("Noto Serif",       "Noto Sans",       "DejaVu Sans Mono"),
    ("TeX Gyre Termes",  "TeX Gyre Heros",  "DejaVu Sans Mono"),
    ("Times New Roman",  "Arial",           "DejaVu Sans Mono"),
    # último recurso: tudo DejaVu
    ("DejaVu Serif",     "DejaVu Sans",     "DejaVu Sans Mono"),
]

BASE_ARGS = [
    "--standalone",
    "--number-sections",
    "--wrap=preserve",
    "--pdf-engine", "xelatex",
    "--syntax-highlighting=idiomatic",
    "--citeproc",
    "-V", "documentclass=IEEEtran",
    "-V", "classoption=conference",
    "-V", "lang=pt-BR",
    "-V", "babel-lang=brazilian",
]

def fc_list(pattern: str) -> bool:
    """Retorna True se a fonte 'pattern' é encontrada pelo fontconfig (fc-list)."""
    try:
        out = subprocess.run(
            ["fc-list", ":", "family"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True, text=True
        ).stdout
        # fc-list retorna famílias separadas por vírgula; comparação case-insensitive
        families = {f.strip().lower() for line in out.splitlines() for f in line.split(",")}
        return pattern.lower() in families
    except Exception:
        # Se não houver fc-list, não bloqueia; apenas retorna False
        return False

def pick_fonts():
    """Seleciona o primeiro trio de fontes disponível. Retorna tuple[str,str,str] ou None."""
    for main, sans, mono in FONT_CANDIDATES:
        if all(fc_list(f) for f in (main, sans, mono)):
            return (main, sans, mono)
    return None

def ensure_pandoc():
    try:
        pypandoc.get_pandoc_path()
    except OSError:
        print("Pandoc não encontrado — baixando localmente...")
        pypandoc.download_pandoc()

def build_args():
    """Monta os argumentos do Pandoc com o que existir localmente e fontes detectadas."""
    args = BASE_ARGS.copy()

    # bibliografia / csl / cabeçalho opcionais
    if DEFAULT_BIB.exists():
        args += ["--bibliography", str(DEFAULT_BIB)]
    if DEFAULT_CSL.exists():
        args += ["--csl", str(DEFAULT_CSL)]
    if CODE_STYLE.exists():
        args += ["-H", str(CODE_STYLE)]

    # tentar fontes; se não achar, seguimos sem -V mainfont/... (evita fontspec error)
    fonts = pick_fonts()
    if fonts:
        main, sans, mono = fonts
        args += ["-V", f"mainfont={main}",
                 "-V", f"sansfont={sans}",
                 "-V", f"monofont={mono}"]
    else:
        print("⚠ Nenhuma das fontes preferidas encontrada via fc-list; "
              "seguindo sem -V mainfont/sansfont/monofont (pode haver warnings de glifos).")
    return args

def convert_one(md_path: Path):
    md_path = md_path.resolve()
    pdf_path = md_path.with_suffix(".pdf")

    resource_path = os.pathsep.join([str(md_path.parent), str(ROOT)])
    args = build_args()

    try:
        pypandoc.convert_file(
            str(md_path),
            to="pdf",
            format="md",
            outputfile=str(pdf_path),
            extra_args=args + [f"--resource-path={resource_path}"],
        )
        print(f"✔ Gerado: {pdf_path}  (engine: xelatex, classe: IEEEtran[conference])")
        return
    except Exception as e1:
        msg = str(e1)
        # Fallback automático se falhar por fonte/fontspec: tenta de novo sem fontes
        fontspec_trigger = ("fontspec Error" in msg) or ("cannot be found" in msg and "font" in msg.lower())
        if fontspec_trigger:
            print("↻ Tentando novamente sem variáveis de fonte (-V mainfont/sansfont/monofont)...")
            args_no_fonts = [a for a in args if not (isinstance(a, str) and a.startswith(("mainfont=", "sansfont=", "monofont=")))]
            # remove as chaves -V que precedem esses valores
            cleaned = []
            skip_next = False
            for i, a in enumerate(args):
                if skip_next:
                    skip_next = False
                    continue
                if a == "-V" and i + 1 < len(args) and any(
                    args[i+1].startswith(x) for x in ("mainfont=", "sansfont=", "monofont=")
                ):
                    skip_next = True
                    continue
                cleaned.append(a)
            try:
                pypandoc.convert_file(
                    str(md_path),
                    to="pdf",
                    format="md",
                    outputfile=str(pdf_path),
                    extra_args=cleaned + [f"--resource-path={resource_path}"],
                )
                print(f"✔ Gerado: {pdf_path}  (fallback sem fontes explícitas)")
                return
            except Exception as e2:
                raise RuntimeError(
                    f"Falha ao gerar PDF para '{md_path.name}'.\n"
                    f"Dica: instale fontes como 'fonts-libertinus' ou use 'fonts-noto', "
                    f"ou mantenha o fallback sem fontes.\n"
                    f"Erro inicial: {e1}\nErro no fallback: {e2}"
                ) from e2
        # se não foi erro de fonte, propaga
        raise RuntimeError(
            f"Falha ao gerar PDF para '{md_path.name}'.\n"
            f"Dica: verifique o 'xelatex' e se o LaTeX encontra a classe IEEEtran instalada.\n"
            f"Erro: {e1}"
        ) from e1

def main():
    ensure_pandoc()
    for md in ROOT.rglob("*.md"):
        try:
            convert_one(md)
        except Exception as e:
            print(f"✖ Erro em {md}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
