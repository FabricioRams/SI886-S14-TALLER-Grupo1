# 07_portafolio/PR03_priorizacion.py
import pandas as pd
import matplotlib.pyplot as plt

PESOS = {
    "contribucion": 0.22,
    "beneficio": 0.18,
    "habilitacion": 0.15,
    "urgencia": 0.13,
    "impacto_social_ambiental": 0.12,
    "riesgo_no_hacer": 0.10,
    "facilidad": 0.05,
    "aceptacion": 0.05,
}
assert abs(sum(PESOS.values()) - 1.0) < 1e-9, "Los pesos deben sumar 1.0"
assert PESOS["impacto_social_ambiental"] >= 0.10, "Impacto social y ambiental >= 10%"

CALIF = pd.DataFrame(
    [
        # codigo, contrib, benef, hab, urg, soc_amb, riesgo, facil, acept
        ("PR-01", 5, 4, 5, 5, 4, 5, 3, 4),  # Sistema Integrado de Trazabilidad (Reemplazo Access)
        ("PR-03", 5, 4, 5, 4, 3, 4, 2, 3),  # Integración Balanza-Planta-ERP
        ("PR-04", 5, 5, 2, 4, 3, 4, 2, 4),  # Portal Digital Exportación B2B
        ("PR-05", 3, 3, 1, 2, 4, 2, 2, 2),  # Portal Productores Asociados (Sumidero)
        ("PR-06", 4, 4, 2, 3, 5, 4, 3, 4),  # Telemetría Riego e Integración Hídrica ANA
        ("PR-07", 4, 4, 1, 3, 3, 3, 3, 3),  # Tablero Gerencial de Campaña y Costos (BI)
        ("PR-08", 3, 3, 3, 3, 2, 4, 4, 4),  # Mesa de Servicio e Inventario ITIL
        ("PR-10", 4, 3, 3, 4, 2, 5, 2, 3),  # Renovación y Segregación de Roles ERP
        ("PR-12", 3, 2, 2, 3, 4, 3, 4, 4),  # Gestión del Conocimiento y Capacitación Seguridad
        ("PR-13", 5, 3, 4, 4, 3, 5, 5, 5),  # Comité de Gobierno de TI (EDM02/APO05)
        ("PR-14", 3, 2, 2, 3, 2, 4, 4, 4),  # Monitoreo Proactivo Red y Servidor Planta
        ("PR-15", 2, 3, 1, 2, 4, 2, 2, 3),  # Portal Autoservicio 380 Temp. (Sumidero)
    ],
    columns=["codigo"] + list(PESOS.keys()),
)

CALIF["puntaje"] = sum(CALIF[c] * w for c, w in PESOS.items()).round(3)
CALIF = CALIF.sort_values("puntaje", ascending=False).reset_index(drop=True)

tco = pd.read_csv("PF02_tco.csv")[["codigo", "nombre", "tco_5", "inv_inicial", "meses"]]
r = CALIF.merge(tco, on="codigo", how="left")

# --- Matriz esfuerzo-impacto ---
r["impacto"] = (
    r.contribucion * 0.40
    + r.beneficio * 0.25
    + r.riesgo_no_hacer * 0.20
    + r.impacto_social_ambiental * 0.15
).round(2)
r["esfuerzo"] = (6 - r.facilidad).round(2)
r["cuadrante"] = [
    "① Ganancia rápida"
    if i >= 3.5 and e < 3.5
    else "② Apuesta mayor"
    if i >= 3.5 and e >= 3.5
    else "③ Relleno"
    if i < 3.5 and e < 3.5
    else "④ Sumidero"
    for i, e in zip(r.impacto, r.esfuerzo)
]

r.to_csv("PR03_priorizado.csv", index=False)

print("=== PORTAFOLIO PRIORIZADO (sin los no negociables) ===")
print(
    r[["codigo", "puntaje", "impacto", "esfuerzo", "cuadrante", "tco_5"]].to_string(
        index=False
    )
)

print("\n=== MATRIZ ESFUERZO-IMPACTO ===")
for c in ["① Ganancia rápida", "② Apuesta mayor", "③ Relleno", "④ Sumidero"]:
    sub = r[r.cuadrante == c]
    print(f"\n{c}: {list(sub.codigo)}")

print("\n-> El cuadrante ④ contiene los candidatos a NO EJECUTAR. Deben declararse")
print("   explícitamente en el plan, con el riesgo que la organización asume.")

fig, ax = plt.subplots(figsize=(10, 7.5))
COL = {
    "① Ganancia rápida": "#16A34A",
    "② Apuesta mayor": "#0EA5E9",
    "③ Relleno": "#94A3B8",
    "④ Sumidero": "#B91C1C",
}

# Sombrear cuadrantes sutilmente
ax.axvspan(0.5, 3.5, ymin=0.5, ymax=1.0, color="#DCFCE7", alpha=0.25)
ax.axvspan(3.5, 5.0, ymin=0.5, ymax=1.0, color="#E0F2FE", alpha=0.25)
ax.axvspan(0.5, 3.5, ymin=0.0, ymax=0.5, color="#F1F5F9", alpha=0.35)
ax.axvspan(3.5, 5.0, ymin=0.0, ymax=0.5, color="#FEE2E2", alpha=0.25)

offsets = {
    "PR-01": (0.0, 0.16),
    "PR-06": (0.18, -0.14),
    "PR-07": (-0.18, -0.12),
    "PR-13": (0.0, 0.14),
    "PR-03": (-0.18, 0.14),
    "PR-04": (0.18, 0.12),
    "PR-10": (0.0, -0.18),
    "PR-08": (0.0, 0.14),
    "PR-12": (-0.16, 0.12),
    "PR-14": (0.16, -0.14),
    "PR-05": (0.0, 0.16),
    "PR-15": (0.0, -0.16),
}

for c, g in r.groupby("cuadrante"):
    ax.scatter(
        g.esfuerzo,
        g.impacto,
        s=g.tco_5 / 180,
        c=COL[c],
        label=c,
        edgecolors="black",
        linewidth=1.1,
        alpha=0.85,
        zorder=4,
    )
    for _, x in g.iterrows():
        dx, dy = offsets.get(x.codigo, (0, 0.12))
        ax.annotate(
            f"{x.codigo}\n({x.puntaje:.2f})",
            (x.esfuerzo + dx, x.impacto + dy),
            fontsize=8.5,
            fontweight="bold",
            ha="center",
            va="center",
            zorder=5,
        )

ax.axhline(3.5, color="#475569", ls="--", lw=1.2, zorder=3)
ax.axvline(3.5, color="#475569", ls="--", lw=1.2, zorder=3)
ax.set_xlim(0.5, 4.8)
ax.set_ylim(2.1, 5.0)
ax.set_xlabel("Esfuerzo de implementación (6 − Facilidad) →", fontsize=11, fontweight="bold")
ax.set_ylabel("Impacto estratégico y socioambiental →", fontsize=11, fontweight="bold")
ax.set_title(
    "Matriz Esfuerzo–Impacto · AGROEXPORTADORA VALLE VIEJO S.A.C.\n(tamaño de burbuja proporcional al TCO a 5 años)",
    fontsize=13,
    fontweight="bold",
    pad=12,
)
ax.legend(loc="lower left", fontsize=9, frameon=True, facecolor="white")
ax.grid(alpha=0.25, zorder=1)
plt.tight_layout()
plt.savefig("../graficos/PR_esfuerzo_impacto.png", dpi=150)
print("\nGráfico guardado en ../graficos/PR_esfuerzo_impacto.png")

