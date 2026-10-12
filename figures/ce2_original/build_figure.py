"""Online-book composition of intact original JACS Figures 2, 3 and 4.

No curves are traced, selected, reconstructed or fitted. No orbital or dynamics
panel is omitted. Each embedded original figure is included in its entirety.
Only placement, display size, section headings and attribution are new.
Source: Jin et al., doi:10.1021/jacs.5c07348; CC BY 4.0.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "original_figures"
PDF = ROOT.parent.parent / "output" / "pdf" / "ce2_original.pdf"
DOI = "https://doi.org/10.1021/jacs.5c07348"
LICENSE = "https://creativecommons.org/licenses/by/4.0/"
INK = "#243849"
MUTED = "#687785"
AUTHOR_LINES = (
    "Jiaye Jin, Nikita Kavka, Tatsuya Chiba, Max Grellmann, Shiying Wang, Marcel Jorewitz,",
    "Kit H. Bowen, Roland Mitric, and Knut R. Asmis",
)
TITLE = "Cerium Dimer Anion and the Contribution of 4f Electrons to Lanthanide Metal-Metal Bonds"
JOURNAL = "Journal of the American Chemical Society 2025, 147 (42), 37977-37984. DOI: 10.1021/jacs.5c07348."
FULL_REFERENCE = " ".join(AUTHOR_LINES) + ". " + TITLE + ". " + JOURNAL

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 12,
    "svg.fonttype": "none", "pdf.fonttype": 42,
})


def place(fig, rect, filename, anchor="C"):
    ax = fig.add_axes(rect)
    # interpolation='none' retains native original images in vector exports.
    ax.imshow(Image.open(ASSETS / filename), interpolation="none")
    ax.set_anchor(anchor)
    ax.axis("off")
    return ax


def build():
    # Extend the canvas below the existing composition so the original panels
    # retain their physical display sizes while the complete citation fits.
    panel_height, reference_height = 13.0, 1.15
    height = panel_height + reference_height
    fig = plt.figure(figsize=(16.5, height), facecolor="white")

    def panel_y(y):
        return (y * panel_height + reference_height) / height

    def panel_rect(rect):
        x, y, w, h = rect
        return [x, panel_y(y), w, h * panel_height / height]

    fig.text(.052, panel_y(.969), "Struktur", fontsize=21, weight="medium", color=INK)
    fig.text(.446, panel_y(.969), "Bindung", fontsize=21, weight="medium", color=INK)
    # Complete Figure 4: every energy curve and both full orbital panels.
    place(fig, panel_rect([.045, .515, .91, .44]), "jacs_figure_4.png", anchor="N")

    fig.text(.052, panel_y(.477), "Spektroskopie", fontsize=21, weight="medium", color=INK)
    fig.text(.426, panel_y(.477), "Dynamik", fontsize=21, weight="medium", color=INK)
    # Complete Figure 2 includes the low-energy inset and stick spectrum.
    place(fig, panel_rect([.045, .086, .322, .365]), "jacs_figure_2.png", anchor="NW")
    # Complete Figure 3 includes all four transients and SO-coupled PESs.
    place(fig, panel_rect([.413, .086, .542, .365]), "jacs_figure_3.png", anchor="NE")

    # One self-contained reference and reuse notice travels with every export.
    reference_lines = [
        (AUTHOR_LINES[0], 11.5, "normal", INK, DOI),
        (AUTHOR_LINES[1] + ".", 11.5, "normal", INK, DOI),
        (TITLE + ".", 11.5, "italic", INK, DOI),
        (JOURNAL, 11.5, "normal", INK, DOI),
        ("Original Figures 2-4. © 2025 The Authors; published by American Chemical Society. CC BY 4.0.",
         10.5, "normal", MUTED, LICENSE),
        ("Änderungen: neue Anordnung, Darstellungsgröße und deutsche Überschriften; Originalabbildungen unverändert.",
         10.5, "normal", MUTED, LICENSE),
    ]
    for line, (label, size, style, color, url) in enumerate(reference_lines):
        fig.text(.052, (1.67 - line * .215) / height, label,
                 fontsize=size, fontstyle=style, color=color, url=url)

    ROOT.mkdir(parents=True, exist_ok=True)
    PDF.parent.mkdir(parents=True, exist_ok=True)
    png = ROOT / "ce2_original.png"
    svg = ROOT / "ce2_original.svg"
    fig.savefig(png, dpi=240, facecolor="white", metadata={
        "Title": "Ceriumdimer: Struktur, Bindung, Spektroskopie und Dynamik",
        "Author": " ".join(AUTHOR_LINES),
        "Copyright": "2025 The Authors. Published by American Chemical Society",
        "License": LICENSE,
        "Description": FULL_REFERENCE + " Intact original scientific figures; new layout, resizing and German section labels. No original panels or data omitted, redrawn or reconstructed.",
    })
    fig.savefig(svg, facecolor="white", metadata={
        "Title": "Ceriumdimer: Struktur, Bindung, Spektroskopie und Dynamik",
        "Creator": " ".join(AUTHOR_LINES),
        "Source": DOI,
        "Rights": "Copyright 2025 The Authors. CC BY 4.0 " + LICENSE,
        "Description": FULL_REFERENCE + " Entire original Figures 4, 2 and 3 rearranged. German section headings added. Scientific image content is unaltered.",
    })
    fig.savefig(PDF, facecolor="white", metadata={
        "Title": "Ceriumdimer: Struktur, Bindung, Spektroskopie und Dynamik",
        "Author": " ".join(AUTHOR_LINES),
        "Subject": FULL_REFERENCE + "; copyright 2025 The Authors; CC BY 4.0 " + LICENSE
                   + "; complete original Figures 2-4; new layout and German headings only.",
    })
    plt.close(fig)
    print(png)
    print(svg)
    print(PDF)


if __name__ == "__main__":
    build()
