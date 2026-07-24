"""產生圖表（英文標籤避免缺字型；README 為中文）。

兩張圖：看起來像發現的東西，以及三道防線如何把它拆掉。
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from analyze import SOURCE, FAKE, load, regional_wind, mark_downwind, contrast


def make_figures(path="data/winter.csv", outdir="figures") -> list:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    paths = []

    d = load(path)
    d = d.join(regional_wind(d, SOURCE), on="dt").dropna(subset=["blow_to", "reg_spd"])
    d["dw"] = mark_downwind(d, SOURCE)

    # ── Fig 1: main result vs the negative control ──────────────────────────
    labels = ["Coarse PM\n(PM10 − PM2.5)\n★ dust signal", "PM10\n(total)",
              "PM2.5\n☜ negative control\n(dust should NOT move it)"]
    keys = ["coarse", "pm10", "fine"]
    vals, ps = [], []
    for k in keys:
        r = contrast(d, k)
        vals.append(r["mean"]); ps.append(r["p"])
    fig, ax = plt.subplots(figsize=(8.5, 5))
    colors = ["tab:orange", "tab:gray", "tab:red"]
    ax.bar(labels, vals, color=colors)
    for i, (v, p) in enumerate(zip(vals, ps)):
        ax.annotate(f"{v:+.2f}\np={p:.4f}", (i, v), ha="center", va="bottom", fontsize=9)
    ax.axhline(0, color="black", lw=.8)
    ax.set_ylabel("Downwind minus non-downwind (µg/m³)\nsame hour, station fixed effects removed")
    ax.set_title("The negative control fires: fine PM rises almost as much as coarse.\n"
                 "Riverbed dust is coarse — so this is general pollution, not dust.")
    fig.tight_layout(); p_ = out / "fig1_negative_control_fires.png"
    fig.savefig(p_, dpi=140); plt.close(fig); paths.append(p_)

    # ── Fig 2: displaced placebos + wind mechanism ──────────────────────────
    fig, ax = plt.subplots(1, 2, figsize=(12.5, 4.8))
    names = ["REAL\nriverbed"] + list(FAKE)
    srcs = [SOURCE] + list(FAKE.values())
    v2, p2 = [], []
    for src in srcs:
        dd = d.copy(); dd["dwf"] = mark_downwind(dd, src)
        r = contrast(dd, "coarse", "dwf") if dd.dwf.sum() >= 50 else {"mean": np.nan, "p": np.nan}
        v2.append(r["mean"]); p2.append(r["p"])
    cols = ["tab:orange"] + ["tab:blue"] * len(FAKE)
    ax[0].bar(range(len(names)), [0 if np.isnan(v) else v for v in v2], color=cols)
    ax[0].set_xticks(range(len(names)))
    ax[0].set_xticklabels([n.replace("移", "-shift ") for n in names], fontsize=8)
    for i, (v, p) in enumerate(zip(v2, p2)):
        if not np.isnan(v):
            ax[0].annotate(f"{v:+.2f}", (i, v), ha="center", va="bottom", fontsize=9)
    ax[0].axhline(0, color="black", lw=.8)
    ax[0].set_ylabel("Coarse PM, downwind minus other (µg/m³)")
    ax[0].set_title("A FAKE source 25 km north beats the real riverbed\n"
                    "→ the effect is not riverbed-specific")

    lo = d[d.reg_spd <= d.reg_spd.quantile(.33)]
    hi = d[d.reg_spd >= d.reg_spd.quantile(.67)]
    rl, rh = contrast(lo, "coarse"), contrast(hi, "coarse")
    ax[1].bar(["Low wind", "High wind"], [rl["mean"], rh["mean"]],
              color=["tab:blue", "tab:red"])
    for i, r in enumerate([rl, rh]):
        ax[1].annotate(f"{r['mean']:+.2f}\np={r['p']:.3f}", (i, r["mean"]),
                       ha="center", va="bottom", fontsize=9)
    ax[1].axhline(0, color="black", lw=.8)
    ax[1].set_ylabel("Coarse PM, downwind minus other (µg/m³)")
    ax[1].set_title("Mechanism runs BACKWARDS: dust needs wind to lift,\n"
                    "yet the effect only shows at LOW wind")
    fig.tight_layout(); p_ = out / "fig2_placebos_and_mechanism.png"
    fig.savefig(p_, dpi=140); plt.close(fig); paths.append(p_)
    return paths
