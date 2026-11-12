# 07_portafolio/PR04_hoja_ruta.py
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

r = pd.read_csv("PR03_priorizado.csv")
nn = pd.read_csv("PR01_portafolio_marcado.csv")
tco = pd.read_csv("PF02_tco.csv").set_index("codigo")
hr = pd.read_csv("PR05_hoja_ruta.csv")

# Proyectos ejecutados (se excluyen los del cuadrante ④ Sumidero: PR-05, PR-15)
excluidos = set(r[r.cuadrante == "④ Sumidero"]["codigo"])
ejecutados = [c for c in list(nn[nn.no_negociable].codigo) + list(r.codigo) if c not in excluidos]

# Dependencias (proyecto, depende_de)
DEP = [
    ("PR-01", "PR-09"),
    ("PR-06", "PR-09"),
    ("PR-10", "PR-11"),
    ("PR-10", "PR-13"),
    ("PR-14", "PR-08"),
    ("PR-03", "PR-01"),
    ("PR-04", "PR-01"),
    ("PR-04", "PR-03"),
    ("PR-07", "PR-01"),
    ("PR-07", "PR-03"),
]

CAPACIDAD_SIMULTANEA = 3  # Equipo TI de 3 personas + apoyo externo puntual
PRESUPUESTO_ANUAL = 280000  # S/ techo anual acordado con gerencia para portafolio PETI

G = nx.DiGraph()
G.add_nodes_from(ejecutados)
G.add_edges_from([(b, a) for a, b in DEP])  # arista b -> a (b habilita a a)
assert nx.is_directed_acyclic_graph(G), "El grafo contiene ciclos"

nivel = {n: 0 for n in G.nodes}
for n in nx.topological_sort(G):
    for s in G.successors(n):
        nivel[s] = max(nivel[s], nivel[n] + 1)

print("=== NIVELES DE DEPENDENCIA (0 = puede iniciar de inmediato) ===")
for lv in sorted(set(nivel.values())):
    print(f"  Nivel {lv}: {[n for n, v in sorted(nivel.items()) if v == lv]}")

OLAS = {
    "Ola 1 — Fundacional y Cumplimiento (Año 1, S1–S2)": ["PR-13", "PR-09", "PR-02", "PR-11", "PR-01", "PR-08"],
    "Ola 2 — Habilitación e Integración (Año 2, S1–S2)": ["PR-10", "PR-03", "PR-14", "PR-12", "PR-06"],
    "Ola 3 — Explotación y Valor Digital (Año 3, S1–S2)": ["PR-04", "PR-07"],
}

print("\n=== HOJA DE RUTA POR OLAS ===")
errores_dep = 0
for ola, proys in OLAS.items():
    inv = tco.loc[proys, "inv_inicial"].sum()
    capex = tco.loc[proys, "costo_unico"].sum()
    print(f"\n{ola}")
    print(f"  Proyectos: {', '.join(proys)}")
    print(f"  CAPEX (costo único): S/ {capex:,.0f} | Inversión Año 1 de ola: S/ {inv:,.0f}")
    for p in proys:
        prev_olas = [
            x
            for k, v in OLAS.items()
            if list(OLAS).index(k) < list(OLAS).index(ola)
            for x in v
        ]
        pendientes = [d for d in G.predecessors(p) if d not in proys and d not in prev_olas]
        if pendientes:
            errores_dep += 1
            print(f"  ⚠ {p} depende de {pendientes}, no está en esta ola ni en anteriores")

# Verificación mes a mes en PR05_hoja_ruta.csv
print("\n=== VERIFICACIÓN ESTRICTA DE PRECEDENCIAS Y CAPACIDAD (MES A MES) ===")
fin_mes = hr.set_index("Proyecto")["Fin"].to_dict()
ini_mes = hr.set_index("Proyecto")["Inicio"].to_dict()
for p, dep in DEP:
    if ini_mes[p] <= fin_mes[dep]:
        errores_dep += 1
        print(f"  ⚠ {p} inicia en mes {ini_mes[p]} antes de que termine {dep} (mes {fin_mes[dep]})")
print(f"Dependencias rotas detectadas: {errores_dep}")

max_conc = 0
meses_pico = []
for m in range(1, 37):
    activos = hr[(hr["Inicio"] <= m) & (hr["Fin"] >= m)]["Proyecto"].tolist()
    if len(activos) > max_conc:
        max_conc = len(activos)
        meses_pico = [(m, activos)]
    elif len(activos) == max_conc:
        meses_pico.append((m, activos))

print(f"Capacidad simultánea declarada: {CAPACIDAD_SIMULTANEA} proyectos")
print(f"Máximo de proyectos simultáneos observados: {max_conc} (en mes(es): {[m for m, _ in meses_pico]})")
assert max_conc <= CAPACIDAD_SIMULTANEA, "Se excede la capacidad simultánea"
print("✓ Capacidad simultánea respetada en los 36 meses (12 trimestres).")

# Gráfico Gantt de la Hoja de Ruta
fig, ax = plt.subplots(figsize=(12, 6.8))
ola_colors = {
    "Ola 1 — Fundacional y Cumplimiento": "#1E3A8A",
    "Ola 2 — Habilitación e Integración": "#0284C7",
    "Ola 3 — Explotación y Valor Digital": "#059669",
}
hr_plot = hr.iloc[::-1].reset_index(drop=True)

for idx, row in hr_plot.iterrows():
    color = ola_colors.get(row["Ola"], "#475569")
    if row["Proyecto"] in ["PR-02", "PR-09", "PR-11"]:
        hatch = "//"
    else:
        hatch = None
    ax.barh(
        idx,
        row["Duración (meses)"],
        left=row["Inicio"] - 1,
        height=0.62,
        color=color,
        edgecolor="black",
        hatch=hatch,
        alpha=0.88,
    )
    nombre_corto = tco.loc[row["Proyecto"], "nombre"][:36]
    ax.text(
        row["Inicio"] - 1 + row["Duración (meses)"] / 2,
        idx,
        f"{row['Proyecto']} ({row['Duración (meses)']}m)",
        va="center",
        ha="center",
        color="white",
        fontsize=8,
        fontweight="bold",
    )

ax.set_yticks(range(len(hr_plot)))
ax.set_yticklabels([f"{r['Proyecto']} · {tco.loc[r['Proyecto'], 'nombre'][:34]}" for _, r in hr_plot.iterrows()], fontsize=8.5)
ax.set_xlim(0, 36)
ax.set_xticks(range(0, 37, 3))
ax.set_xticklabels([f"M{m}" for m in range(0, 37, 3)], fontsize=8.5)

# Hitos de decisión y límites normativos
for m_hito, label in [(12, "H1 Fin Ola 1"), (24, "H2 Fin Ola 2"), (34, "H3 Cierre PETI")]:
    ax.axvline(m_hito, color="#DC2626", ls="--", lw=1.3)
    ax.text(m_hito + 0.3, len(hr_plot) - 0.4, label, color="#DC2626", fontsize=8, fontweight="bold")

ax.set_xlabel("Horizonte del PETI (Meses 1–36 · 3 Años)", fontsize=10.5, fontweight="bold")
ax.set_title("Hoja de Ruta Plurianual por Olas · AGROEXPORTADORA VALLE VIEJO S.A.C.", fontsize=12.5, fontweight="bold")
ax.grid(axis="x", alpha=0.3)

patches = [mpatches.Patch(color=c, label=k) for k, c in ola_colors.items()]
patches.append(mpatches.Patch(facecolor="#64748B", hatch="//", edgecolor="black", label="No negociable (Normativo/Continuidad)"))
ax.legend(handles=patches, loc="lower left", fontsize=8.5, frameon=True)
plt.tight_layout()
plt.savefig("../graficos/PR_hoja_ruta_gantt.png", dpi=150)
print("Gráfico guardado en ../graficos/PR_hoja_ruta_gantt.png")
