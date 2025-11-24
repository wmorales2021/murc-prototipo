
# 📘 Documentación del Prototipo MURC  
**Modelo Unificado de Riesgo Cibernético (MURC)**  
Versión académica — Trabajo de grado (2025)  
Autor: **Wilson Rafael Morales Rada**

---

## 🧩 Introducción

El **Modelo Unificado de Riesgo Cibernético (MURC)** es una metodología y herramienta tecnológica diseñada para optimizar la **priorización de vulnerabilidades** en entidades financieras.  
El modelo integra de forma ponderada tres dimensiones fundamentales:

- **CVSS** — Severidad técnica  
- **CVSSF** — Exposición al riesgo
- **Criticidad del activo (BIA)**  

MURC ofrece un índice unificado con valores entre **0 y 1**, permitiendo clasificar  la exposicion al riesgo en :

🔹 **BAJO**  
🔸 **MEDIO**  
🟥 **ALTO**  
🟥 **CRÍTICO**  

Este prototipo fue construido como parte del trabajo de grado de la **Maestría en Informática** de la Escuela Colombiana de Ingeniería Julio Garavito (2025).

---

## 🏗️ Arquitectura del Prototipo

El prototipo implementado en Python + Streamlit opera mediante los siguientes módulos:

### 1️⃣ Carga de datos
Requiere un archivo Excel con tres hojas:

| Hoja                | Campos obligatorios                          | Descripción |
|---------------------|-----------------------------------------------|-------------|
| `Escaneo`           | Identificador, Activo                         | Vulnerabilidades detectadas |
| `CVSSF`             | Identificador, CVSS, CVSSF                    | Severidad técnica y exploitability |
| `Criticidad_Activos`| Activo, Criticidad                            | Clasificación BIA del activo |

---

### 2️⃣ Unificación y normalización

- Se unen los datos por **Identificador** y **Activo**  
- Se normalizan los valores:  
  - `cvss_norm = CVSS / 10`  
  - `cvssf_norm = CVSSF / 4096`  
  - `crit_norm = Criticidad_num / 4`

---

### 3️⃣ Cálculo del índice MURC

<div align="center">

\[
\text{MURC} = 0.5 \cdot \text{CVSS}_{\text{norm}} \;+\; 
0.3 \cdot \text{CVSSF}_{\text{norm}} \;+\; 
0.2 \cdot \text{Criticidad}_{\text{norm}}
\]

</div>


### 4️⃣ Clasificación del nivel de exposición

| Rango MURC | Nivel |
|-----------|--------|
| 0.00 – 0.25 | BAJO |
| 0.26 – 0.50 | MEDIO |
| 0.51 – 0.75 | ALTO |
| > 0.75      | CRÍTICO |

---

## 📊 Funcionalidades principales

- Tabla interactiva filtrable  
- Gráficos con Plotly:
  - Barras por nivel de exposición  
  - Donut por criticidad  
  - Dispersión CVSS vs MURC  
- Comparación de severidad:
  - CVSS (0–10) vs MURC (0–10)
- Descarga de resultados en **Excel y CSV**
- Generación automática de justificación del nivel de exposición
- Autenticación con variables de entorno (`MURC_USER`, `MURC_PASS`)

---

## 🚀 Instalación y ejecución local

### 1️⃣ Clonar el repositorio
git clone https://github.com/wmorales2021/murc-prototipo.git

cd murc-prototipo


### 2️⃣ Crear entorno virtual
python -m venv venv
source venv/Scripts/activate # Windows


### 3️⃣ Instalar dependencias
pip install -r requisitos.txt


### 4️⃣ (Opcional) Configurar credenciales
Crear archivo `.env` basado en `.env.ejemplo`:

MURC_USER=admin
MURC_PASS=admin123



### 5️⃣ Ejecutar la aplicación
streamlit run aplicación.py


---

## 📁 Estructura del repositorio

murc-prototipo/
├── aplicación.py
├── requisitos.txt
├── logo_murc.png
├── .env.ejemplo
├── README.md
├── documentos/
│ └── index.md ← (esta documentación)



---

## 📎 Anexos (Trabajo de Grado)

Este sitio corresponde al **Anexo A: Evidencias del modelo MURC y herramienta tecnológica**.

### 🔹 Anexo B – Código fuente  
Repositorio:  
👉 https://github.com/wmorales2021/murc-prototipo

### 🔹 Anexo C – Concepto de validación técnica  
Documento almacenado en repositorio institucional del FNA (uso interno).

---

## 👨‍💻 Autor  
**Wilson Rafael Morales Rada**  
Maestría en Informática  
Escuela Colombiana de Ingeniería Julio Garavito  
2025

---

## 📝 Licencia y uso  
Este prototipo se publica únicamente para fines **académicos y de investigación**.  
Su uso en producción debe ajustarse a las políticas de cada entidad  y normativas aplicables.

---



