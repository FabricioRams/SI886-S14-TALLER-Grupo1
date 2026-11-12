# 07_portafolio/PR01_no_negociables.py
import pandas as pd

p = pd.read_csv("PF01_portafolio_candidatos.csv")

NO_NEGOCIABLES = {  # codigo: (norma_o_riesgo, plazo_limite, fundamento)
    "PR-02": (
        "D.S. 016-2024-JUS / Ley 29733",
        "2027-Q2 (Año 1 - S2)",
        "Registro de actividades de tratamiento obligatorio para planilla (142), campaña (380) y productores",
    ),
    "PR-09": (
        "Continuidad crítica / Exigencia SENASA-UE",
        "2027-Q1 (Año 1 - S1)",
        "Incidente 2024: pérdida del maestro Access sin respaldo; PC de planta y ERP sin respaldo verificado",
    ),
    "PR-11": (
        "Ley 29733 art. 9 / D.S. 016-2024-JUS",
        "2027-Q2 (Año 1 - S2)",
        "Cuentas admin compartidas, sin 2FA y política de seguridad en borrador hace 2 años",
    ),
}

p["no_negociable"] = p.codigo.isin(NO_NEGOCIABLES)
p["norma_nn"] = p.codigo.map(lambda c: NO_NEGOCIABLES.get(c, (None, None, None))[0])
p["plazo_limite"] = p.codigo.map(lambda c: NO_NEGOCIABLES.get(c, (None, None, None))[1])
p["fundamento_nn"] = p.codigo.map(lambda c: NO_NEGOCIABLES.get(c, (None, None, None))[2])

print("=== PROYECTOS NO NEGOCIABLES (AGROEXPORTADORA VALLE VIEJO S.A.C.) ===")
print(
    p[p.no_negociable][["codigo", "nombre", "norma_nn", "plazo_limite", "fundamento_nn"]].to_string(
        index=False
    )
)
print("\n-> NO entran al modelo de priorización. Se ubican en la hoja de ruta por su plazo,")
print("   con al menos un trimestre de margen antes de la fecha límite.")
print(f"\nProyectos que sí compiten en el modelo: {(~p.no_negociable).sum()}")

p.to_csv("PR01_portafolio_marcado.csv", index=False)

