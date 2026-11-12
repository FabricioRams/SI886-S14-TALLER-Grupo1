# 07_portafolio/PR06_presupuesto.py
import pandas as pd
import matplotlib.pyplot as plt

tco = pd.read_csv("PF02_tco.csv").set_index("codigo")
hr = pd.read_csv("PR05_hoja_ruta.csv")

CAMBIO_PCT, CONTINGENCIA_PCT = 0.10, 0.12  # gestión del cambio y contingencia
AÑOS = ["Año 1", "Año 2", "Año 3"]

filas = []
for a in AÑOS:
    proys = hr[hr["Año"] == a]["Proyecto"].tolist()
    capex = tco.loc[proys, "costo_unico"].sum()
    entregados = hr[hr["Año"] <= a]["Proyecto"].tolist()
    opex = tco.loc[entregados, "costo_anual"].sum()
    cambio = capex * CAMBIO_PCT
    subtotal = capex + opex + cambio
    contingencia = subtotal * CONTINGENCIA_PCT
    total = subtotal + contingencia
    filas.append(
        {
            "año": a,
            "proyectos": len(proys),
            "capex": capex,
            "opex_acumulado": opex,
            "gestion_cambio": cambio,
            "subtotal": subtotal,
            "contingencia": contingencia,
            "total": total,
            "rango_min_15": total * 0.85,
            "rango_max_15": total * 1.15,
        }
    )

pr = pd.DataFrame(filas)
pr.to_csv("PR06_presupuesto.csv", index=False)

print("=== PRESUPUESTO PLURIANUAL DEL PETI (AGROEXPORTADORA VALLE VIEJO S.A.C.) ===")
print(pr.round(0).to_string(index=False))

total_3a = pr.total.sum()
print(f"\nTOTAL DEL PLAN (3 años): S/ {total_3a:,.0f} (rango ±15 %: S/ {total_3a*0.85:,.0f} – S/ {total_3a*1.15:,.0f})")
print(f"  CAPEX : S/ {pr.capex.sum():,.0f} ({pr.capex.sum()/total_3a:.1%})")
print(f"  OPEX  : S/ {pr.opex_acumulado.sum():,.0f} ({pr.opex_acumulado.sum()/total_3a:.1%})")
print(f"  Cambio: S/ {pr.gestion_cambio.sum():,.0f} ({pr.gestion_cambio.sum()/total_3a:.1%})")
print(f"  Cont. : S/ {pr.contingencia.sum():,.0f} ({pr.contingencia.sum()/total_3a:.1%})")

opex_y1 = pr.opex_acumulado.iloc[0]
opex_y3 = pr.opex_acumulado.iloc[-1]
print(f"\nOPEX acumulado Año 1: S/ {opex_y1:,.0f}")
print(f"OPEX acumulado Año 3: S/ {opex_y3:,.0f} (×{opex_y3/max(opex_y1,1):.2f})")
print("\n-> El OPEX NO BAJA: cada proyecto entregado lo incrementa de forma permanente.")
print("   Este es el compromiso real que la gerencia asume al aprobar el plan.")

# Gráfico de barras apiladas + curva de OPEX acumulado
fig, ax = plt.subplots(figsize=(10.5, 6.2))
ax.bar(pr.año, pr.capex, label="Inversión (CAPEX)", color="#16285C", width=0.5)
ax.bar(
    pr.año,
    pr.opex_acumulado,
    bottom=pr.capex,
    label="Gasto operativo acumulado (OPEX)",
    color="#0EA5E9",
    width=0.5,
)
ax.bar(
    pr.año,
    pr.gestion_cambio,
    bottom=pr.capex + pr.opex_acumulado,
    label="Gestión del cambio (10 % CAPEX)",
    color="#F59E0B",
    width=0.5,
)
ax.bar(
    pr.año,
    pr.contingencia,
    bottom=pr.capex + pr.opex_acumulado + pr.gestion_cambio,
    label="Contingencia (12 %)",
    color="#94A3B8",
    width=0.5,
)

for idx, row in pr.iterrows():
    ax.text(
        idx,
        row["total"] + 7000,
        f"S/ {row['total']:,.0f}",
        ha="center",
        va="bottom",
        fontsize=9.5,
        fontweight="bold",
        color="#0F172A",
    )

ax2 = ax.twinx()
ax2.plot(
    pr.año,
    pr.opex_acumulado,
    "o--",
    color="#B91C1C",
    lw=2.5,
    markersize=8,
    label="Curva de OPEX acumulado",
)
for idx, val in enumerate(pr.opex_acumulado):
    ax2.text(
        idx + 0.08,
        val + 4000,
        f"OPEX: S/ {val:,.0f}",
        color="#B91C1C",
        fontsize=8.5,
        fontweight="bold",
    )

ax2.set_ylabel("OPEX acumulado (S/)", color="#B91C1C", fontweight="bold")
ax2.set_ylim(0, pr.opex_acumulado.max() * 1.45)

ax.set_xlabel("Horizonte del Plan", fontsize=10.5, fontweight="bold")
ax.set_ylabel("Presupuesto anual (S/)", fontsize=10.5, fontweight="bold")
ax.set_ylim(0, pr.total.max() * 1.22)
ax.set_title(
    "Presupuesto Plurianual del PETI y Curva de OPEX Acumulado\nAGROEXPORTADORA VALLE VIEJO S.A.C.",
    fontsize=12.5,
    fontweight="bold",
)

h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=8.5, frameon=True)
ax.grid(axis="y", alpha=0.25)
plt.tight_layout()
plt.savefig("../graficos/PR_presupuesto.png", dpi=150)
print("\nGráfico guardado en ../graficos/PR_presupuesto.png")

