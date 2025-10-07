#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# Rutas
INPUT_JSON = "reporte_datasets.json"
OUTPUT_PDF = "reporte_datasets.pdf"

# Cargar JSON
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

results = data["results"]

# Crear PDF
doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=landscape(letter))
styles = getSampleStyleSheet()
elements = []

# Título
elements.append(Paragraph("<b>Reporte de Exploración de Datasets</b>", styles["Title"]))
elements.append(Spacer(1, 12))
elements.append(Paragraph(f"Generado: {data['generated_at']}", styles["Normal"]))
elements.append(Spacer(1, 24))

# Resumen general
ok_count = sum(1 for r in results if r["ok"])
error_count = len(results) - ok_count
elements.append(Paragraph(f"✅ Archivos OK: {ok_count}", styles["Normal"]))
elements.append(Paragraph(f"❌ Archivos con error: {error_count}", styles["Normal"]))
elements.append(Spacer(1, 24))

# Tabla resumen
table_data = [["Archivo", "Status", "Filas", "Columnas", "% promedio NA", "Error"]]

for r in results:
    status = "OK" if r["ok"] else "ERROR"
    rows = r["summary"]["rows"] if r["ok"] else "-"
    cols = r["summary"]["cols"] if r["ok"] else "-"
    avg_missing = "-"
    if r["ok"]:
        cols_info = r["summary"]["columns"]
        avg_missing = round(sum(c["pct_missing"] for c in cols_info.values()) / max(1, len(cols_info)), 2)
    table_data.append([
        r["path"].split("/")[-2] + "/" + r["path"].split("/")[-1],
        status,
        rows,
        cols,
        avg_missing,
        r.get("error", "")
    ])

# Construir tabla
table = Table(table_data, repeatRows=1, colWidths=[200, 60, 60, 60, 80, 200])
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
    ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
]))
elements.append(table)

# Salto de página y detalle por dataset
elements.append(PageBreak())

for r in results[:30]:  # límite para no explotar el PDF
    if r["ok"]:
        elements.append(Paragraph(f"<b>{r['path']}</b>", styles["Heading3"]))
        s = r["summary"]
        elements.append(Paragraph(f"Filas: {s['rows']} | Columnas: {s['cols']} | Duplicados: {s['n_duplicated_rows']}", styles["Normal"]))
        col_table = [["Columna", "Tipo", "% NA", "Únicos", "Ejemplos"]]
        for cname, cinfo in s["columns"].items():
            col_table.append([
                cname,
                cinfo["dtype"],
                round(cinfo["pct_missing"]*100, 2),
                cinfo["n_unique"],
                ", ".join(map(str, cinfo["sample_values"]))
            ])
        t = Table(col_table, repeatRows=1, colWidths=[120, 60, 60, 60, 300])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 12))
    else:
        elements.append(Paragraph(f"<b>{r['path']}</b> — ERROR: {r['error']}", styles["Normal"]))
        elements.append(Spacer(1, 12))

# Construir PDF
doc.build(elements)
print(f"Reporte PDF generado: {OUTPUT_PDF}")
