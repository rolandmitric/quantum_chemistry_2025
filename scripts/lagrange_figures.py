"""Reproducible geometric sketches for the chapter on Lagrange multipliers.

Import one of the three public functions to obtain a Matplotlib Figure, or run
this file to write the PNG assets beneath figures/lagrange_multipliers.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


BLUE = "#2465A6"
ORANGE = "#C66A1B"
INK = "#263442"
MUTED = "#637383"
TEXT_BACKGROUND = {"facecolor": "white", "edgecolor": "none", "alpha": 0.88,
                   "pad": 2}
STYLE = {
    "font.family": "DejaVu Sans",
    "font.size": 13,
    "axes.titlesize": 17,
    "axes.labelsize": 14,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "mathtext.fontset": "dejavusans",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
}


def _axes(ax, limits=(-1.5, 1.7)):
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(*limits)
    ax.set_ylim(*limits)
    ax.set_xlabel(r"$x$", labelpad=3)
    ax.set_ylabel(r"$y$", rotation=0, labelpad=12)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#A8B2BA")
    ax.tick_params(colors=MUTED, length=3)
    ax.set_axisbelow(True)
    ax.grid(color="#E7EBEF", linewidth=0.6)


def _arrow(ax, start, delta, color=INK, linewidth=2.3, zorder=5):
    start = np.asarray(start)
    ax.annotate(
        "", xy=start + np.asarray(delta), xytext=start,
        arrowprops=dict(arrowstyle="-|>", color=color, lw=linewidth,
                        mutation_scale=16, shrinkA=0, shrinkB=0),
        zorder=zorder,
    )


def _point(ax, point):
    ax.plot(*point, "o", color=INK, markeredgecolor="white",
            markeredgewidth=1, markersize=8, zorder=8)


def _circle(ax):
    angle = np.linspace(0, 2 * np.pi, 601)
    ax.plot(np.cos(angle), np.sin(angle), color=ORANGE, lw=2.6, zorder=3)


def unconstrained_displacements():
    """Show the directional differential away from and at a free minimum."""
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(1, 2, figsize=(11.6, 5.8), layout="constrained")
        grid = np.linspace(-1.5, 1.7, 351)
        xx, yy = np.meshgrid(grid, grid)
        for ax in axes:
            _axes(ax)
            contours = ax.contour(xx, yy, xx**2 + yy**2,
                                  levels=[0.16, 0.49, 1, 1.69, 2.56, 3.61],
                                  colors=BLUE, alpha=0.55, linewidths=1.2)
            ax.clabel(contours, levels=[0.49, 1.69], inline=True,
                      fontsize=10, fmt="%g")

        p = np.array([0.8, 0.6])
        ax = axes[0]
        ax.set_title("Beliebiger Punkt", pad=13)
        # The radial directions are the local steepest ascent and descent.
        _arrow(ax, p, 0.63 * p, BLUE)
        _arrow(ax, p, -0.63 * p, BLUE)
        _arrow(ax, p, [-0.48, 0.26], MUTED, linewidth=1.6)
        _arrow(ax, p, [0.05, -0.49], MUTED, linewidth=1.6)
        _point(ax, p)
        ax.annotate(r"$\mathbf{r}$", p, xytext=(7, -17),
                    textcoords="offset points", color=INK)
        ax.text(1.11, 1.13, r"$df>0$", color=BLUE, fontsize=15,
                bbox=TEXT_BACKGROUND)
        ax.text(0.02, -0.02, r"$df<0$", color=BLUE, fontsize=15,
                bbox=TEXT_BACKGROUND)
        ax.text(-1.32, 1.42, r"$f=x^2+y^2$", color=BLUE, fontsize=14,
                bbox=TEXT_BACKGROUND)

        ax = axes[1]
        ax.set_title("Stationärer Punkt", pad=13)
        for angle in np.linspace(0, 2 * np.pi, 8, endpoint=False):
            _arrow(ax, [0, 0], 0.52 * np.array([np.cos(angle), np.sin(angle)]),
                   MUTED, linewidth=1.7)
        _point(ax, [0, 0])
        ax.text(-1.32, 1.42, r"$\nabla f(0,0)=\mathbf{0}$", color=BLUE,
                fontsize=14, bbox=TEXT_BACKGROUND)
        ax.text(0, -0.91, "$df=0$ in jeder Richtung\n(erste Ordnung)",
                color=INK, ha="center", va="center", linespacing=1.6,
                bbox=TEXT_BACKGROUND)
        fig.supxlabel("Pfeile: Richtungen infinitesimaler Verschiebungen",
                      fontsize=12, color=MUTED)
        return fig


def allowed_displacements():
    """Distinguish the tangent differential from a finite step off a circle."""
    with plt.rc_context(STYLE):
        fig, ax = plt.subplots(figsize=(7.6, 6.6), layout="constrained")
        _axes(ax, (-1.4, 1.65))
        _circle(ax)
        p = np.array([1, 1]) / np.sqrt(2)
        tangent = np.array([-p[1], p[0]])
        t = np.linspace(-0.48, 0.9, 2)
        line = p[:, None] + tangent[:, None] * t
        ax.plot(*line, color=ORANGE, lw=1.3, linestyle=(0, (5, 4)), alpha=0.6)
        delta = 0.76 * tangent
        _arrow(ax, p, delta, ORANGE, linewidth=2.8)
        _arrow(ax, p, 0.69 * p, INK, linewidth=2.4)
        endpoint = p + delta
        ax.plot(*endpoint, "o", markersize=6, markerfacecolor="white",
                markeredgecolor=ORANGE, markeredgewidth=1.7, zorder=7)
        _point(ax, p)
        ax.annotate(r"$\mathbf{r}$", p, xytext=(8, -20),
                    textcoords="offset points", fontsize=15, color=INK)
        ax.text(0.12, 0.87, r"$d\mathbf{r}$", color=ORANGE, fontsize=17)
        ax.text(0.06, 1.43, r"$\mathbf{r}+\Delta\mathbf{r}$", color=ORANGE,
                fontsize=14, ha="center")
        ax.annotate("", xy=endpoint, xytext=(0.08, 1.37),
                    arrowprops=dict(arrowstyle="-", lw=0.9, color=ORANGE))
        ax.text(1.18, 1.28, r"$\nabla g$", color=INK, fontsize=17)
        ax.text(-1.25, -1.2, r"$g=x^2+y^2-1=0$", color=ORANGE,
                fontsize=15)
        ax.text(-0.76, -0.11, "$dg=\\nabla g\\cdot d\\mathbf{r}=0$\n"
                "Zulässige Richtung: Tangente", color=INK,
                fontsize=12, linespacing=1.8)
        ax.set_title("Zulässige infinitesimale Verschiebungen", pad=15)
        return fig


def constrained_extremum():
    """Compare a generic feasible point and the exact minimum of x + 2y."""
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(1, 2, figsize=(11.6, 6.25),
                                 layout="constrained")
        p_regular = np.array([np.cos(np.deg2rad(25)), np.sin(np.deg2rad(25))])
        p_minimum = -np.array([1, 2]) / np.sqrt(5)
        gradient_f = np.array([1, 2])
        xline = np.linspace(-1.65, 1.75, 2)

        for ax, point, title in zip(
            axes, (p_regular, p_minimum),
            ("Zulässiger Punkt", "Minimum auf dem Kreis"),
        ):
            _axes(ax, (-1.65, 1.75))
            for value in [-3, -1, 0, 1, 3]:
                ax.plot(xline, (value - xline) / 2, color=BLUE,
                        alpha=0.22, lw=1.05, zorder=1)
            value_at_point = gradient_f @ point
            ax.plot(xline, (value_at_point - xline) / 2,
                    color=BLUE, lw=2.1, zorder=2)
            _circle(ax)
            tangent = np.array([-point[1], point[0]])
            endpoints = point[:, None] + tangent[:, None] * np.array([-0.64, 0.64])
            ax.plot(*endpoints, color=ORANGE, lw=2.2,
                    linestyle=(0, (4, 3)), zorder=4)
            # Both actual gradients use exactly the same geometric scale.
            scale = 0.28
            _arrow(ax, point, scale * gradient_f, BLUE)
            _arrow(ax, point, scale * 2 * point, INK)
            _point(ax, point)
            f_tip = point + scale * gradient_f
            g_tip = point + scale * 2 * point
            ax.annotate(r"$\nabla f$", f_tip, xytext=(5, 8),
                        textcoords="offset points", color=BLUE, fontsize=15)
            ax.annotate(r"$\nabla g$", g_tip, xytext=(8, -8),
                        textcoords="offset points", color=INK, fontsize=15)
            ax.set_title(title, pad=14)
            ax.text(-1.48, 1.45, r"$f=x+2y$", color=BLUE, fontsize=14,
                    bbox=TEXT_BACKGROUND)
            ax.text(-1.48, 1.12, r"$g=x^2+y^2-1=0$", color=ORANGE,
                    fontsize=12, bbox=TEXT_BACKGROUND)

        axes[0].annotate(r"$\mathbf{r}$", p_regular, xytext=(-11, -22),
                         textcoords="offset points", color=INK, fontsize=14)
        axes[1].annotate(r"$\mathbf{r}_{\min}$", p_minimum, xytext=(7, -18),
                         textcoords="offset points", color=INK, fontsize=14)
        axes[0].text(-1.47, -1.44, r"$\nabla f\not\parallel\nabla g$",
                     color=INK, fontsize=15)
        axes[1].text(0.02, -1.48, r"$f_{\min}=-\sqrt{5}$", color=BLUE,
                     fontsize=14, bbox=TEXT_BACKGROUND)
        fig.supxlabel("Blaue Linien: Niveaulinien von f   ·   "
                      "Orange gestrichelt: Tangente\n"
                      "Gradientenpfeile: gemeinsamer Maßstab in beiden Bildern",
                      fontsize=12, color=MUTED, linespacing=1.8)
        return fig


def main():
    output = Path(__file__).resolve().parents[1] / "figures" / "lagrange_multipliers"
    output.mkdir(parents=True, exist_ok=True)
    for builder in (unconstrained_displacements, allowed_displacements,
                    constrained_extremum):
        fig = builder()
        destination = output / f"{builder.__name__}.png"
        fig.savefig(destination, dpi=220, bbox_inches="tight",
                    metadata={"Software": None})
        plt.close(fig)
        print(destination)


if __name__ == "__main__":
    main()
