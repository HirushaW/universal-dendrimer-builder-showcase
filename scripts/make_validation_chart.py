#!/usr/bin/env python3
"""
Regenerate the validation benchmark figure in the site's HUD dark theme.

Replaces the old white-background `public/images/ai-validation-benchmarks.png`
so it matches the Fusion-HUD look (deep navy, cyan glow). Data is taken
verbatim from the values shown on /tools/udb/validation/ so the figure stays
faithful to the page (no fabricated numbers).

Run:  python3 scripts/make_validation_chart.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager  # noqa: F401  (ensures default sans is available)

# ── HUD palette ──────────────────────────────────────────────────────────
INK      = "#060e16"   # panel background
CY       = "#2ce8d8"   # UDB (primary)
CY_BR    = "#6ffff2"   # bright accent
AMBER    = "#f5b301"   # literature
RED      = "#ff6b8b"   # threshold
TEXT     = "#cbd5e1"   # slate-300 labels
TITLE    = "#eaf9f7"
GRID     = "#2ce8d8"

# ── Data (from src/pages/tools/udb/validation/index.astro) ───────────────
gens        = ["G1", "G2", "G3", "G4", "G5", "G6"]
atoms       = [84, 228, 516, 1108, 2420, 4548]          # UDB == Maiti (exact, deterministic)
rg_udb      = [7.4, 10.1, 12.4, 15.3, 19.2, 23.8]
# literature Rg (Maiti 2004); G3 is a published range → midpoint + asym error bar
rg_lit_idx  = [2, 3, 4, 5]                               # G3..G6 have lit values
rg_lit_val  = [12.45, 15.1, 20.3, 24.5]
rg_lit_err  = [[0.75, 0.75], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]  # G3 range 11.7-13.2
delta       = [0.18, 0.09, 0.042, 0.022, 0.011, 0.006]  # asphericity δ (UDB)

x = list(range(len(gens)))

plt.rcParams.update({
    "font.size": 10,
    "font.family": "DejaVu Sans",
    "text.color": TEXT,
    "axes.labelcolor": TEXT,
    "xtick.color": TEXT,
    "ytick.color": TEXT,
})

fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.3), dpi=200)
fig.patch.set_facecolor(INK)

def style(ax, title):
    ax.set_facecolor(INK)
    ax.set_title(title, color=TITLE, fontsize=11, fontweight="bold", pad=12)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#1f3a40")
    ax.grid(True, color=GRID, alpha=0.10, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)

# ── Panel 1 · Atom counts (UDB reproduces Maiti exactly) ─────────────────
ax = axes[0]
style(ax, "Atom Count vs Generation")
bars = ax.bar(x, atoms, color=CY, width=0.62, edgecolor=CY_BR, linewidth=0.8, zorder=3)
for xi, a in zip(x, atoms):
    ax.text(xi, a * 1.05, f"{a:,}", ha="center", va="bottom", color=CY_BR, fontsize=8)
ax.set_yscale("log")
ax.set_xticks(x); ax.set_xticklabels(gens)
ax.set_ylabel("Atoms (log scale)")
ax.set_ylim(50, atoms[-1] * 2.2)
ax.text(0.02, 0.96, "UDB = Maiti et al. 2004 (exact)", transform=ax.transAxes,
        color=CY_BR, fontsize=8.5, va="top",
        bbox=dict(boxstyle="round,pad=0.35", fc="#0a1a20", ec=CY, alpha=0.9))

# ── Panel 2 · Radius of gyration UDB vs literature ───────────────────────
ax = axes[1]
style(ax, "Radius of Gyration  (Å)")
ax.plot(x, rg_udb, "-o", color=CY, markerfacecolor=CY_BR, markeredgecolor=CY,
        linewidth=2, markersize=6, label="UDB v1.0", zorder=4)
lit_x = rg_lit_idx
ax.errorbar(lit_x, rg_lit_val, yerr=list(zip(*rg_lit_err)), fmt="s", color=AMBER,
            markersize=6, capsize=4, linewidth=1.5, label="Literature (Maiti 2004)", zorder=3)
ax.set_xticks(x); ax.set_xticklabels(gens)
ax.set_ylabel("R$_g$ (Å)")
ax.legend(facecolor="#0a1a20", edgecolor="#1f3a40", labelcolor=TEXT, fontsize=8.5, loc="upper left")

# ── Panel 3 · Asphericity vs threshold ───────────────────────────────────
ax = axes[2]
style(ax, "Asphericity  δ")
ax.plot(x, delta, "-o", color=CY, markerfacecolor=CY_BR, markeredgecolor=CY,
        linewidth=2, markersize=6, label="UDB δ", zorder=4)
ax.axhline(0.05, color=RED, linestyle="--", linewidth=1.4, label="Threshold δ = 0.05", zorder=2)
ax.fill_between([-0.5, 5.5], 0, 0.05, color=CY, alpha=0.05, zorder=1)
ax.set_xlim(-0.5, 5.5)
ax.set_xticks(x); ax.set_xticklabels(gens)
ax.set_ylabel("δ (0 = perfect sphere)")
ax.legend(facecolor="#0a1a20", edgecolor="#1f3a40", labelcolor=TEXT, fontsize=8.5, loc="upper right")

fig.suptitle("UDB v1.0  -  Validation Against Published Benchmarks",
             color=TITLE, fontsize=13, fontweight="bold", y=1.02)
fig.tight_layout(rect=(0, 0, 1, 0.97))

out = "public/images/ai-validation-benchmarks.png"
fig.savefig(out, facecolor=INK, bbox_inches="tight", pad_inches=0.25)
print("wrote", out)
