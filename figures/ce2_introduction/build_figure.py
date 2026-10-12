"""Compact online-book adaptation of Jin et al., JACS (2025).

Source: doi:10.1021/jacs.5c07348, Figures 4A and 2, CC BY 4.0.
Changes: selected potential curves, digitized published traces, simplified
presentation, spectrum excerpt and sampling, German labels, new layout.
The data are figure digitizations, not original calculation/instrument files.
"""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
PDF = ROOT.parent.parent / "output" / "pdf" / "ce2_introduction.pdf"
DOI = "https://doi.org/10.1021/jacs.5c07348"
LICENSE = "https://creativecommons.org/licenses/by/4.0/"

INK = "#233444"
MUTED = "#687785"
BLUE = "#255a98"
RED = "#c84949"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 12,
    "axes.labelsize": 12, "axes.titlesize": 15,
    "axes.labelcolor": INK, "axes.edgecolor": MUTED,
    "text.color": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "svg.fonttype": "none", "pdf.fonttype": 42,
})


def potential(name):
    d = np.genfromtxt(DATA / name, delimiter=",", names=True)
    return d["r_A"], d["E_relative_eV"]


def spectrum():
    with (DATA / "spectrum_digitized.csv").open() as f:
        rows = list(csv.DictReader(f))
    def column(name):
        return np.array([float(r[name]) if r[name] else np.nan for r in rows])
    return column("eBE_eV"), column("experiment_relative"), column("simulation_relative")


def style_axis(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["bottom", "left"]].set_linewidth(.8)
    ax.tick_params(length=3, width=.7, pad=5, labelsize=10.5)
    ax.set_facecolor("white")


def build():
    fig = plt.figure(figsize=(11.2, 5.5), facecolor="white")
    fig.text(.067, .943, "Quantenchemie am Ceriumdimer", fontsize=20, weight="medium")

    left = fig.add_axes([.085, .237, .363, .54])
    right = fig.add_axes([.585, .237, .365, .54])
    for ax in [left, right]:
        style_axis(ax)

    x, y = potential("anion_selected_doublet.csv")
    left.plot(x, y, color=BLUE, lw=2.4, label=r"Ce$_2^-$")
    x, y = potential("neutral_selected_lowest_singlet.csv")
    left.plot(x, y, color=RED, lw=2.4, label=r"Ce$_2$")
    left.set_xlim(2.45, 2.9)
    left.set_ylim(0, .4)
    left.set_xticks([2.5, 2.7, 2.9])
    left.set_yticks([0, .2, .4])
    left.set_xlabel("Kernabstand / Å", labelpad=9)
    left.set_ylabel("Relative Energie / eV", labelpad=9)
    left.set_title("Bindung", loc="left", pad=39, weight="medium")
    left.legend(loc="lower left", bbox_to_anchor=(0, 1.025), ncol=2,
                frameon=False, fontsize=11, handlelength=1.5, borderaxespad=0)

    e, experiment, simulation = spectrum()
    # Show the dominant published bands, with unresolved / occluded source
    # pixels left missing. Open circles are display samples of the digitized
    # experimental curve, not newly inferred instrument measurements.
    chosen = np.arange(0, len(e), 14)
    chosen = chosen[(e[chosen] >= .5) & (e[chosen] <= 1.15)
                    & np.isfinite(experiment[chosen])]
    # Retain the highest visible source sample in each main band as well.
    # No missing or occluded values are reconstructed.
    peaks = []
    for lo, hi in [(.65, .78), (.87, .97)]:
        candidates = np.flatnonzero((e >= lo) & (e <= hi)
                                    & np.isfinite(experiment))
        peaks.append(candidates[np.argmax(experiment[candidates])])
    chosen = np.unique(np.concatenate([chosen, peaks]))
    right.plot(e[chosen], experiment[chosen], linestyle="none", marker="o",
               ms=4.4, mfc="white", mec=INK, mew=1.1, label="Experiment", zorder=3)
    shown = (e >= .5) & (e <= 1.15)
    right.plot(e[shown], simulation[shown], color=RED, lw=2.2,
               label="Simulation*", zorder=2)
    right.set_xlim(.5, 1.15)
    right.set_ylim(0, 1.07)
    right.set_xticks([.6, .8, 1.0])
    right.set_yticks([0, .5, 1])
    right.set_xlabel("Elektronenbindungsenergie / eV", labelpad=9)
    right.set_ylabel("Intensität (relativ)", labelpad=9)
    right.set_title("Spektroskopie", loc="left", pad=39, weight="medium")
    right.legend(loc="lower left", bbox_to_anchor=(0, 1.025), ncol=2,
                 frameon=False, fontsize=10.5, handlelength=1.5, borderaxespad=0,
                 columnspacing=1.5)

    fig.text(.586, .1, "* Im Original um −0,24 eV verschoben.",
             fontsize=9.5, color=MUTED)
    fig.text(.067, .034,
             "© 2025 The Authors · Jin et al., JACS · doi:10.1021/jacs.5c07348",
             fontsize=9, color=MUTED, url=DOI)
    fig.text(.95, .034, "CC BY 4.0 · adaptiert", fontsize=9,
             color=MUTED, ha="right", url=LICENSE)

    PNG = ROOT / "ce2_introduction.png"
    SVG = ROOT / "ce2_introduction.svg"
    fig.savefig(PNG, dpi=240, facecolor="white", metadata={
        "Title": "Quantenchemie am Ceriumdimer",
        "Author": "Adapted from Jin et al. (2025), doi:10.1021/jacs.5c07348",
        "Copyright": "2025 The Authors; published by American Chemical Society",
        "License": LICENSE,
        "Description": "Selected published curves digitized and redrawn; spectrum excerpt and display sampling; German labels; new layout. See accompanying caption and provenance.",
    })
    fig.savefig(SVG, facecolor="white", metadata={
        "Title": "Quantenchemie am Ceriumdimer",
        "Creator": "Adapted from Jin et al. (2025)", "Source": DOI,
        "Rights": "Copyright 2025 The Authors. CC BY 4.0: " + LICENSE,
        "Description": "Selected curves from Figures 4A and 2 digitized and redrawn, spectrum excerpt and display sampling, German labels, new layout.",
    })
    PDF.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(PDF, facecolor="white", metadata={
        "Title": "Quantenchemie am Ceriumdimer",
        "Author": "Adapted from Jin et al. (2025)",
        "Subject": DOI + "; copyright 2025 The Authors; CC BY 4.0 " + LICENSE
                   + "; selected curves digitized/redrawn; simplified layout and spectrum excerpt.",
    })
    plt.close(fig)
    print(PNG)
    print(SVG)
    print(PDF)


if __name__ == "__main__":
    build()
