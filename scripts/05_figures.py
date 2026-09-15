"""05 — Publication figures. Every value read from the built tables or stats.json."""
import json, os, sys
import pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator

OUT, FIG = "data/processed", "figures"
os.makedirs(FIG, exist_ok=True)
S = json.load(open(f"{OUT}/stats.json"))
df = pd.read_csv(f"{OUT}/fda_state_year.csv")

# Diverging palette: two poles + neutral midpoint. Polarity data, so hue carries
# direction (lighter vs heavier) and the midpoint is grey, never a third hue.
LIGHT, HEAVY, NEUTRAL = "#2a78d6", "#eb6834", "#9aa0a6"
GRID, INK, MUTE = "#d8dce2", "#1a1d21", "#6b7280"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTE, "text.color": INK,
    "axes.labelcolor": INK, "xtick.color": MUTE, "ytick.color": MUTE,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 200, "savefig.bbox": "tight", "savefig.facecolor": "white"})
DRAFT = not os.path.exists(".gate-signed")


def save(fig, name):
    if DRAFT:
        fig.text(0.99, 0.005, "DRAFT — NOT VERIFIED", ha="right", va="bottom",
                 fontsize=7, color="#b45309", weight="bold")
    for ext in ("png", "pdf"):
        fig.savefig(f"{FIG}/{name}.{ext}")
    plt.close(fig); print(f"  {name}")


L = df[(df.year == S["latest_year"]) & (df.State != "US")].copy()
L = L[L.density_dev.abs() > 0.01].sort_values("density_dev")

# --- Fig 1: the bidirectional finding, with sensitivity bands ---------------
fig, ax = plt.subplots(figsize=(6.6, max(3.2, len(L) * .22)))
y = range(len(L))
colors = [LIGHT if v < 0 else HEAVY for v in L.density_dev]
ax.barh(y, L.density_dev, color=colors, height=.66, zorder=3)
ax.errorbar(L.density_dev, y,
            xerr=[L.density_dev - L.density_dev_low, L.density_dev_high - L.density_dev],
            fmt="none", ecolor=NEUTRAL, elinewidth=1.1, capsize=2, zorder=4, alpha=.85)
ax.axvline(0, color=INK, lw=1.1, zorder=5)
ax.set_yticks(list(y)); ax.set_yticklabels(L.State, fontsize=8)
ax.grid(axis="x", color=GRID, lw=.8); ax.set_axisbelow(True)
ax.set_ylim(-1, len(L))
# Direction belongs on the axis, not floating over the bars.
ax.set_xlabel("←  lighter          Blend density minus certification-fuel reference (kg/m³)"
              "          heavier  →")
# Title and subtitle positioned in POINTS, not axes fractions: this figure's height
# varies with the number of states, so an axes-fraction offset collides on tall runs.
ax.annotate("Bars: midpoint estimate.  Whiskers: full specification-envelope range.\n"
            "Only bars whose whiskers clear zero have a direction the specifications "
            "determine —\nin practice the HVO-blending states. See LIMITATIONS §3.",
            xy=(0, 1), xycoords="axes fraction", xytext=(0, 8),
            textcoords="offset points", fontsize=7.6, color=MUTE, va="bottom")
ax.annotate(f"Divergence from the EPA certification fuel, {S['latest_year']}",
            xy=(0, 1), xycoords="axes fraction", xytext=(0, 34),
            textcoords="offset points", fontsize=11.5, weight="bold",
            color=INK, va="bottom")
save(fig, "fig1_divergence_by_state")

# --- Fig 2: pool composition over time, the two regimes --------------------
PICK = ["CA", "OR", "WA", "MN", "IA"]
fig, axes = plt.subplots(1, len(PICK), figsize=(9.2, 2.5), sharey=True)
for ax, st in zip(axes, PICK):
    d = df[(df.State == st)].sort_values("year")
    ax.stackplot(d.year, d.hvo_share * 100, d.fame_share * 100,
                 colors=[LIGHT, HEAVY], edgecolor="white", lw=.4)
    ax.set_title(st, fontsize=10, weight="bold", pad=4)
    ax.set_xlim(d.year.min(), d.year.max())
    ax.xaxis.set_major_locator(MultipleLocator(4))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{int(v)}"))
    ax.grid(axis="y", color=GRID, lw=.7); ax.set_axisbelow(True)
axes[0].set_ylabel("% of diesel pool")
axes[0].set_ylim(0, 60)
fig.suptitle("Two different fuels, two different policies", x=.005, ha="left",
             fontsize=11.5, weight="bold", y=1.10)
fig.text(.005, .995, "HVO renewable diesel (blue) follows clean-fuel standards on the West Coast.  "
         "FAME biodiesel (orange) follows blending mandates in the Midwest.",
         fontsize=7.8, color=MUTE, ha="left", va="top")
save(fig, "fig2_pool_composition")

# --- Fig 3: national biofuel share, with the accounting break marked -------
us = df[df.State == "US"].sort_values("year")
fig, ax = plt.subplots(figsize=(6.6, 3.1))
ax.plot(us.year, (us.fame_share + us.hvo_share) * 100, color=INK, lw=2,
        marker="o", ms=3.4, mfc="white", mew=1.3, zorder=3)
ax.axvline(S["accounting_break_year"], color=NEUTRAL, ls="--", lw=1.1, zorder=2)
ax.text(S["accounting_break_year"] + .12, ax.get_ylim()[1] * .12,
        f"EIA accounting change\n{S['accounting_break_year']}", fontsize=7.6, color=MUTE)
ax.grid(axis="y", color=GRID, lw=.8); ax.set_axisbelow(True)
ax.xaxis.set_major_locator(MultipleLocator(2))
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{int(v)}"))
ax.set_ylabel("Biofuel share of US diesel pool (%)"); ax.set_xlabel("Year")
ax.set_title("No discontinuity across the accounting change", loc="left",
             fontsize=11.5, weight="bold", pad=20)
ax.text(0, 1.03, "Using DAACP as the denominator. Summing the three component series instead\n"
        f"would overstate the pool by ~{S['naive_overcount_pct_mean']}% from "
        f"{S['accounting_break_year']} onward and manufacture a false break.",
        transform=ax.transAxes, fontsize=7.6, color=MUTE, va="bottom")
save(fig, "fig3_national_share")

print(f"\n{len(os.listdir(FIG))} files")
