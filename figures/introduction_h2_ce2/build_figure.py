"""Source-backed teaching figure: Heitler-London H2 (1927) and Ce2 (2025).

Run with Python, numpy, matplotlib and Pillow. Source excerpts are retained in
source_panels. Spectrum data are digitized from the published Figure 2, not the
underlying experimental records. No illustrative/model curves are substituted.
"""
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
ASSETS = ROOT / "source_panels"
PDF_OUT = REPO / "output" / "pdf" / "h2_ce2_quantum_chemistry.pdf"

INK = "#172e3b"
MUTED = "#586775"
BLUE = "#1e4f8f"
CYAN = "#008aac"
RED = "#ba3330"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 12,
    "svg.fonttype": "none", "pdf.fonttype": 42,
    "axes.labelsize": 12, "axes.titlesize": 14,
    "text.color": INK, "axes.labelcolor": INK,
    "axes.edgecolor": MUTED, "xtick.color": INK, "ytick.color": INK,
})


def add_image(fig, rect, filename):
    ax = fig.add_axes(rect)
    ax.imshow(Image.open(ASSETS / filename))
    ax.axis("off")
    return ax


def text(fig, x, y, s, size=11, color=INK, **kw):
    return fig.text(x, y, s, fontsize=size, color=color, **kw)


def make_figure():
    fig = plt.figure(figsize=(16.4, 10.3), facecolor="white")
    text(fig, .048, .959, "Warum binden Atome?", size=25, weight="medium", va="top")
    text(fig, .048, .917,
         "Von H₂ (1927) zu Ce₂⁻ / Ce₂ (2025): Bindung, Energiekurven und der Vergleich mit dem Experiment",
         size=13, color=MUTED, va="top")

    text(fig, .048, .863, "A   H₂: der Anfang", size=15, weight="medium")
    text(fig, .354, .863, "B   Ce₂⁻ / Ce₂: viele nahe Zustände", size=15, weight="medium")
    text(fig, .684, .863, "C   Spektroskopie testet das Modell", size=15, weight="medium")

    add_image(fig, [.048, .467, .252, .365], "h2_heitler_london_1927_fig1.png")
    add_image(fig, [.354, .452, .278, .383], "ce2_2025_pes_fig4a.png")

    data_path = ROOT / "spectrum_digitized.csv"
    if data_path.exists():
        d = np.genfromtxt(data_path, delimiter=",", names=True)
        ax = fig.add_axes([.696, .505, .266, .307])
        ax.plot(d["eBE_eV"], d["experiment_relative"], color=INK, lw=1.7, label="Experiment")
        ax.plot(d["eBE_eV"], d["simulation_relative"], color=RED, lw=1.7, label="Simulation")
        ax.set_xlim(0, 1.2)
        ax.set_ylim(-.02, 1.08)
        ax.set_xlabel("Elektronenbindungsenergie / eV", labelpad=8)
        ax.set_ylabel("Relative Photoelektronenintensität", labelpad=8)
        ax.set_xticks(np.arange(0, 1.21, .2))
        ax.set_yticks([0, .5, 1])
        ax.legend(frameon=False, loc="upper left", fontsize=10)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=10)
        spectrum_source_note = "Spektrum aus Abb. 2 digitalisiert; gemeinsame Intensitätsskala."
    else:
        add_image(fig, [.674, .481, .295, .354], "ce2_2025_spectrum_fig2.png")
        spectrum_source_note = "Originalspektrum aus Abb. 2; keine Rohmessdaten."

    text(fig, .048, .425,
         "Originalabbildung von Heitler und London (1927).\n"
         "Eα: bindend; Eβ: abstoßend; E₁₁: Coulomb-Anteil.\n"
         "Nullpunkt: zwei getrennte H-Atome; R/a₀ dimensionslos.\n"
         "Historische Energieangabe „Volt“ entspricht hier eV.",
         size=10, color=MUTED, va="top", linespacing=1.45)
    text(fig, .354, .425,
         "SA-CASSCF / XMS-CASPT2, Abb. 4A; relative Energie.\n"
         "Dunkelblau: tiefe Ce₂⁻-Zustände; Hellblau: weitere Ce₂⁻-Zustände;\n"
         "Rot: neutrales Ce₂. Die Energieskala hat einen anderen\n"
         "Nullpunkt als die historischen H₂-Kurven.",
         size=10, color=MUTED, va="top", linespacing=1.45)
    text(fig, .684, .425,
         "SO-CASSCF / Franck-Condon-Simulation, 50 K.\n"
         "Verbreiterung: 0,055 eV; Simulation um −0,24 eV verschoben.\n"
         + spectrum_source_note + "\n"
         "Experiment: Photonenenergie 1,17 eV.",
         size=10, color=MUTED, va="top", linespacing=1.45)

    fig.add_artist(Line2D([.048, .967], [.325, .325], transform=fig.transFigure,
                         color="#cad2d8", lw=.8))
    text(fig, .048, .294, "D   Welche Elektronen tragen zur Bindung bei?", size=15, weight="medium")
    text(fig, .048, .267,
         "Ausgewählte natürliche 4f-Orbitale von Ce₂⁻ aus Abb. 4B/C; Zahlen = Besetzungen, Rot/Blau = Phase der Orbitale.",
         size=10, color=MUTED)
    text(fig, .11, .229, "Tiefe Zustandsfamilie", size=12, color=BLUE, weight="medium")
    text(fig, .416, .229, "Niedrig angeregte Familie", size=12, color=CYAN, weight="medium")
    add_image(fig, [.088, .104, .236, .117], "ce2_2025_4f_phi_pair_fig4b.png")
    add_image(fig, [.4, .104, .236, .117], "ce2_2025_4f_pi_pair_fig4c.png")
    text(fig, .352, .177, "→", size=22, color=MUTED, ha="center")
    text(fig, .352, .215, "≈ 0,1 eV\nhöher", size=10, color=MUTED,
         ha="center", va="top", linespacing=1.2)
    text(fig, .685, .227, "Ein kleiner 4f-Bindungsbeitrag wird möglich.", size=12, weight="medium")
    text(fig, .685, .196,
         "Andere Orbitalbesetzungen verändern die Bindung.\n"
         "Effektive Bindungsordnung: ca. 2,5 → 2,6.\n"
         "Der formale Dreifachbindungsrahmen bleibt erhalten.",
         size=10.5, color=MUTED, va="top", linespacing=1.5)
    text(fig, .685, .119,
         "Weiterer Test: Elektronenaffinität von Ce₂\n"
         "Experiment 0,24 eV · XMS-CASPT2 0,25 eV",
         size=10.5, color=INK, va="top", linespacing=1.5)

    text(fig, .048, .062,
         "Dieselben grundlegenden Fragen - heute mit vielen Elektronen, relativistischen Effekten und Spin-Bahn-Kopplung.",
         size=12, weight="medium")
    text(fig, .048, .033,
         "Quellen: Heitler & London, Z. Phys. 44, 455-472 (1927), doi:10.1007/BF01397394 · "
         "Jin et al., JACS 147, 37977-37984 (2025), doi:10.1021/jacs.5c07348 (CC BY 4.0).",
         size=9, color=MUTED)
    text(fig, .048, .016,
         "Lehrabbildung: Original-H₂-Graph und Ce₂-Ausschnitte aus den veröffentlichten Abbildungen; "
         "keine Modellkurven ergänzt. Eigenständige Anordnung und deutsche Beschriftung.",
         size=8.5, color=MUTED)

    ROOT.mkdir(parents=True, exist_ok=True)
    PDF_OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ROOT / "h2_ce2_quantum_chemistry.png", dpi=220, facecolor="white")
    fig.savefig(ROOT / "h2_ce2_quantum_chemistry.svg", facecolor="white")
    fig.savefig(PDF_OUT, facecolor="white", metadata={
        "Title": "Warum binden Atome? H2 (1927) und Ce2 (2025)",
        "Subject": "Source-backed quantum chemistry teaching figure",
        "Keywords": "Heitler London Ce2 cerium JACS quantum chemistry spectroscopy",
    })
    plt.close(fig)
    print(ROOT / "h2_ce2_quantum_chemistry.png")
    print(ROOT / "h2_ce2_quantum_chemistry.svg")
    print(PDF_OUT)


if __name__ == "__main__":
    make_figure()
