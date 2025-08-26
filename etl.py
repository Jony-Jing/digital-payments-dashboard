import pandas as pd
from pathlib import Path

def clean_t1(file_path: Path) -> pd.DataFrame:
    df = pd.read_excel(file_path, sheet_name="T1 - Transactions Per Capita")
    years = pd.to_numeric(df.iloc[1, 3:], errors="coerce").dropna().astype(int)
    row_idx = df[df.iloc[:,1].astype(str).str.strip().str.startswith("E-payments")].index[0]
    values = pd.to_numeric(df.iloc[row_idx, 3:3+len(years)], errors="coerce")
    return pd.DataFrame({"year": years.values, "e_payments_per_capita": values.values})

def clean_t2(file_path: Path) -> pd.DataFrame:
    df = pd.read_excel(file_path, sheet_name="T2.1 - Volume & Value")
    # detect rows
    metric_row = None
    for i in range(0, 12):
        texts = df.iloc[i].astype(str).str.lower()
        if (texts.str.contains("volume").sum() >= 2) and (texts.str.contains("value").sum() >= 2):
            metric_row = i
            break
    if metric_row is None:
        raise RuntimeError("Could not detect metric header row in T2.")
    instr_row = max(0, metric_row - 2)
    instr_vals = df.iloc[instr_row].astype(str).replace({"nan": None}).ffill(axis=0)
    metric_vals = df.iloc[metric_row].astype(str).tolist()
    # year column
    year_col = next((c for c in range(df.shape[1]) if "payment instruments" in str(df.columns[c]).lower()), 1)
    data_start = metric_row + 1
    data_end = data_start
    while data_end < df.shape[0] and not df.iloc[data_end].isna().all():
        data_end += 1
    data = df.iloc[data_start:data_end].reset_index(drop=True)
    base = pd.DataFrame({"period": data.iloc[:, year_col].astype(str).str.strip()})
    base["year"] = pd.to_numeric(base["period"].str.extract(r"(20\d{2})")[0], errors="coerce")
    valid = base["year"].notna()
    base = base[valid].reset_index(drop=True)
    data = data.loc[valid.values].reset_index(drop=True)
    wide = base.copy()
    for c in range(df.shape[1]):
        if c == year_col:
            continue
        inst = str(instr_vals.iloc[c]) if c < len(instr_vals) else ""
        met = metric_vals[c].strip().lower() if c < len(metric_vals) else ""
        if not inst or met not in ("volume","value"):
            continue
        clean_inst = "".join(ch for ch in inst if not ch.isdigit()).strip()
        series = pd.to_numeric(data.iloc[:, c], errors="coerce")
        wide[f"{clean_inst}__{met}"] = series.values
    instruments = sorted(set([c.split("__")[0] for c in wide.columns if "__" in c]))
    parts = []
    for inst in instruments:
        out = wide[["period","year"]].copy()
        out["instrument"] = inst
        out["volume"] = pd.to_numeric(wide.get(f"{inst}__volume"), errors="coerce")
        val = pd.to_numeric(wide.get(f"{inst}__value"), errors="coerce")
        if val is not None:
            val = val * 1_000_000  # RM mil -> RM
        out["value"] = val
        out["avg_txn_value"] = out["value"] / out["volume"]
        parts.append(out)
    return pd.concat(parts, ignore_index=True)

def clean_t5(file_path):
    df = pd.read_excel(file_path, sheet_name="T5 - EFTPOS Terminal & ATM", header=None)
    ncols = df.shape[1]
    labels = {}
    # find label columns in row 2 where cell contains 'EFTPOS' or 'ATM'
    for c in range(ncols):
        cell = str(df.iloc[2, c]).strip()
        if not cell or cell.lower() in ('nan','none'):
            continue
        if 'eftpos' in cell.lower():
            labels['EFTPOS'] = c
        if 'atm' in cell.lower():
            labels['ATM'] = c
    # fallback scanning if not found exactly
    for c in range(ncols):
        cell = str(df.iloc[2,c]).lower()
        if 'atm' in cell and 'ATM' not in labels:
            labels['ATM'] = c
        if 'eftpos' in cell and 'EFTPOS' not in labels:
            labels['EFTPOS'] = c
    pos_rows, atm_rows = [], []
    for name, start_col in labels.items():
        following = [c for c in labels.values() if c > start_col]
        end_col = min(following) - 1 if following else ncols - 1
        for c in range(start_col+1, end_col+1):
            ycell = df.iloc[3, c]
            year = None
            if pd.notna(ycell):
                if hasattr(ycell, 'year'):
                    year = int(ycell.year)
                else:
                    import re
                    m = re.search(r'(20\d{2})', str(ycell))
                    if m:
                        year = int(m.group(1))
            total = df.iloc[5, c] if c < df.shape[1] else None
            per1000 = df.iloc[7, c] if c < df.shape[1] else None
            if name.upper() == 'EFTPOS':
                pos_rows.append({'year': year, 'pos_total': total, 'pos_per_1000': per1000})
            elif name.upper() == 'ATM':
                atm_rows.append({'year': year, 'atm_total': total, 'atm_per_1000': per1000})
    pos_df = pd.DataFrame(pos_rows).dropna(subset=['year']).astype({'year': int})
    atm_df = pd.DataFrame(atm_rows).dropna(subset=['year']).astype({'year': int})
    pos_df = pos_df.groupby('year', as_index=False).agg({'pos_total': 'last', 'pos_per_1000': 'last'})
    atm_df = atm_df.groupby('year', as_index=False).agg({'atm_total': 'last', 'atm_per_1000': 'last'})
    pos_df['pos_per_1000'] = pd.to_numeric(pos_df['pos_per_1000'], errors='coerce')
    atm_df['atm_per_1000'] = pd.to_numeric(atm_df['atm_per_1000'], errors='coerce')
    merged = pd.merge(pos_df[['year','pos_per_1000']], atm_df[['year','atm_per_1000']], on='year', how='outer').sort_values('year').reset_index(drop=True)
    return merged


def run_etl(input_dir: Path, output_dir: Path) -> None:
    t1_fp = input_dir / "T1 - Transactions Per Capita.xlsx"
    t2_fp = input_dir / "T2 - Payment Instruments.xlsx"
    t5_fp = input_dir / "T5 - EFTPOS Terminal & ATM.xlsx"
    t1 = clean_t1(t1_fp)
    t2 = clean_t2(t2_fp)
    t5 = clean_t5(t5_fp)
    shares = (t2.groupby(["year","instrument"])
                .agg(volume=("volume","sum"), value=("value","sum"))
                .reset_index())
    totals = shares.groupby("year")[["volume","value"]].sum().rename(columns={"volume":"year_volume","value":"year_value"})
    shares = shares.join(totals, on="year")
    shares["volume_share"] = shares["volume"] / shares["year_volume"]
    shares["value_share"] = shares["value"] / shares["year_value"]
    dataset = (t2.merge(t1, on="year", how="left")
                 .merge(t5, on="year", how="left"))
    output_dir.mkdir(parents=True, exist_ok=True)
    t1.to_csv(output_dir / "clean_t1.csv", index=False)
    t2.to_csv(output_dir / "clean_t2.csv", index=False)
    t5.to_csv(output_dir / "clean_t5.csv", index=False)
    shares.to_csv(output_dir / "kpi_instrument_share.csv", index=False)
    dataset.to_csv(output_dir / "bnm_payments_powerbi.csv", index=False)

if __name__ == "__main__":
    base = Path(".")
    run_etl(base, base)
