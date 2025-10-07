#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Explorador de datasets Sonora.
Genera un reporte JSON y un CSV resumen por archivo.

Requisitos:
pip install pandas openpyxl python-dateutil tabulate

Uso:
python explorar_datasets.py --root . --out reporte.json

El script escanea CSV y XLSX recursivamente en las carpetas datasets_sonora_csv y datasets_sonora_xlsx
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
from dateutil.parser import parse as dateparse
from tabulate import tabulate

# Ajustes
CSV_ENCODING_TRIES = ['utf-8', 'latin1', 'utf-16']
CSV_CHUNKSIZE = 200_000  # por si hay archivos enormes: cambia si lo necesitas

def try_read_csv(path):
    for enc in CSV_ENCODING_TRIES:
        try:
            # intento con infer_datetime_format disabled (lo haremos manualmente)
            df = pd.read_csv(path, encoding=enc, low_memory=False)
            return df, enc, None
        except Exception as e:
            last_err = e
    return None, None, str(last_err)

def try_read_excel(path):
    try:
        df = pd.read_excel(path)
        return df, None
    except Exception as e:
        return None, str(e)

def detect_date_series(series, sample_n=50):
    """
    Intenta detectar si una columna es fecha y devuelve rango si lo es.
    """
    nonnull = series.dropna().astype(str)
    if nonnull.empty:
        return False, None, None
    sample = nonnull.iloc[:sample_n]
    parsed = []
    for v in sample:
        try:
            dt = dateparse(v, fuzzy=False)
            parsed.append(dt)
        except Exception:
            # no es fecha esta muestra
            return False, None, None
    # si llegamos aquí, al menos el sample fue parseable
    # parse full col (con errors='coerce')
    parsed_full = pd.to_datetime(series, errors='coerce', infer_datetime_format=True)
    if parsed_full.dropna().empty:
        return False, None, None
    return True, parsed_full.min(), parsed_full.max()

def summarize_dataframe(df: pd.DataFrame):
    rows, cols = df.shape
    col_summaries = {}
    for c in df.columns:
        s = df[c]
        n_missing = s.isna().sum()
        pct_missing = float(n_missing) / max(1, rows)
        n_unique = s.nunique(dropna=True)
        sample_vals = s.dropna().astype(str).unique()[:5].tolist()
        # tipo heurístico
        dtype = str(s.dtype)
        is_date, min_date, max_date = detect_date_series(s)
        n_duplicated = s.duplicated().sum()
        col_summaries[c] = {
            'dtype': dtype,
            'missing': int(n_missing),
            'pct_missing': round(pct_missing, 4),
            'n_unique': int(n_unique),
            'sample_values': sample_vals,
            'is_date': bool(is_date),
            'min_date': None if pd.isna(min_date) else str(min_date),
            'max_date': None if pd.isna(max_date) else str(max_date),
            'n_duplicated_cells_in_column': int(n_duplicated)
        }
    # dataset-level:
    n_duplicated_rows = int(df.duplicated().sum())
    memory_bytes = df.memory_usage(deep=True).sum()
    return {
        'rows': int(rows),
        'cols': int(cols),
        'n_duplicated_rows': n_duplicated_rows,
        'memory_bytes': int(memory_bytes),
        'columns': col_summaries
    }

def analyze_file(path: Path):
    ext = path.suffix.lower()
    result = {'path': str(path), 'ok': False, 'error': None, 'read_encoding': None, 'summary': None}
    try:
        if ext == '.csv':
            df, enc, err = try_read_csv(path)
            if df is None:
                result['error'] = f'CSV read error: {err}'
                return result
            result['read_encoding'] = enc
        elif ext in ('.xls', '.xlsx'):
            df, err = try_read_excel(path)
            if df is None:
                result['error'] = f'Excel read error: {err}'
                return result
        else:
            result['error'] = f'extensión no soportada: {ext}'
            return result

        # normalize column names: strip
        df.columns = [str(c).strip() for c in df.columns]

        summary = summarize_dataframe(df)
        result['ok'] = True
        result['summary'] = summary
    except Exception as e:
        result['error'] = str(e)
    return result

def walk_and_analyze(root: Path):
    allowed_ext = {'.csv', '.xls', '.xlsx'}
    results = []
    # opcional: priorizar diccionarios
    for p in root.rglob('*'):
        if p.is_file() and p.suffix.lower() in allowed_ext:
            print(f'Analizando: {p}')
            res = analyze_file(p)
            results.append(res)
    return results

def produce_overview(results):
    # resumen tabular para consola y CSV
    rows = []
    for r in results:
        path = r['path']
        status = 'OK' if r['ok'] else 'ERROR'
        rows_count = r['summary']['rows'] if r['ok'] else None
        cols_count = r['summary']['cols'] if r['ok'] else None
        missing_cols = 0
        pct_avg_missing = None
        if r['ok']:
            cols = r['summary']['columns']
            missing_cols = sum(1 for c in cols.values() if c['pct_missing'] > 0.0)
            pct_avg_missing = round(sum(c['pct_missing'] for c in cols.values()) / max(1, len(cols)), 4)
        rows.append({
            'path': path,
            'status': status,
            'rows': rows_count,
            'cols': cols_count,
            'missing_cols_count': missing_cols,
            'avg_pct_missing_per_col': pct_avg_missing,
            'read_encoding': r.get('read_encoding')
        })
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.', help='directorio raíz que contiene datasets_sonora_*')
    ap.add_argument('--out', default='reporte_datasets.json', help='archivo JSON de salida')
    ap.add_argument('--csv-summary', default='resumen_datasets.csv', help='CSV resumen por archivo')
    args = ap.parse_args()

    root = Path(args.root)
    results = walk_and_analyze(root)
    overview = produce_overview(results)

    # guardar JSON completo
    out_json = Path(args.out)
    with out_json.open('w', encoding='utf-8') as f:
        json.dump({'generated_at': str(datetime.utcnow()), 'results': results}, f, ensure_ascii=False, indent=2)

    # guardar CSV resumen
    df_over = pd.DataFrame(overview)
    df_over.to_csv(args.csv_summary, index=False)

    # imprimir tabla en consola
    print('\nResumen:')
    print(tabulate(df_over.head(200), headers='keys', tablefmt='psql', showindex=False))
    print(f'\nJSON completo: {out_json}')
    print(f'CSV resumen: {args.csv_summary}')
    print('Si quieres, pega aquí (o comparte) el JSON y te ayudo a interpretarlo.')

if __name__ == '__main__':
    main()
