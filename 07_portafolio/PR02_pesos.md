# PR02 — Pesos del Modelo de Priorización Multicriterio
**Organización:** AGROEXPORTADORA VALLE VIEJO S.A.C. (Empresa 01)  
**Instancia de acuerdo:** Entrevista 3 con la Gerencia General y Administración y Finanzas (simulada con el docente)  
**Regla metodológica:** Los pesos fueron acordados y fijados **antes** de ejecutar el cálculo de puntajes (`PR03_priorizacion.py`), garantizando objetividad conforme a COBIT 2019 (APO05).

## 1. Registro de Entrevista 3 con la Gerencia (Simulada)

| Pregunta realizada | Respuesta de la Gerencia (Administración y Finanzas) | Impacto en el modelo |
|---|---|---|
| ¿Qué objetivo del periodo es innegociable para el negocio? | Sostener la trazabilidad para los clientes de España, Brasil, Chile y EE. UU. y bajar la reconstrucción documental de 11 a 2 días. | Mayor peso a **Contribución a los objetivos (0.22)**. |
| ¿Cuál es la postura frente a inversiones con desviaciones pasadas (+20.6 % y +24.5 % en 2024-2025)? | Exigir retorno claro y evitar compras reactivas sin acta de conformidad ni medición de beneficios. | Peso sólido a **Beneficio económico (0.18)** y creación del Comité de TI. |
| ¿Qué restricción operativa limita la ejecución paralela? | El equipo de TI tiene solo **3 personas** (Jefe de Sistemas + 2 técnicos) y entre mayo y agosto hay 380 trabajadores en campaña. | Se fija capacidad simultánea de **2 proyectos** (máx. 3 con proveedor externo) y se pondera **Facilidad de ejecución (0.05)**. |
| ¿Qué compromisos ambientales y sociales prioriza la empresa? | Uso responsable de la licencia de agua (ANA) en La Yarada-Los Palos y cumplimiento laboral/seguridad con los 142 fijos y 380 temporales. | Se incorpora **Impacto social y ambiental (0.12)**, superando el mínimo obligatorio del 10 %. |

## 2. Tabla Oficial de Criterios y Pesos Acordados

| # | Criterio | Código en script | Peso | Justificación acordada con la gerencia (derivada del diagnóstico) |
|:---:|:---|:---|---:|:---|
| 1 | **Contribución a los objetivos** | `contribucion` | **0.22** | Prioriza la trazabilidad de exportación y reducción del cierre de campaña de 11 a 2 días (OD-01 y OD-02). |
| 2 | **Beneficio económico** | `beneficio` | **0.18** | Facturación de S/ 47.3 M requiere proteger márgenes y corregir la falta de medición de valor vista en INV01–INV03. |
| 3 | **Habilitación** | `habilitacion` | **0.15** | El diagnóstico mostró sistemas desconectados (Access local, balanza 2012 sin red, ERP aislado); los habilitadores deben ir primero. |
| 4 | **Urgencia** | `urgencia` | **0.13** | Riesgo latente tras la corrupción del maestro Access en 2024 y dependencia de un exempleado para trazabilidad. |
| 5 | **Impacto social y ambiental** | `impacto_social_ambiental` | **0.12** | **Criterio obligatorio (≥ 10 %).** Control hídrico ante ANA en zona árida (Tacna), reducción de papel y formalización de 380 trabajadores de campaña. |
| 6 | **Riesgo de no hacerlo** | `riesgo_no_hacer` | **0.10** | Exposición a pérdida de certificaciones, reclamos de compradores europeos y multas de SENASA/SUNAT/SUNAFIL. |
| 7 | **Facilidad de ejecución** | `facilidad` | **0.05** | **Equipo de TI de 3 personas.** Restricción severa de capacidad interna de gestión e implementación. |
| 8 | **Aceptación organizacional** | `aceptacion` | **0.05** | Ausencia de Comité de TI y alta carga estacional en planta (campaña may–ago) condicionan la absorción del cambio. |
| | **TOTAL** | | **1.00** | **Comprobación: $\sum w_i = 1.00$ (100 %)** |

