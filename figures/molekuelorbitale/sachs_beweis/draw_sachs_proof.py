"""Vier Tafelbilder zum Satz von Sachs; benötigt nur NumPy und Matplotlib."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch
from matplotlib.path import Path as MplPath
import numpy as np

OUT = Path(__file__).resolve().parent
BG, INK, MUTED = "#fbf8f0", "#243a44", "#66777c"
EDGE, CYCLE, FIXED, PALE = "#177e91", "#c67b23", "#7b69a6", "#d4dad8"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 16,
    "mathtext.fontset": "dejavusans", "svg.fonttype": "path",
    "pdf.fonttype": 42, "savefig.facecolor": BG,
})


def text(ax, x, y, s, size=16, color=INK, **kwargs):
    kwargs.setdefault("ha", "center")
    kwargs.setdefault("va", "center")
    return ax.text(x, y, s, fontsize=size, color=color, **kwargs)


def page(number, title, subtitle):
    fig = plt.figure(figsize=(14, 8), facecolor=BG)
    ax = fig.add_axes([0, 0, 1, 1], xlim=(0, 14), ylim=(0, 8), aspect="equal")
    ax.axis("off")
    text(ax, .65, 7.53, "SATZ VON SACHS", 11, MUTED, ha="left")
    text(ax, 13.35, 7.53, f"{number} / 4", 11, MUTED, ha="right")
    text(ax, .65, 7.00, title, 25, ha="left", fontweight="bold")
    text(ax, .65, 6.48, subtitle, 14, MUTED, ha="left")
    return fig, ax


def node(ax, p, label=None, color=INK, radius=.16):
    ax.add_patch(Circle(p, radius, facecolor=BG, edgecolor=color,
                        linewidth=2.1, zorder=5))
    if label is not None:
        text(ax, *p, str(label), 11, color, zorder=6)


def line(ax, p, q, color=EDGE, background=False):
    ax.plot(*zip(p, q), color=color, lw=1.5 if background else 3.2,
            ls=(0, (3, 4)) if background else "-", zorder=1 if background else 3)


def arrow(ax, p, q, color=EDGE, rad=0, shrink=12):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=18,
                               linewidth=2.3, color=color, shrinkA=shrink,
                               shrinkB=shrink, connectionstyle=f"arc3,rad={rad}",
                               zorder=3))


def loop(ax, p):
    x, y = p
    path = MplPath([(x-.12, y+.11), (x-.72, y+1.05),
                    (x+.72, y+1.05), (x+.12, y+.11)],
                   [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4])
    ax.add_patch(FancyArrowPatch(path=path, arrowstyle="-|>", mutation_scale=17,
                               lw=2.3, color=FIXED, zorder=3))


def polygon(center, radius, n):
    angles = np.pi / 2 - 2 * np.pi * np.arange(n) / n
    return np.asarray(center) + radius * np.column_stack((np.cos(angles), np.sin(angles)))


def directed_cycle(ax, center, radius=.78, n=6, reverse=False):
    pts = polygon(center, radius, n)
    for i in range(n):
        p, q = pts[i], pts[(i+1) % n]
        arrow(ax, q if reverse else p, p if reverse else q, CYCLE, shrink=7)
    for p in pts:
        node(ax, p, color=CYCLE, radius=.09)


def band(ax, s, y=.48, size=17):
    ax.add_patch(FancyBboxPatch((.65, y-.28), 12.7, .56,
                              boxstyle="round,pad=0.04,rounding_size=0.12",
                              facecolor="#eeeade", edgecolor="none"))
    text(ax, 7, y, s, size)


def determinant_picture():
    fig, ax = page(1, "Von der Determinante zu geschlossenen Wegen",
                   r"Ein Term von $\det(\lambda I-A)$: aus jeder Zeile und Spalte genau ein Eintrag.")
    # A connected example: chain 1-2-3-4 with a four-cycle 4-5-6-7-4.
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 3)]
    A = np.zeros((7, 7), dtype=int)
    for i, j in edges:
        A[i, j] = A[j, i] = 1
    sigma = [0, 2, 1, 4, 5, 6, 3]
    colors = [FIXED, EDGE, EDGE, CYCLE, CYCLE, CYCLE, CYCLE]
    step, x0, y0 = .52, 1.60, 5.15
    text(ax, 3.16, 5.85, r"$M=\lambda I-A$", 20)
    for i in range(7):
        text(ax, x0-.62, y0-i*step, str(i+1), 10, MUTED)
        text(ax, x0+i*step, y0+.43, str(i+1), 10, MUTED)
        for j in range(7):
            x, y = x0+j*step, y0-i*step
            chosen = j == sigma[i]
            if chosen:
                ax.add_patch(FancyBboxPatch((x-.22, y-.22), .44, .44,
                    boxstyle="round,pad=0,rounding_size=0.07", facecolor=colors[i],
                    edgecolor="none", alpha=.16))
            value = r"$\lambda$" if i == j else (r"$-1$" if A[i, j] else "$0$")
            text(ax, x, y, value, 17,
                 colors[i] if chosen else (MUTED if A[i, j] or i == j else "#b6bdb9"),
                 fontweight="bold" if chosen else "normal")
    for x, direction in [(x0-.35, 1), (x0+6*step+.35, -1)]:
        ax.plot([x+.12*direction, x, x, x+.12*direction],
                [y0+.27, y0+.27, y0-6*step-.27, y0-6*step-.27], color=INK, lw=1.6)
    arrow(ax, (5.65, 3.75), (6.70, 3.75), INK, shrink=0)
    text(ax, 6.16, 4.15, r"$M_{ij}\ \to\ i\!\to\!j$", 12)
    positions = [(8.0, 4.85), (7.8, 2.80), (9.45, 2.80),
                 (10.85, 4.90), (12.65, 4.90), (12.65, 3.10), (10.85, 3.10)]
    loop(ax, positions[0])
    text(ax, 8.0, 5.92, r"Diagonaleintrag $\lambda$", 12, FIXED)
    arrow(ax, positions[1], positions[2], EDGE, rad=.32)
    arrow(ax, positions[2], positions[1], EDGE, rad=.32)
    for i in range(3, 7):
        arrow(ax, positions[i], positions[sigma[i]], CYCLE)
    for i, p in enumerate(positions):
        node(ax, p, i+1, colors[i])
    text(ax, 3.16, 1.30, r"$M_{11}M_{23}M_{32}M_{45}M_{56}M_{67}M_{74}$", 16)
    text(ax, 10.25, 1.65, "Zerlegung der Permutation", 12, MUTED)
    text(ax, 10.25, 1.25, r"$(1)\,(2\ 3)\,(4\ 5\ 6\ 7)$", 22)
    band(ax, "Ein Pfeil hinein und einer hinaus: Es entstehen nur getrennte Zyklen.")
    return fig


def weights_picture():
    fig, ax = page(2, "Die drei Bausteine und ihre Gewichte",
                   "Matrixeinträge und Permutationsvorzeichen bestimmen gemeinsam den Beitrag.")
    for x in [4.45, 8.65]:
        ax.plot([x, x], [1.0, 6.05], color=PALE, lw=1)
    text(ax, 2.35, 5.88, "Fixpunkt", 19, FIXED, fontweight="bold")
    text(ax, 6.55, 5.88, "Hin- und Rückweg", 19, EDGE, fontweight="bold")
    text(ax, 11.0, 5.88, r"Zyklus mit $r\geq 3$ Knoten", 18, CYCLE, fontweight="bold")
    loop(ax, (2.35, 4.33))
    node(ax, (2.35, 4.33), "$i$", FIXED)
    text(ax, 2.35, 3.60, r"Diagonaleintrag $M_{ii}$", 14, FIXED)
    text(ax, 2.35, 2.75, r"$\lambda$", 34, FIXED)
    text(ax, 2.35, 1.63, "Dieser Knoten wird im\nSachs-Teilgraphen weggelassen.", 14, linespacing=1.5)
    p, q = (5.7, 4.48), (7.4, 4.48)
    arrow(ax, p, q, EDGE, rad=.38)
    arrow(ax, q, p, EDGE, rad=.38)
    node(ax, p, "$i$", EDGE)
    node(ax, q, "$j$", EDGE)
    text(ax, 6.55, 3.60, "Ein Tausch, zwei Matrixeinträge", 13, EDGE)
    text(ax, 6.55, 2.75, r"$(-1)\,(-1)^2=-1$", 22, EDGE)
    text(ax, 6.55, 1.63, "Beide Pfeile gehören zu\nderselben Vertauschung.\nKein zusätzlicher Faktor zwei!", 13, linespacing=1.5)
    directed_cycle(ax, (9.82, 4.52), .66)
    directed_cycle(ax, (12.18, 4.52), .66, reverse=True)
    text(ax, 11, 4.52, "+", 24, CYCLE)
    for x in [9.82, 12.18]:
        text(ax, x, 3.50, r"$-1$", 23, CYCLE)
    text(ax, 11, 2.80, r"Je Richtung: $(-1)^{r-1}(-1)^r=-1$", 14)
    text(ax, 11, 2.12, "Zwei Umlaufrichtungen", 14)
    text(ax, 11, 1.48, r"$-1-1=-2$", 28, CYCLE)
    band(ax, "Eine Kante hat Gewicht −1; ein ungerichteter Zyklus hat Gewicht −2.")
    return fig


def formula_picture():
    fig, ax = page(3, "Unabhängige Komponenten: Gewichte multiplizieren",
                   "Ohne die Pfeilrichtungen bleiben einzelne Kanten und einfache Zyklen übrig.")
    positions = [(1.35, 4.90), (2.5, 4.25), (2.5, 2.75),
                 (4.25, 4.25), (5.85, 4.25), (5.85, 2.75), (4.25, 2.75)]
    for i, j in [(0, 1), (2, 3)]:
        line(ax, positions[i], positions[j], PALE, background=True)
    line(ax, positions[1], positions[2])
    for i, j in [(3, 4), (4, 5), (5, 6), (6, 3)]:
        line(ax, positions[i], positions[j], CYCLE)
    for i, p in enumerate(positions):
        node(ax, p, i+1, PALE if i == 0 else (EDGE if i < 3 else CYCLE))
    text(ax, .80, 5.70, r"Knoten 1 bleibt außerhalb: $\lambda$", 12, FIXED, ha="left")
    text(ax, 2.50, 4.85, r"$-1$", 22, EDGE)
    text(ax, 5.05, 4.85, r"$-2$", 22, CYCLE)
    text(ax, 3.55, 2.26, "Grau gestrichelt: weggelassene Kanten.", 11, MUTED)
    text(ax, 3.55, 1.85, r"$N=7,\quad k=6,\quad m=1,\quad c=1$", 17)
    text(ax, 3.55, 1.25, r"$(-1)\,(-2)\,\lambda=2\lambda$", 26)
    ax.plot([6.75, 6.75], [1.0, 6.0], color=PALE, lw=1)
    text(ax, 10.1, 5.65, "Für einen Sachs-Teilgraphen", 18, fontweight="bold")
    text(ax, 10.1, 4.86, r"$(-1)^m(-2)^c\,\lambda^{N-k}$", 25)
    text(ax, 10.1, 4.20, r"$=(-1)^{m+c}2^c\,\lambda^{N-k}$", 23)
    text(ax, 10.1, 3.33, "$m$: einzelne Kantenkomponenten\n$c$: Zykluskomponenten\n$k$: bedeckte Knoten", 14, linespacing=1.55)
    text(ax, 10.1, 2.26, r"Alle Teilgraphen mit $k$ Knoten addieren:", 14)
    text(ax, 10.1, 1.42, r"$a_k=\sum_{S\in\mathcal{S}_k}(-1)^{m(S)+c(S)}2^{c(S)}$", 23)
    band(ax, r"$P_G(\lambda)=\det(\lambda I-A)=\lambda^N+a_1\lambda^{N-1}+\cdots+a_N$", size=21)
    return fig


def benzene_picture():
    fig, ax = page(4, "Benzol: der konstante Term ist −4",
                   r"Für den konstanten Term müssen alle sechs Knoten bedeckt sein: $k=N=6$.")
    selections = [[(0, 1), (2, 3), (4, 5)], [(1, 2), (3, 4), (5, 0)],
                  [(i, (i+1) % 6) for i in range(6)]]
    centers = [2.55, 7.0, 11.45]
    for index, (x, chosen) in enumerate(zip(centers, selections)):
        color = EDGE if index < 2 else CYCLE
        label = f"Kantenpaarung {index+1}" if index < 2 else "Sechserzyklus"
        text(ax, x, 5.84, label, 19, color, fontweight="bold")
        pts = polygon((x, 4.10), 1.23, 6)
        for i in range(6):
            line(ax, pts[i], pts[(i+1) % 6], PALE, background=True)
        for i, j in chosen:
            line(ax, pts[i], pts[j], color)
        for i, p in enumerate(pts):
            node(ax, p, i+1, color)
        text(ax, x, 2.27, r"$(-1)^3=-1$" if index < 2 else r"$-2$", 27, color)
        text(ax, x, 1.67, r"$m=3,\ c=0$" if index < 2 else r"$m=0,\ c=1$", 14, MUTED)
    for x in [4.77, 9.23]:
        text(ax, x, 4.10, "+", 29)
    text(ax, 7, 1.04, r"$a_6=-1-1-2=-4$", 29, fontweight="bold")
    band(ax, r"$P_{\mathrm{Benzol}}(\lambda)=\lambda^6-6\lambda^4+9\lambda^2-4$", size=22)
    return fig


def main():
    pictures = [
        ("01_determinante_und_pfeile", determinant_picture),
        ("02_bausteine_und_gewichte", weights_picture),
        ("03_sachs_formel", formula_picture),
        ("04_benzol_konstanter_term", benzene_picture),
    ]
    metadata = {"Title": "Ein anschaulicher Beweis des Satzes von Sachs",
                "Creator": None, "Producer": None, "CreationDate": None,
                "ModDate": None}
    with PdfPages(OUT / "sachs_beweis.pdf", metadata=metadata) as pdf:
        for name, draw in pictures:
            fig = draw()
            fig.savefig(OUT / f"{name}.png", dpi=180, metadata={"Software": None})
            fig.savefig(OUT / f"{name}.svg", metadata={"Creator": None, "Date": None})
            pdf.savefig(fig)
            plt.close(fig)
    print(f"Vier PNGs, vier SVGs und eine PDF gespeichert in {OUT}")


if __name__ == "__main__":
    main()
