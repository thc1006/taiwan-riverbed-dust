"""濁水溪河床揚塵:同小時跨站「下風 vs 非下風」對比。

識別策略:同一小時內比較「位於河床下風」與「非下風」的測站。東北季風、境外傳輸、
季節、全台性汙染事件同一小時打在所有測站上 → 被小時固定效果差分掉;測站固定效果
吸收各站基準。同一測站在不同小時會在下風/非下風間切換,自己就是自己的對照。

⚠️ 但小時固定效果**拿不掉順風向的空間梯度** —— 河床下風的站往往也是全島上游都市/
工業源與境外傳輸的下風,「下游比較髒」會偽裝成揚塵。兩個對治:

  ① 主結果用**粗顆粒 PM10−PM2.5**:揚塵幾乎全是粗顆粒,都市與境外汙染主要是細顆粒。
  ② **PM2.5 當陰性對照**:若下風效果在粗顆粒出現而 PM2.5 沒有 → 揚塵特有;
     若兩者一樣強 → 只是一般汙染累積,必須否定。

安慰劑:假來源(海上/山區/同軸南北位移)、隨機重排。機制:效果應隨風速放大。
"""
from __future__ import annotations
import numpy as np, pandas as pd
from scipy import stats

# 濁水溪下游裸露河床(揚塵熱點:大城/麥寮、西螺/溪州、二水/林內)
SOURCE = [(23.86, 120.28), (23.84, 120.45), (23.83, 120.60)]
FAKE = {                      # 都不是裸露河床
    "海上":     [(23.85, 119.60)],
    "山區":     [(23.85, 121.15)],
    "北移25km": [(24.08, 120.45)],   # 同軸位移:控制「下游比較髒」
    "南移25km": [(23.61, 120.45)],
}
MAX_KM, ANG_TOL = 40.0, 45.0


def _bearing(la1, lo1, la2, lo2):
    p1, p2 = np.radians(la1), np.radians(la2)
    dl = np.radians(lo2 - lo1)
    y = np.sin(dl) * np.cos(p2)
    x = np.cos(p1) * np.sin(p2) - np.sin(p1) * np.cos(p2) * np.cos(dl)
    return (np.degrees(np.arctan2(y, x)) + 360) % 360


def _km(la1, lo1, la2, lo2):
    dx = (lo2 - lo1) * 111.32 * np.cos(np.radians((la1 + la2) / 2))
    dy = (la2 - la1) * 110.57
    return np.sqrt(dx ** 2 + dy ** 2)


def _angdiff(a, b):
    d = np.abs(a - b) % 360
    return np.minimum(d, 360 - d)


def load(path) -> pd.DataFrame:
    d = pd.read_csv(path)
    for c in ["pm10", "pm2.5", "windspeed", "winddirec", "longitude", "latitude"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["dt"] = pd.to_datetime(d.datacreationdate, errors="coerce")
    d = d.dropna(subset=["dt", "pm10", "pm2.5", "longitude", "latitude"])
    d = d[(d.pm10 >= 0) & (d.pm10 < 1000) & (d["pm2.5"] >= 0)]
    d["coarse"] = (d.pm10 - d["pm2.5"]).clip(lower=0)      # 粗顆粒 ≈ 揚塵訊號
    d["fine"] = d["pm2.5"]                                  # 陰性對照
    return d.drop_duplicates(["sitename", "dt"]).reset_index(drop=True)


def regional_wind(d: pd.DataFrame, src) -> pd.DataFrame:
    """區域風(向量平均),只用來源 60km 內的測站,避免遠處環流稀釋。"""
    w = d.dropna(subset=["winddirec", "windspeed"]).copy()
    near = w.apply(lambda r: min(_km(la, lo, r.latitude, r.longitude) for la, lo in src) <= 60, axis=1)
    w = w[near]
    th = np.radians(w.winddirec)
    w["u"] = -w.windspeed * np.sin(th)     # winddirec = 風的「來向」
    w["v"] = -w.windspeed * np.cos(th)
    g = w.groupby("dt")[["u", "v"]].mean()
    g["reg_spd"] = np.sqrt(g.u ** 2 + g.v ** 2)
    g["blow_to"] = (np.degrees(np.arctan2(g.u, g.v)) + 360) % 360
    return g[["reg_spd", "blow_to"]]


def mark_downwind(d, src, max_km=MAX_KM, ang=ANG_TOL):
    sites = d.groupby("sitename")[["latitude", "longitude"]].first()
    brg, dist = {}, {}
    for s, r in sites.iterrows():
        b = [(_km(la, lo, r.latitude, r.longitude), _bearing(la, lo, r.latitude, r.longitude))
             for la, lo in src]
        dist[s], brg[s] = min(b, key=lambda x: x[0])
    near = d.sitename.map(dist) <= max_km
    return (near & (_angdiff(d.sitename.map(brg).values, d.blow_to.values) <= ang)).astype(int)


def contrast(d, y="coarse", col="dw"):
    """去測站固定效果後,逐小時『下風 − 非下風』之差,再對這些差做 t 檢定。"""
    x = d.copy()
    x["_y"] = x[y] - x.groupby("sitename")[y].transform("mean")
    diffs = [g.loc[g[col] == 1, "_y"].mean() - g.loc[g[col] == 0, "_y"].mean()
             for _, g in x.groupby("dt")
             if (g[col] == 1).sum() >= 1 and (g[col] == 0).sum() >= 3]
    diffs = np.array([v for v in diffs if np.isfinite(v)])
    if len(diffs) < 10:
        return {"n": len(diffs), "mean": np.nan, "t": np.nan, "p": np.nan}
    t, p = stats.ttest_1samp(diffs, 0)
    return {"n": int(len(diffs)), "mean": float(diffs.mean()), "t": float(t), "p": float(p)}


def run(path):
    d = load(path)
    d = d.join(regional_wind(d, SOURCE), on="dt").dropna(subset=["blow_to", "reg_spd"])
    print(f"資料 {len(d)} 筆 | {d.sitename.nunique()} 站 | {d.dt.min()} → {d.dt.max()}")
    print(f"PM10 均 {d.pm10.mean():.1f}   粗顆粒均 {d.coarse.mean():.1f}   PM2.5 均 {d.fine.mean():.1f} µg/m³")

    d["dw"] = mark_downwind(d, SOURCE)
    print(f"下風觀測 {d.dw.sum()}/{len(d)} ({d.dw.mean()*100:.1f}%)，涵蓋 {d[d.dw==1].dt.nunique()} 小時")

    print("\n=== 主檢驗 vs 陰性對照(同小時、已去測站固定效果)===")
    res = {}
    for y, lab in [("coarse", "粗顆粒 PM10−PM2.5 ★主結果"), ("pm10", "PM10(總量)"),
                   ("fine", "PM2.5 ☜陰性對照,揚塵不該推高它")]:
        r = contrast(d, y); res[y] = r
        print(f"  {lab:<28} 差 {r['mean']:+7.2f}  t={r['t']:+5.2f}  p={r['p']:.4f}  ({r['n']} 小時)")

    print("\n=== 安慰劑 A:假來源(粗顆粒;都不該有效果)===")
    for nm, src in FAKE.items():
        dd = d.copy(); dd["dwf"] = mark_downwind(dd, src)
        if dd.dwf.sum() < 50:
            print(f"  {nm:<9} 下風樣本不足({dd.dwf.sum()}),略過"); continue
        rf = contrast(dd, "coarse", "dwf")
        print(f"  {nm:<9} 差 {rf['mean']:+7.2f}  t={rf['t']:+5.2f}  p={rf['p']:.4f}  ({rf['n']} 小時)")

    print("\n=== 安慰劑 B:隨機重排下風標籤(400 次,粗顆粒)===")
    rng = np.random.default_rng(20260725); null = []
    for _ in range(400):
        dd = d.copy()
        dd["dwp"] = dd.groupby("dt").dw.transform(lambda s: rng.permutation(s.values))
        v = contrast(dd, "coarse", "dwp")["mean"]
        if np.isfinite(v): null.append(v)
    null = np.array(null); obs = res["coarse"]["mean"]
    pemp = (np.abs(null) >= abs(obs)).mean()
    print(f"  實際 {obs:+.2f}   虛無 SD={null.std():.2f}   經驗 p={pemp:.4f}")

    print("\n=== 機制:效果是否隨風速放大(揚塵需風力抬升)===")
    for lab, sub in [("低風速(下三分位)", d[d.reg_spd <= d.reg_spd.quantile(.33)]),
                     ("高風速(上三分位)", d[d.reg_spd >= d.reg_spd.quantile(.67)])]:
        rs = contrast(sub, "coarse")
        print(f"  {lab:<16} 差 {rs['mean']:+7.2f}  p={rs['p']:.4f}  ({rs['n']} 小時)")

    print("\n=== 敏感度:距離/角度門檻(研究者自由度)===")
    for mk, ag in [(20, 30), (20, 45), (40, 30), (40, 45), (60, 45)]:
        dd = d.copy(); dd["dws"] = mark_downwind(dd, SOURCE, mk, ag)
        rs = contrast(dd, "coarse", "dws")
        print(f"  ≤{mk}km ±{ag}°  差 {rs['mean']:+7.2f}  p={rs['p']:.4f}  (下風 {dd.dws.sum()})")

    ok = (res["coarse"]["p"] < .05 and res["coarse"]["mean"] > 0 and pemp < .05
          and not (res["fine"]["p"] < .05 and res["fine"]["mean"] > 0))
    print("\n" + "=" * 64)
    print("判定:" + ("✅ 粗顆粒下風效果顯著、PM2.5 陰性對照未同步 → 揚塵訊號成立"
                     if ok else "❌ 未通過 —— 不宣稱發現"))
    return d, res


if __name__ == "__main__":
    import sys
    run(sys.argv[1] if len(sys.argv) > 1 else "winter.csv")
