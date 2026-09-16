# Portfolio Presentation — Action Plan (Tableau + Repo)

> Documento de trabajo que captura **todo lo pendiente para dejar el proyecto
> presentable** (portfolio), según lo relevado en la revisión del proyecto.
> Estado verificado contra el repo el 2026-09-15.

---

## 1. Estado actual (verificado)

| Ítem | Estado | Nota |
|---|---|---|
| Repo git | ✅ rama `main` | solo `prompt-1` y `prompt-2` sin trackear |
| `.gitignore` | ✅ correcto | excluye `data/raw|interim|processed/*` (los CSV no se publican) |
| `.twb` starter | ✅ existe | `reports/tableau/telecom_churn_dashboard.twb` (4 dashboards, 7 calculated fields) |
| Specs Tableau (data_sources / calculated_fields / wireframes) | ✅ completos | `reports/tableau/` |
| `model_validation.md` | ✅ existe | `reports/insights/` |
| **README.md raíz** | ❌ **falta** | solo existe `data/raw/README.md` |
| **LICENSE** | ❌ **falta** | — |
| **Tableau Public publicado** | ❌ **falta** | no hay link compartible |
| **Demo GIF de pantalla** | ❌ **falta** | no hay nada que grabar aún |

**Conclusión:** la analítica está terminada; lo que falta es el "envoltorio" de
portfolio (README + LICENSE + publicación + demo).

---

## 2. Lo que hay que hacer con TABLEAU

### 2.1 Publicar en Tableau Public
- [ ] Publicar los 4 dashboards en **Tableau Public** (gratis). Da un **link
      compartible/embebible** — el equivalente al badge de "Deployment" del repo
      de referencia.
- [ ] Guardar el link final para embeberlo en el README.

### 2.2 Estrategia de conexión de datos (decidir)
**Nota técnica:** Tableau **no tiene conector nativo a DuckDB**, así que las 11
vistas lógicas (`v_*`) de `sql/views/` no se pueden consumir directamente.

- **Opción A (recomendada para portfolio):** conectar Tableau a un **único
  archivo** `data/processed/clean_customers.csv` (7.043 filas) y hacer la
  agregación *dentro* de Tableau con calculated fields + LODs. Rendimiento
  trivial a 7k filas y demuestra dominio de Tableau (LODs, parámetros, `IIF`).
  Para el mapa se agrega `data/raw/telecom_zipcode_population.csv` por `zip_code`.
- **Opción B (alternativa):** materializar las 11 vistas a CSV en
  `data/processed/` (o `data/tableau/`) y conectar cada hoja a su mart.
  Más "data-engineering", menos vistoso en Tableau.

> Decisión adoptada: **Opción A** como camino principal.

### 2.3 Construir los 4 dashboards
Seguir `reports/tableau/dashboard_wireframes.md` al pie de la letra:
- [ ] (a) Churn Overview — KPIs: 6.589 clientes, 1.869 churned, **28.4%**, ~$63.60.
- [ ] (b) Revenue at Risk — MRR **$137.087/mes**, riesgo 12/24/36m = $1.65M/$3.29M/$4.94M.
- [ ] (c) Retention Drivers — retención 71.6%, combo 3 add-ons **7.2%** vs 35.3%, AUC 0.921.
- [ ] (d) Regional & Infrastructure — mapa coroplético ZIP (San Diego 92122 **97.1%**).

### 2.4 Aplicar calculated fields
Usar `reports/tableau/calculated_fields.md` (ya validadas contra los valores
reales). Mínimo obligatorio: Churn Rate %, MRR Impact, Revenue at Risk 12/24/36m,
CLV, LTV:CAC, Retention Rate.

### 2.5 Resolver los datos "feos"
- [ ] **`monthly_charge` tiene 120 valores negativos** (créditos/reembolsos).
      Decidir: filtrarlos con una nota, **o** mostrarlos explícitamente como
      "créditos". No dejarlos sin control (se ven barras negativas en el histograma).

### 2.6 Higiene de roles de campo
- [ ] `customer_id` → **dimensión** (no medida).
- [ ] `churn` / `is_churned` / `is_joined` / `is_fiber` → **booleanos discretos**.
- [ ] `churn_rate` / `retention_rate` → formato **% a 1 decimal**.
- [ ] `zip_code` → **string** (no integer) para no perder ceros a la izquierda.

### 2.7 Estilo / color (lo que hace que "luzca")
- [ ] Rojo `#D64550` = churn ("malo"); azul = revenue; paleta divergente
      colorblind-safe para lift/heatmaps.
- [ ] Línea de referencia al **28.4%** en todo gráfico de churn rate.
- [ ] Semántica fija: churn-positivo SIEMPRE rojo; retenido/sano azul/verde.

### 2.8 Mapa / geocodificación
- [ ] `zip_code` como string geocodifica solo a ZCTA en Tableau (US).
- [ ] Alternativa: scatter con `latitude`/`longitude` (ya presentes en el dataset).

### 2.9 Licencia del dataset
- [ ] Verificar la **licencia de Maven Analytics** antes de publicar el extract en
      Tableau Public (los datos van embebidos en el workbook publicado).

---

## 3. Lo que hay que hacer con el REPO

### 3.1 README raíz (el archivo más importante)
Crear `README.md` en la raíz con esta estructura (modelo del repo de referencia):

| Sección | Contenido |
|---|---|
| Título + **badges** (shields.io) | Python · DuckDB · Pandas · Tableau |
| **Overview** | 1 párrafo: dataset Maven 7.043 clientes CA, churn 28.4% |
| **Preview** | **GIF** + link a Tableau Public |
| **KPIs destacados** | churn 28.4% · MRR $137k/mes · Fiber 42.1% · 3 add-ons 7.2% |
| **Arquitectura / pipeline** | flujo raw → interim → processed → views → Tableau (ya en `PIPELINE.md`) |
| **Estructura del repo** | árbol de carpetas |
| **Cómo reproducir** | comandos de `PIPELINE.md` (los CSV están gitignored) |
| **Insights / recomendaciones** | resumen de `reports/insights/` |
| **License + Autor/contacto** | — |

### 3.2 LICENSE
- [ ] Añadir `LICENSE` (elegir: MIT es el estándar para portfolio).

### 3.3 Demo GIF de pantalla (cómo grabarlo)
- [ ] Grabar **15–30s** interactuando con los 4 dashboards (filtros, drill-down, mapa).
- [ ] Herramientas:
  - Linux: `peek` o `OBS Studio` + `ffmpeg`.
  - Windows: `ScreenToGif` (exporta GIF directo).
  - Mac: QuickTime → `ffmpeg -i demo.mov -vf "fps=12,scale=900:-1:flags=lanczos" demo.gif`.
- [ ] **Mantener el GIF liviano** (GitHub renderiza mal >10 MB): 800–1000px de ancho,
      10–12 fps, 20s aprox. Objetivo **< 5–8 MB**.
- [ ] Guardar en `reports/` o `assets/` (**no** gitignored) y embeberlo con
      `![preview](ruta.gif)`.

### 3.4 Badges + topics
- [ ] Badges en el README (shields.io): Python, DuckDB, Pandas, Tableau.
- [ ] Configurar **topics** de GitHub (analytics, dashboard, data-visualization,
      tableau, churn).

### 3.5 Notas de reproducción (por el `.gitignore`)
- [ ] El README debe explicar **cómo regenerar `clean_customers.csv`** (los CSV no
      se suben) y/o linkear la fuente pública de Maven Analytics. Sin esto, quien
      clona no puede correr Tableau.

### 3.6 Limpieza y commit
- [ ] Decidir qué hacer con `prompt-1` y `prompt-2` (untracked): trackear, mover a
      `docs/`, o ignorar.
- [ ] Commit + push: `feat: add root README, LICENSE and Tableau Public demo`.

---

## 4. Orden de dependencias (secuencia ganadora)

```
1. Construir/verificar dashboards en Tableau Desktop (abrir el .twb, re-apuntar datos)
        ↓
2. Publicar en Tableau Public  →  obtener link
        ↓
3. Grabar demo GIF de los dashboards publicados
        ↓
4. Escribir README.md (con GIF + link + badges)
        ↓
5. Añadir LICENSE + topics + limpiar archivos sueltos
        ↓
6. Commit final + push
```

> El GIF es el **último** paso de contenido, no el primero: graba el dashboard
> *funcionando*.

---

## 5. Decisiones pendientes de confirmar

1. **Tableau Public vs. solo `.twb`** → recomendado Tableau Public (link + GIF).
2. **Conexión de datos** → recomendado Opción A (un solo `clean_customers.csv`).
3. **Los 120 `monthly_charge` negativos** → ¿filtrar con nota o mostrar como créditos?
4. **Licencia del repo** → recomendado MIT.
5. **Licencia del dataset Maven** → verificar antes de publicar el extract.
