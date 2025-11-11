import os
import time
from datetime import datetime
import unicodedata
import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.express as px
from PIL import Image

# =========================================
#  Carga opcional de .env (solo desarrollo)
# =========================================
try:
    from dotenv import load_dotenv
    load_dotenv()   # lee MURC_USER y MURC_PASS del archivo .env si existe
except ImportError:
    # si no está instalado en el entorno, no se rompe
    pass

# =========================
#  CONFIGURACIÓN PÁGINA
# =========================
st.set_page_config(
    page_title="MURC - Modelo Unificado de Riesgo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------- ESTILO -----------------
PRIMARY = "#003b73"
ACCENT  = "#00a1e4"
st.markdown(
    f"""
    <style>
    :root {{
        --primary: {PRIMARY};
        --accent:  {ACCENT};
    }}
    header[data-testid="stHeader"] {{
        background: linear-gradient(90deg, var(--primary), var(--accent));
        height: 4px;
    }}
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 1rem;
        max-width: 1200px;
    }}
    h1, h2, h3 {{ color: var(--primary); }}
    .murc-header {{ margin-top: 40px; text-align: center; }}
    .murc-header img {{ margin-bottom: 10px; }}
    .login-container {{
        display: flex; justify-content: center; align-items: center;
        height: 80vh;
    }}
    .login-box {{
        background: #fff; padding: 2rem; border-radius: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1); width: 360px;
    }}
    .stButton>button, .stDownloadButton>button {{
        border-radius: 10px; border: 1px solid #e6e9ef;
        box-shadow: 0 1px 2px rgba(0,0,0,.04);
    }}
    .stDownloadButton>button {{
        background-color: var(--primary) !important; color: #fff !important;
    }}
    .badge-conf {{
        display:inline-block; margin:.25rem 0 1rem 0; padding:4px 10px;
        background:#e0f2fe; color:#075985; border:1px solid #0ea5e9;
        border-radius:999px; font-size:12px; font-weight:600;
    }}
    footer {{ visibility: hidden; }}
    #custom-footer {{
        position: fixed; left:0; right:0; bottom:0;
        background:#f5f7fb; color:#444; border-top:1px solid #e6e9ef;
        padding:6px 16px; font-size:12px; z-index: 9999;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
#  AUTENTICACIÓN (SEGURA)
# =========================
MURC_USER = os.getenv("MURC_USER")
MURC_PASS = os.getenv("MURC_PASS")

def login_view():
    st.markdown('<div class="login-container"><div class="login-box">', unsafe_allow_html=True)
    st.markdown("### 🔐 Iniciar sesión")

    if not MURC_USER or not MURC_PASS:
        st.error("⚠️ La aplicación no tiene credenciales configuradas. Defina MURC_USER y MURC_PASS en el entorno o en .env.")
        st.markdown('</div></div>', unsafe_allow_html=True)
        st.stop()

    with st.form("login_form", clear_on_submit=False):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        ok = st.form_submit_button("Ingresar")
    if ok:
        u_norm = (u or "").strip().lower()
        p_norm = (p or "").strip()
        if (
            u_norm == (MURC_USER or "").strip().lower()
            and p_norm == (MURC_PASS or "").strip()
        ):
            st.session_state["auth"] = True
            st.session_state["user"] = u_norm
            st.success("Acceso concedido.")
            time.sleep(0.6)
            st.rerun()
        else:
            st.error("Credenciales inválidas.")
    st.markdown('</div></div>', unsafe_allow_html=True)

if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    login_view()
    st.stop()

with st.sidebar:
    st.caption(f"Usuario: **{st.session_state.get('user','-')}**")
    if st.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

# =========================
#   ENCABEZADO CON LOGO
# =========================
def header():
    try:
        logo = Image.open("logo_murc.png")
        st.markdown('<div class="murc-header">', unsafe_allow_html=True)
        st.image(logo, width=140)
        st.markdown("<h2>Modelo Unificado de Riesgo Cibernético (MURC)</h2>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception:
        st.markdown("## Modelo Unificado de Riesgo Cibernético (MURC)")

header()
# 👇 aquí cambié el texto
st.markdown('<span class="badge-conf">Versión académica — Prototipo MURC</span>', unsafe_allow_html=True)
st.write("Sube tu archivo Excel con las hojas: `Escaneo`, `CVSSF` y `Criticidad_Activos`.")

# =========================
#   HELPERS
# =========================
def _norm(s: str) -> str:
    if s is None: return ""
    s = str(s)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return s.strip().lower().replace(" ", "").replace("-", "").replace("_", "")

def _to_num(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype("string").str.replace(",", ".", regex=False), errors="coerce")

def _match_col(headers, aliases):
    norm_map = { _norm(h): h for h in headers }
    for alias in aliases:
        a = _norm(alias)
        if a in norm_map:
            return norm_map[a]
        for k, real in norm_map.items():
            if a in k:
                return real
    return None

# =========================
#   FUNCIONES DE NEGOCIO
# =========================
@st.cache_data(show_spinner=False)
def procesar_archivo_bytes(data_bytes: bytes) -> pd.DataFrame:
    xls = pd.ExcelFile(BytesIO(data_bytes), engine="openpyxl")

    # ---- Hoja Escaneo ----
    esc_hdr = pd.read_excel(xls, sheet_name="Escaneo", nrows=0).columns
    id_e  = _match_col(esc_hdr, ["Identificador","ID","Id_vuln","CVE","CVE_ID"])
    act_e = _match_col(esc_hdr, ["Activo","Asset","Equipo","Hostname","Sistema"])
    if not id_e or not act_e:
        raise ValueError(f"No encuentro columnas de Identificador/Activo en hoja Escaneo. Encabezados: {list(esc_hdr)}")

    escaneo_df = pd.read_excel(
        xls, sheet_name="Escaneo",
        usecols=[id_e, act_e],
        dtype={id_e:"string", act_e:"string"}
    ).rename(columns={id_e:"Identificador", act_e:"Activo"})
    escaneo_df["Identificador"] = escaneo_df["Identificador"].str.strip().str.upper()
    escaneo_df["Activo"]        = escaneo_df["Activo"].str.strip().str.upper()

    # ---- Hoja CVSSF ----
    cv_hdr = pd.read_excel(xls, sheet_name="CVSSF", nrows=0).columns
    id_c   = _match_col(cv_hdr, ["Identificador","ID","Id_vuln","CVE","CVE_ID"])
    cvss_c = _match_col(cv_hdr, ["CVSS","CVSS_Base","cvssscore"])
    cvssf_c= _match_col(cv_hdr, ["CVSSF","KEV","Exploitability","Threat_Score"])
    if not id_c or not cvss_c or not cvssf_c:
        raise ValueError(f"No encuentro Identificador/CVSS/CVSSF en hoja CVSSF. Encabezados: {list(cv_hdr)}")

    cvssf_df = pd.read_excel(
        xls, sheet_name="CVSSF",
        usecols=[id_c, cvss_c, cvssf_c],
        dtype={id_c:"string"}
    ).rename(columns={id_c:"Identificador", cvss_c:"CVSS", cvssf_c:"CVSSF"})
    cvssf_df["Identificador"] = cvssf_df["Identificador"].str.strip().str.upper()
    cvssf_df["CVSS"]  = _to_num(cvssf_df["CVSS"])
    cvssf_df["CVSSF"] = _to_num(cvssf_df["CVSSF"])

    # ---- Hoja Criticidad_Activos ----
    cr_hdr = pd.read_excel(xls, sheet_name="Criticidad_Activos", nrows=0).columns
    act_cr  = _match_col(cr_hdr, ["Activo","Asset","Equipo","Hostname","Sistema"])
    crit_cr = _match_col(cr_hdr, ["Criticidad","Criticidad_Activo","Clasificacion","Criticality"])
    if not act_cr or not crit_cr:
        raise ValueError(
            "Usecols no coincide con las columnas, columnas esperadas pero no encontradas: "
            "['Activo','Criticidad'] (hoja: Criticidad_Activos). "
            f"Encabezados detectados: {list(cr_hdr)}"
        )

    criticidad_df = pd.read_excel(
        xls, sheet_name="Criticidad_Activos",
        usecols=[act_cr, crit_cr],
        dtype={act_cr:"string", crit_cr:"string"}
    ).rename(columns={act_cr:"Activo", crit_cr:"Criticidad"})
    criticidad_df["Activo"]     = criticidad_df["Activo"].str.strip().str.upper()
    criticidad_df["Criticidad"] = criticidad_df["Criticidad"].astype("string").str.strip().str.capitalize()

    # ---- Uniones ----
    df = escaneo_df.merge(cvssf_df, on="Identificador", how="left") \
                   .merge(criticidad_df, on="Activo", how="left")

    # ---- Cálculo de riesgo ----
    mapa_criticidad = {"bajo":1, "medio":2, "alto":3, "critico":4, "crítico":4}
    df["Criticidad_num"]  = df["Criticidad"].astype("string").str.lower().map(mapa_criticidad)
    df["cvss_norm"]       = df["CVSS"] / 10
    df["cvssf_norm"]      = df["CVSSF"] / 4096
    df["criticidad_norm"] = df["Criticidad_num"] / 4

    df["riesgo"] = (
        0.5*df["cvss_norm"].fillna(0) +
        0.3*df["cvssf_norm"].fillna(0) +
        0.2*df["criticidad_norm"].fillna(0)
    )

    bins   = [-1, 0.25, 0.50, 0.75, float("inf")]
    labels = ["BAJO","MEDIO","ALTO","CRÍTICO"]
    df["Nivel de Exposición"] = pd.cut(df["riesgo"].fillna(-1), bins=bins, labels=labels).astype("string")
    df["Nivel de Exposición"] = df["Nivel de Exposición"].fillna("SIN DATO")

    columnas = ["Activo","Identificador","CVSS","CVSSF","Criticidad","riesgo","Nivel de Exposición"]
    return df[columnas].drop_duplicates().reset_index(drop=True)

# =========================
#       INTERFAZ UI
# =========================
archivo_subido = st.file_uploader("Selecciona un archivo Excel", type=["xlsx"])

if archivo_subido:
    try:
        with st.spinner("Procesando archivo..."):
            data_bytes = archivo_subido.getvalue()
            resultado = procesar_archivo_bytes(data_bytes)

        st.success("✅ Archivo procesado con éxito.")

        # -------- Filtros --------
        with st.expander("🔎 Filtros", expanded=True):
            colf1, colf2, colf3 = st.columns([1,1,2])
            niveles = sorted(resultado["Nivel de Exposición"].dropna().unique().tolist())
            criticidades = sorted(resultado["Criticidad"].dropna().unique().tolist())
            sel_niveles = colf1.multiselect("Nivel de Exposición", niveles, default=niveles)
            sel_critic  = colf2.multiselect("Criticidad", criticidades, default=criticidades)
            buscar_activo = colf3.text_input("Buscar por nombre de activo (contiene):").strip().upper()

        df_filt = resultado.copy()
        if sel_niveles:   df_filt = df_filt[df_filt["Nivel de Exposición"].isin(sel_niveles)]
        if sel_critic:    df_filt = df_filt[df_filt["Criticidad"].isin(sel_critic)]
        if buscar_activo: df_filt = df_filt[df_filt["Activo"].str.contains(buscar_activo, na=False)]

        # -------- Justificación (solo visible) --------
        just = (
            "La exposición se clasifica como " + df_filt["Nivel de Exposición"].astype("string").fillna("SIN DATO") +
            " porque la vulnerabilidad " + df_filt["Identificador"].astype("string").fillna("No asignado") +
            " tiene CVSS " + df_filt["CVSS"].round(2).astype("string").replace({"nan":"s/d"}) +
            ", CVSSF " + df_filt["CVSSF"].round(0).astype("Int64").astype("string").replace({"<NA>":"s/d"}) +
            " y afecta al activo " + df_filt["Activo"].astype("string").fillna("Sin nombre") +
            " con criticidad " + df_filt["Criticidad"].astype("string").fillna("Sin dato") + "."
        )
        df_filt = df_filt.assign(Justificación=just)

        # -------- KPIs --------
        c1, c2, c3, c4, c5 = st.columns(5)
        total = len(df_filt)
        c1.metric("Activos (filtrados)", f"{total:,}".replace(",", "."))
        for col, label in zip([c2,c3,c4,c5], ["BAJO","MEDIO","ALTO","CRÍTICO"]):
            col.metric(f"{label}", int((df_filt["Nivel de Exposición"]==label).sum()))

        st.divider()

        # -------- Tabla --------
        st.subheader("📄 Resultados")
        st.dataframe(df_filt, use_container_width=True, height=420)

        # -------- Gráficos (Plotly) --------
        st.subheader("📈 Visualizaciones")

        colores_nivel = {
            "BAJO": "#2ca02c", "MEDIO": "#ff7f0e",
            "ALTO": "#d62728", "CRÍTICO": "#8b0000",
            "SIN DATO": "#808080"
        }
        colores_critic = {
            "Bajo": "#2ca02c", "Medio": "#ff7f0e",
            "Alto": "#d62728", "Critico": "#8b0000",
            "Sin dato": "#808080"
        }

        # Barras por nivel
        conteo_nivel = df_filt.groupby("Nivel de Exposición", dropna=False).size().reset_index(name="Cantidad")
        orden_niveles = ["BAJO","MEDIO","ALTO","CRÍTICO","SIN DATO"]
        conteo_nivel["Nivel de Exposición"] = pd.Categorical(conteo_nivel["Nivel de Exposición"], categories=orden_niveles, ordered=True)
        fig_barras = px.bar(
            conteo_nivel.sort_values("Nivel de Exposición"),
            x="Nivel de Exposición", y="Cantidad",
            color="Nivel de Exposición",
            color_discrete_map=colores_nivel,
            text="Cantidad", height=360
        )
        fig_barras.update_layout(showlegend=False, margin=dict(l=10,r=10,t=30,b=10))
        fig_barras.update_traces(textposition="outside")

        # Donut por criticidad
        dist_critic = (
            df_filt.assign(Criticidad=df_filt["Criticidad"].astype("string"))
                  .groupby("Criticidad", dropna=False)
                  .size().reset_index(name="Cantidad")
        )
        dist_critic["Criticidad"] = dist_critic["Criticidad"].fillna("Sin dato")
        fig_donut = px.pie(
            dist_critic, names="Criticidad", values="Cantidad",
            hole=0.55, color="Criticidad",
            color_discrete_map=colores_critic, height=360
        )
        fig_donut.update_layout(margin=dict(l=10,r=10,t=30,b=10))

        # Scatter
        agrup = (
            df_filt
            .groupby("Activo", dropna=False)
            .agg(
                prom_riesgo=("riesgo","mean"),
                suma_cvssf=("CVSSF","sum"),
                suma_cvss=("CVSS","sum"),
                count_vuln=("Identificador","size"),
                nivel=("Nivel de Exposición","first"),
                critic=("Criticidad","first")
            )
            .reset_index()
        )
        fig_scatter = px.scatter(
            agrup,
            x="count_vuln",
            y="suma_cvssf",
            color="nivel",
            color_discrete_map=colores_nivel,
            size="suma_cvss", size_max=32,
            hover_data={
                "Activo": True, "critic": True, "nivel": True,
                "prom_riesgo": ":.2f", "suma_cvssf": ":.0f", "suma_cvss": ":.2f", "count_vuln": True
            },
            labels={
                "count_vuln": "Cantidad de vulnerabilidades",
                "suma_cvssf": "Suma de CVSSF",
                "nivel": "Nivel de Exposición",
                "critic": "Criticidad"
            },
            height=460
        )
        y_max = max(agrup["suma_cvssf"].max(), 1)
        y_lim = y_max * 1.15
        fig_scatter.update_layout(
            margin=dict(l=10, r=30, t=30, b=10),
            yaxis=dict(title="Suma de CVSSF", range=[0, y_lim]),
            xaxis=dict(title="Cantidad de vulnerabilidades"),
            legend_title_text="Nivel de Exposición",
            shapes=[], annotations=[]
        )

        cA, cB = st.columns(2)
        with cA: st.plotly_chart(fig_barras, use_container_width=True)
        with cB: st.plotly_chart(fig_donut, use_container_width=True)
        st.plotly_chart(fig_scatter, use_container_width=True)

        # =========================
        #  COMPARACIÓN: CVSS vs MURC
        # =========================
        with st.expander("📊 Comparación CVSS vs MURC (priorización)", expanded=True):
            df_comp = df_filt.copy()

            df_comp["MURC_0a10"] = (df_comp["riesgo"] * 10).round(2)

            bins_cvss = [-0.01, 2.5, 5.0, 7.5, float("inf")]
            labels_nivel = ["BAJO", "MEDIO", "ALTO", "CRÍTICO"]
            df_comp["Nivel_CVSS"] = pd.cut(
                (df_comp["CVSS"]).fillna(-0.01),
                bins=bins_cvss, labels=labels_nivel
            ).astype("string").fillna("SIN DATO")

            df_comp["Delta(MURC-CVSS)"] = (df_comp["MURC_0a10"] - df_comp["CVSS"]).round(2)

            orden = {"BAJO":1, "MEDIO":2, "ALTO":3, "CRÍTICO":4, "SIN DATO":0}
            df_comp["_ord_murc"] = df_comp["Nivel de Exposición"].map(orden).fillna(0)
            df_comp["_ord_cvss"] = df_comp["Nivel_CVSS"].map(orden).fillna(0)
            diff_nivel = (df_comp["_ord_murc"] - df_comp["_ord_cvss"]).astype(int)

            def etiqueta_cambio(n):
                if n > 0:  return "⬆️ Sube prioridad (MURC > CVSS)"
                if n < 0:  return "⬇️ Baja prioridad (MURC < CVSS)"
                return "➡️ Mantiene prioridad"

            df_comp["Cambio_prioridad"] = diff_nivel.map(etiqueta_cambio)

            total_cmp = len(df_comp)
            suben = int((diff_nivel > 0).sum())
            bajan = int((diff_nivel < 0).sum())
            igual = int((diff_nivel == 0).sum())

            c1c, c2c, c3c, c4c = st.columns(4)
            c1c.metric("Registros comparados", f"{total_cmp:,}".replace(",", "."))
            c2c.metric("Suben prioridad", suben)
            c3c.metric("Bajan prioridad", bajan)
            c4c.metric("Sin cambio", igual)

            st.write("---")

            cols_tabla = ["Activo","Identificador","CVSS","MURC_0a10","Delta(MURC-CVSS)","Nivel_CVSS","Nivel de Exposición","Criticidad"]
            st.subheader("Tabla comparativa (Top 50 por diferencia absoluta)")
            df_top = df_comp.assign(_abs= df_comp["Delta(MURC-CVSS)"].abs()) \
                            .sort_values("_abs", ascending=False)[cols_tabla].head(50)
            st.dataframe(df_top, use_container_width=True, height=380)

            st.write("---")

            st.subheader("Dispersión: CVSS (x) vs MURC en escala 0–10 (y)")
            fig_cmp = px.scatter(
                df_comp,
                x="CVSS", y="MURC_0a10",
                color="Cambio_prioridad",
                hover_data={
                    "Activo": True,
                    "Identificador": True,
                    "CVSS": ":.2f",
                    "MURC_0a10": ":.2f",
                    "Nivel_CVSS": True,
                    "Nivel de Exposición": True,
                    "Criticidad": True,
                    "Delta(MURC-CVSS)": ":.2f",
                },
                labels={"MURC_0a10":"MURC (0–10)"},
                height=460
            )
            max_axis = max(
                (df_comp["CVSS"].max() if pd.notna(df_comp["CVSS"].max()) else 10),
                (df_comp["MURC_0a10"].max() if pd.notna(df_comp["MURC_0a10"].max()) else 10)
            )
            fig_cmp.add_shape(type="line", x0=0, y0=0, x1=max_axis, y1=max_axis,
                              line=dict(dash="dash"))
            fig_cmp.update_layout(margin=dict(l=10,r=30,t=30,b=10), legend_title_text="Cambio de prioridad")
            st.plotly_chart(fig_cmp, use_container_width=True)

            st.subheader("Distribución de cambios de prioridad")
            dist_cambio = df_comp.groupby("Cambio_prioridad").size().reset_index(name="Cantidad")
            fig_bar_cmp = px.bar(
                dist_cambio.sort_values("Cantidad", ascending=False),
                x="Cambio_prioridad", y="Cantidad",
                text="Cantidad", height=320
            )
            fig_bar_cmp.update_traces(textposition="outside")
            fig_bar_cmp.update_layout(showlegend=False, margin=dict(l=10,r=30,t=30,b=10))
            st.plotly_chart(fig_bar_cmp, use_container_width=True)

        # -------- Descargas --------
        st.subheader("📥 Descargas")
        output_excel = BytesIO(); df_filt.to_excel(output_excel, index=False)
        st.download_button(
            label="Descargar resultado filtrado (Excel)",
            data=output_excel.getvalue(),
            file_name="Resultado_Riesgo_Unificado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        output_csv = df_filt.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="Descargar resultado filtrado (CSV)",
            data=output_csv,
            file_name="Resultado_Riesgo_Unificado.csv",
            mime="text/csv"
        )

        # -------- Pie de página --------
        st.write("---")
        now_txt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        st.caption(f"Generado por MURC • {now_txt}")
        # 👇 aquí también cambié el texto del footer
        st.markdown(
            f"<div id='custom-footer'>MURC · {now_txt} · Versión académica — Prototipo</div>",
            unsafe_allow_html=True
        )

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")

else:
    st.info("Sube un archivo para iniciar el análisis.")
