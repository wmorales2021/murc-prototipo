1. Descripción general

El Modelo Unificado de Riesgo Cibernético (MURC) es una metodología y herramienta tecnológica desarrollada para optimizar la priorización de vulnerabilidades en entidades financieras 

El modelo integra tres dimensiones clave:

CVSS (severidad técnica),

CVSSF (Exposicion al riesgo)

Criticidad del activo (según clasificación BIA).

Este repositorio, contiene el prototipo funcional implementado en Python + Streamlit, desarrollado como parte del trabajo de grado denominado:

“Desarrollo de una metodología y herramienta para optimizar la gestión de vulnerabilidades y mitigar el riesgo de ciberseguridad en entidades financieras"

2. Contexto académico e institucional

   Este repositorio corresponde al Anexo B. Código Fuente del trabajo de grado.

   El modelo y la herramienta se alinean con:

Superintendencia Financiera de Colombia (Circular 007 de 2018)

ISO/IEC 27005:2018

NIST SP 800-30:2022

3. Arquitectura del prototipo

   El prototipo MURC opera mediante los siguientes módulos:

Carga del archivo Excel con las hojas:
Escaneo, CVSSF y Criticidad_Activos.

Normalización y unión automática de columnas por identificador y activo.

Cálculo del riesgo unificado usando la fórmula:
0.5 * CVSS + 0.3 * CVSSF + 0.2 * Criticidad

Clasificación por nivel de exposición: BAJO, MEDIO, ALTO, CRÍTICO.

Visualización interactiva (Plotly): barras, donut, dispersión CVSS vs MURC.

Exportación de resultados a Excel y CSV.

Autenticación por variables de entorno (MURC_USER / MURC_PASS).

4. Estructura del repositorio

   prototipo-murc/
│
├── aplicación.py        # Aplicación principal Streamlit (versión académica)
├── requisitos.txt       # Dependencias del proyecto
├── logo_murc.png        # Logotipo del prototipo
├── .env.ejemplo         # Ejemplo de variables de entorno
├── docs/                # (Opcional) documentación técnica, evidencias y anexos
└── README.md            # Este archivo

5. Instalación y ejecución

   1. Clonar el repositorio
      
  git clone https://github.com/wilsonmoralesrada/prototipo-murc.git
cd prototipo-murc

2. Crear entorno virtual
 Ejecutar en consola  python -m venv venv
source venv/Scripts/activate   # Windows

3. Instalar dependencias

   pip install -r requisitos.txt

   4. Definir las credenciales (opcional)

se debe Crear un archivo .env basado en .env.ejemplo:

ejemplo 

MURC_USER=admin
MURC_PASS=admin123

5. Ejecutar la aplicación

streamlit run aplicación.py

6. Formato del archivo de entrada

   | Hoja                   | Campos obligatorios        | Descripción                         |
| ---------------------- | -------------------------- | ----------------------------------- |
| **Escaneo**            | Identificador, Activo      | Vulnerabilidades detectadas         |
| **CVSSF**              | Identificador, CVSS, CVSSF | Severidad técnica y explotabilidad |
| **Criticidad_Activos** | Activo, Criticidad         | Clasificación BIA del activo        |


7. Funcionalidades del prototipo

Clasificación y priorización unificada de vulnerabilidades.

Vista de tabla filtrable.

Gráficos:

Conteo por nivel de exposición

Distribución por criticidad

Dispersión CVSS vs MURC

Cambios de prioridad

Descarga de resultados.

Justificación automática del nivel de exposición

8. Documentación y anexos

Este repositorio corresponde al literal B. Código fuente del trabajo de grado.

A. Evidencias modelo unificado de riesgo cibernético y herramienta tecnológica
(pendiente enlazar GitHub Pages o PDF, ejemplo:)
👉 https://wilsonmoralesrada.github.io/MURC/

B. Código fuente
Este repositorio.

C. Concepto de validación técnica de entidad financiera
Documento almacenado en repositorio institucional de la entidad financiera (uso interno).

9. Autoría

Wilson Rafael Morales Rada
Trabajo de grado — Maestría en Informática
Escuela Colombiana de Ingeniería Julio Garavito
2025

10. Licencia y uso

Este prototipo se publica únicamente con fines académicos y de investigación.
La utilización en entornos productivos debe ajustarse a las políticas internas de la entidad financiera correspondiente.

   






      
  
      




   

