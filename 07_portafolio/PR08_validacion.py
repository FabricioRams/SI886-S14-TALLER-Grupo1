# 07_portafolio/PR08_validacion.py
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

print("=== PASO F: VALIDACIÓN INTEGRAL DEL PORTAFOLIO, HOJA DE RUTA Y PRESUPUESTO ===\n")

# 1. Validación de Pesos (PR03 / PR02)
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
suma_pesos = sum(PESOS.values())
assert abs(suma_pesos - 1.0) < 1e-9, "Error: pesos no suman 1"
assert PESOS["impacto_social_ambiental"] >= 0.10, "Error: criterio social/ambiental < 10%"
print(f"[OK] Comprobación 1: Suma de pesos = {suma_pesos:.2f} | Impacto social y ambiental = {PESOS['impacto_social_ambiental']:.0%} (>= 10%).")

# 2. Validación de Dependencias y Capacidad (PR04 / PR05)
hr = pd.read_csv("PR05_hoja_ruta.csv")
DEP = [
    ("PR-01", "PR-09"), ("PR-06", "PR-09"),
    ("PR-10", "PR-11"), ("PR-10", "PR-13"),
    ("PR-14", "PR-08"), ("PR-03", "PR-01"),
    ("PR-04", "PR-01"), ("PR-04", "PR-03"),
    ("PR-07", "PR-01"), ("PR-07", "PR-03"),
]
G = nx.DiGraph()
G.add_nodes_from(hr["Proyecto"].tolist())
G.add_edges_from([(b, a) for a, b in DEP])
assert nx.is_directed_acyclic_graph(G), "Error: grafo con ciclos"

ini = hr.set_index("Proyecto")["Inicio"].to_dict()
fin = hr.set_index("Proyecto")["Fin"].to_dict()
rotas = [(p, d) for p, d in DEP if ini[p] <= fin[d]]
assert len(rotas) == 0, f"Error: dependencias rotas {rotas}"

max_conc = max(len(hr[(hr["Inicio"] <= m) & (hr["Fin"] >= m)]) for m in range(1, 37))
assert max_conc <= 3, f"Error: capacidad simultánea excedida ({max_conc} > 3)"
print(f"[OK] Comprobación 2: 0 dependencias rotas en DAG de {len(G.nodes)} proyectos | Concurrencia máx. = {max_conc}/3.")

# 3. Validación Presupuestal contra Línea Base (presupuesto_ti.csv e inversiones_cerradas.csv)
pr = pd.read_csv("PR06_presupuesto.csv")
pt_base = pd.read_csv("../EMPRESA-01-agroexportadora-valle-viejo/presupuesto_ti.csv")
inv_hist = pd.read_csv("../EMPRESA-01-agroexportadora-valle-viejo/inversiones_cerradas.csv")

base_plan = pt_base["planificado"].sum()
base_ejec = pt_base["ejecutado"].sum()
inv_2025 = inv_hist[inv_hist["anio"] == 2025]["ejecutado"].sum()
capex_prom_peti = pr["capex"].mean()

print(f"[OK] Comprobación 3: Presupuesto base TI = S/ {base_plan:,.0f} (ejec. S/ {base_ejec:,.0f}).")
print(f"     CAPEX histórico 2025 (INV01+INV02) = S/ {inv_2025:,.0f} vs CAPEX prom. anual PETI = S/ {capex_prom_peti:,.0f}.")
print(f"     Total PETI 3 años = S/ {pr['total'].sum():,.0f} (rango ±15 %: S/ {pr['rango_min_15'].sum():,.0f} – S/ {pr['rango_max_15'].sum():,.0f}).")

# Gráfico extra 1: Grafo de dependencias por niveles
nivel = {n: 0 for n in G.nodes}
for n in nx.topological_sort(G):
    for s in G.successors(n):
        nivel[s] = max(nivel[s], nivel[n] + 1)

pos = {}
niveles_unicos = sorted(set(nivel.values()))
for lv in niveles_unicos:
    nodos_lv = sorted([n for n, v in nivel.items() if v == lv])
    for i, n in enumerate(nodos_lv):
        y = (len(nodos_lv) - 1) / 2.0 - i
        pos[n] = (lv * 2.2, y * 1.3)

fig, ax = plt.subplots(figsize=(11, 6.2))
nn_set = {"PR-02", "PR-09", "PR-11"}
node_colors = ["#DC2626" if n in nn_set else "#0284C7" if nivel[n] in (1, 2) else "#059669" if nivel[n] == 3 else "#1E3A8A" for n in G.nodes]

nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#475569", arrows=True, arrowsize=18, width=1.6, connectionstyle="arc3,rad=0.06")
nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=1450, edgecolors="black", linewidths=1.2)
nx.draw_networkx_labels(G, pos, ax=ax, font_color="white", font_weight="bold", font_size=9)

for lv in niveles_unicos:
    ax.text(lv * 2.2, 3.85, f"Nivel {lv}", ha="center", fontsize=10, fontweight="bold", color="#334155")

patches = [
    mpatches.Patch(color="#DC2626", label="No negociable (Nivel 0)"),
    mpatches.Patch(color="#1E3A8A", label="Priorizado Nivel 0"),
    mpatches.Patch(color="#0284C7", label="Habilitados (Niveles 1–2)"),
    mpatches.Patch(color="#059669", label="Explotación Final (Nivel 3)"),
]
ax.set_ylim(-4.2, 4.4)
ax.legend(handles=patches, loc="upper right", fontsize=8.5, frameon=True)
ax.set_title("Grafo de Dependencias (DAG) y Niveles Topológicos · AGROEXPORTADORA VALLE VIEJO S.A.C.", fontsize=12, fontweight="bold", pad=14)
ax.axis("off")
plt.tight_layout()
plt.savefig("../graficos/PR_dependencias_dag.png", dpi=150)

# Gráfico extra 2: Comparación Presupuesto Base TI + Histórico vs PETI
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2))
pt_sorted = pt_base.sort_values("ejecutado", ascending=True)
y_pos = range(len(pt_sorted))
ax1.barh([y - 0.18 for y in y_pos], pt_sorted["planificado"], height=0.35, color="#94A3B8", label="Planificado 2025")
ax1.barh([y + 0.18 for y in y_pos], pt_sorted["ejecutado"], height=0.35, color="#1E3A8A", label="Ejecutado 2025")
ax1.set_yticks(list(y_pos))
ax1.set_yticklabels(pt_sorted["partida"], fontsize=8.5)
ax1.set_xlabel("Soles (S/)")
ax1.set_title("Línea Base Presupuesto TI 2025\n(Planificado S/ 412k vs Ejecutado S/ 414.9k)", fontsize=10.5, fontweight="bold")
ax1.legend(fontsize=8)
ax1.grid(axis="x", alpha=0.25)

etiquetas = ["CAPEX Hist.\n2025 (INV01+02)", "PETI Año 1\n(Ola 1)", "PETI Año 2\n(Ola 2)", "PETI Año 3\n(Ola 3)"]
valores = [inv_2025] + pr["total"].tolist()
colores = ["#64748B", "#1E3A8A", "#0284C7", "#059669"]
bars = ax2.bar(etiquetas, valores, color=colores, width=0.55, edgecolor="black")
for b, v in zip(bars, valores):
    ax2.text(b.get_x() + b.get_width() / 2, v + 7000, f"S/ {v:,.0f}", ha="center", fontsize=8.8, fontweight="bold")
ax2.set_ylabel("Soles (S/)")
ax2.set_ylim(0, max(valores) * 1.18)
ax2.set_title("Capacidad Histórica de Inversión vs\nPresupuesto Anual del PETI", fontsize=10.5, fontweight="bold")
ax2.grid(axis="y", alpha=0.25)

plt.tight_layout()
plt.savefig("../graficos/PR_comparacion_presupuesto.png", dpi=150)
print("\n[OK] Gráficos de validación generados en ../graficos/")
