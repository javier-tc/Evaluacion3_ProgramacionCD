# Manual de Usuario

## Acceso al sistema

1. Ejecutar `docker compose up --build`
2. Abrir http://localhost:8050 en el navegador

## Orden sugerido para presentación

1. **Presentación** — pregunta de investigación, hipótesis y hallazgos
2. **Ejecutivo** — KPIs y tendencias
3. **Analítico** — evidencia estadística
4. **Operacional** — calidad del pipeline

## Vista Presentación

Orientada a autoridad ambiental o municipalidad:

- Pregunta de investigación sobre clima y calidad del aire
- Cuatro hipótesis de trabajo
- Resumen por contaminante (CO, MP2.5, MP10, NO2, O3)
- Hallazgos dinámicos según correlaciones observadas
- Enlaces a las demás vistas

## Dashboard Ejecutivo

- **5 KPI cards** con promedios anuales en unidades reales:
  - CO (ppm), MP2.5 (μg/m³), MP10 (μg/m³), NO2 (ppb), O3 (ppb)
- **Ranking de contaminantes** en barras con valores reales (cada uno en su unidad)
- **Evolución mensual normalizada** (min-max) para comparar tendencias entre contaminantes sin mezclar unidades

### Filtros

- Rango de fechas para la serie mensual normalizada

## Dashboard Analítico

- Matriz de correlación (contaminantes + temperatura, lluvia, viento)
- Scatter plots: Temperatura vs O3, Viento vs MP2.5, Lluvia vs MP10
- Promedio por estación del año (Verano, Otoño, Invierno, Primavera)
- Boxplot por contaminante seleccionado (valores reales)
- Análisis horario de CO y NO2

### Limitación de datos horarios

Los datos fuente son **agregaciones diarias** (hora 00:00). El gráfico horario muestra la resolución disponible; la hipótesis de patrones de tráfico debe interpretarse con esta restricción.

## Dashboard Operacional

- Estado de API, PostgreSQL y último ETL
- Registros procesados, duplicados eliminados, errores y duración
- Calidad de datos: validados, preliminares, no validados, faltantes estimados

Se actualiza cada 30 segundos.

## Exportar gráficos

Cada gráfico incluye la barra de herramientas Plotly. Usar el icono de cámara para exportar PNG.

## Preguntas que responde el sistema

- ¿Cómo afectan las condiciones meteorológicas a la calidad del aire?
- ¿Mayor temperatura se asocia con mayor ozono?
- ¿La lluvia reduce material particulado?
- ¿El viento dispersa CO y NO2?
- ¿Existen patrones estacionales?
- ¿Qué contaminantes correlacionan entre sí y con el clima?
