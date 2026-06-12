# Manual de Usuario

## Acceso al sistema

1. Ejecutar `docker compose up --build`
2. Abrir http://localhost:8050 en el navegador

## Dashboard Ejecutivo

Orientado a toma de decisiones. Incluye:

- **KPI Cards**: promedios anuales por contaminante y contaminante predominante
- **Evolución temporal**: series de línea con zoom y tooltips
- **Comparación**: gráficos de barras entre contaminantes
- **Evolución mensual**: tendencias por mes
- **Días críticos**: ranking de días con mayor contaminación

### Filtros

- **Rango de fechas**: selector en la parte superior
- **Contaminante**: dropdown para filtrar o ver todos

## Dashboard Analítico

Orientado a analistas de datos:

- Matriz de correlación entre contaminantes y variables meteorológicas
- Heatmap temporal (mes × contaminante)
- Boxplots de distribución
- Histogramas de concentración
- Análisis semanal y horario

## Dashboard Operacional

Monitoreo del sistema:

- Estado de la API y PostgreSQL
- Última ejecución del ETL
- Registros procesados y errores
- Alertas automáticas

Se actualiza cada 30 segundos.

## Exportar gráficos

Cada gráfico incluye la barra de herramientas Plotly. Usar el icono de cámara para exportar PNG.

## Preguntas que responde el sistema

- ¿Cuál fue el contaminante predominante?
- ¿Existe relación entre temperatura y ozono?
- ¿Cómo afecta la lluvia al material particulado?
- ¿Qué días tuvieron mayor contaminación?
- ¿Existen patrones semanales?
- ¿Qué contaminantes correlacionan entre sí?
