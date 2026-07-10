CREATE TABLE IF NOT EXISTS pollution_measurements (
    id SERIAL PRIMARY KEY,
    measured_at TIMESTAMP NOT NULL,
    pollutant VARCHAR(10) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(20) NOT NULL,
    quality_status VARCHAR(20) NOT NULL,
    station_name VARCHAR(50) NOT NULL DEFAULT 'Santiago'
);

CREATE INDEX IF NOT EXISTS ix_pollution_measured_at ON pollution_measurements (measured_at);
CREATE INDEX IF NOT EXISTS ix_pollution_pollutant_measured ON pollution_measurements (pollutant, measured_at);

CREATE TABLE IF NOT EXISTS weather_measurements (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    temp_max DOUBLE PRECISION,
    temp_min DOUBLE PRECISION,
    rain_sum DOUBLE PRECISION,
    precipitation_sum DOUBLE PRECISION,
    precip_hours DOUBLE PRECISION,
    precip_prob_max DOUBLE PRECISION,
    wind_speed_max DOUBLE PRECISION,
    wind_gusts_max DOUBLE PRECISION,
    weather_code INTEGER
);

CREATE INDEX IF NOT EXISTS ix_weather_date ON weather_measurements (date);

CREATE TABLE IF NOT EXISTS daily_metrics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    pollutant VARCHAR(10) NOT NULL,
    avg_value DOUBLE PRECISION NOT NULL,
    max_value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(20) NOT NULL,
    UNIQUE (date, pollutant)
);

CREATE INDEX IF NOT EXISTS ix_daily_date_pollutant ON daily_metrics (date, pollutant);

CREATE TABLE IF NOT EXISTS monthly_metrics (
    id SERIAL PRIMARY KEY,
    year_month VARCHAR(7) NOT NULL,
    pollutant VARCHAR(10) NOT NULL,
    avg_value DOUBLE PRECISION NOT NULL,
    max_value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(20) NOT NULL,
    UNIQUE (year_month, pollutant)
);

CREATE INDEX IF NOT EXISTS ix_monthly_ym_pollutant ON monthly_metrics (year_month, pollutant);

CREATE TABLE IF NOT EXISTS correlation_matrix (
    id SERIAL PRIMARY KEY,
    var_x VARCHAR(50) NOT NULL,
    var_y VARCHAR(50) NOT NULL,
    correlation DOUBLE PRECISION NOT NULL,
    method VARCHAR(20) NOT NULL DEFAULT 'pearson',
    computed_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS pollution_thresholds (
    id SERIAL PRIMARY KEY,
    pollutant VARCHAR(10) NOT NULL,
    level VARCHAR(30) NOT NULL,
    threshold_value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(20) NOT NULL,
    source VARCHAR(100) NOT NULL,
    UNIQUE (pollutant, level)
);

CREATE INDEX IF NOT EXISTS ix_threshold_pollutant_level ON pollution_thresholds (pollutant, level);

INSERT INTO pollution_thresholds (pollutant, level, threshold_value, unit, source)
VALUES
    ('MP25', 'normal', 25.0, 'ug/m3', 'referencia operacional proyecto'),
    ('MP25', 'moderado', 50.0, 'ug/m3', 'referencia operacional proyecto'),
    ('MP10', 'normal', 50.0, 'ug/m3', 'referencia operacional proyecto'),
    ('MP10', 'moderado', 150.0, 'ug/m3', 'referencia operacional proyecto')
ON CONFLICT (pollutant, level) DO NOTHING;

CREATE TABLE IF NOT EXISTS model_metrics (
    id SERIAL PRIMARY KEY,
    task_type VARCHAR(30) NOT NULL,
    model_name VARCHAR(80) NOT NULL,
    metric_name VARCHAR(50) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    artifact_path TEXT NOT NULL,
    details TEXT,
    trained_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_model_metric_task ON model_metrics (task_type, model_name);

CREATE TABLE IF NOT EXISTS etl_execution_log (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(50) NOT NULL,
    stage VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    records_count INTEGER DEFAULT 0,
    error_message TEXT,
    duration_seconds DOUBLE PRECISION,
    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP
);
