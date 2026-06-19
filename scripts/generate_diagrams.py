#!/usr/bin/env python3
"""genera diagramas png para entregables (fallback sin mermaid-cli)."""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "capturas"
OUT.mkdir(parents=True, exist_ok=True)


def _box(ax, x, y, w, h, text, color="#4a90d9"):
    rect = FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.02",
        facecolor=color, edgecolor="#333", linewidth=1.2,
    )
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=9, color="white", weight="bold", wrap=True)


def _arrow(ax, x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle="->", mutation_scale=12,
        color="#555", linewidth=1.5,
    ))


def arquitectura():
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5)
    ax.axis("off")
    ax.set_title("Arquitectura del sistema", fontsize=14, weight="bold", pad=12)

    sources = ["CSV CO", "CSV MP10", "CSV MP2.5", "CSV NO2", "CSV O3", "Open-Meteo"]
    for i, s in enumerate(sources):
        _box(ax, 0.2, 4.2 - i * 0.55, 1.8, 0.45, s, "#6c757d")

    _box(ax, 2.5, 2.5, 1.5, 1.2, "ETL\nExtract\nTransform\nValidate\nLoad", "#28a745")
    _box(ax, 4.5, 2.8, 1.3, 0.7, "PostgreSQL", "#ffc107")
    _box(ax, 6.2, 3.0, 1.2, 0.5, "FastAPI", "#17a2b8")
    _box(ax, 7.8, 2.5, 1.5, 1.2, "Dash\nDashboard", "#6610f2")

    _arrow(ax, 2.0, 2.8, 2.5, 3.1)
    _arrow(ax, 4.0, 3.1, 4.5, 3.15)
    _arrow(ax, 5.8, 3.15, 6.2, 3.25)
    _arrow(ax, 7.4, 3.25, 7.8, 3.1)

    fig.tight_layout()
    fig.savefig(OUT / "arquitectura.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def pipeline_etl():
    fig, ax = plt.subplots(figsize=(11, 3))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 3)
    ax.axis("off")
    ax.set_title("Pipeline ETL", fontsize=14, weight="bold", pad=12)

    steps = [
        ("Extract\n6 fuentes", "#6c757d"),
        ("Transform\nAgregados", "#28a745"),
        ("Validate\nPydantic+GE", "#fd7e14"),
        ("Load\nPostgreSQL", "#17a2b8"),
    ]
    for i, (label, color) in enumerate(steps):
        x = 0.5 + i * 2.7
        _box(ax, x, 1.0, 2.2, 1.0, label, color)
        if i < len(steps) - 1:
            _arrow(ax, x + 2.2, 1.5, x + 2.7, 1.5)

    fig.tight_layout()
    fig.savefig(OUT / "pipeline_etl.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def docker_services():
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")
    ax.set_title("Orquestación Docker Compose", fontsize=14, weight="bold", pad=12)

    services = [
        (1, 2.5, "postgres\n:5432", "#336791"),
        (3.5, 2.5, "etl\none-shot", "#28a745"),
        (6, 2.5, "api\n:8000", "#17a2b8"),
        (8.5, 2.5, "dashboard\n:8050", "#6610f2"),
    ]
    for x, y, label, color in services:
        _box(ax, x, y, 1.8, 1.0, label, color)

    for i in range(len(services) - 1):
        x1 = services[i][0] + 1.8
        x2 = services[i + 1][0]
        _arrow(ax, x1, 3.0, x2, 3.0)

    ax.text(5, 0.8, "postgres healthy → etl success → api healthy → dashboard",
            ha="center", fontsize=9, style="italic")

    fig.tight_layout()
    fig.savefig(OUT / "docker_compose.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def dashboard_mockups():
    """mockups simplificados por vista de dashboard."""
    views = [
        ("dashboard_ejecutivo.png", "Vista Ejecutiva", ["KPI CO", "KPI MP2.5", "KPI O3"], "#6610f2"),
        ("dashboard_analitico.png", "Vista Analítica", ["Correlación", "Scatter", "Boxplot"], "#17a2b8"),
        ("dashboard_operacional.png", "Vista Operacional", ["API: OK", "ETL: success", "Calidad: 95%"], "#28a745"),
        ("dashboard_presentacion.png", "Vista Autoridad", ["Hipótesis O3", "Hipótesis MP", "Hallazgos"], "#fd7e14"),
    ]
    for fname, title, items, color in views:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6)
        ax.axis("off")
        ax.set_title(title, fontsize=14, weight="bold", pad=10)
        _box(ax, 0.5, 5.0, 9, 0.6, title, color)
        for i, item in enumerate(items):
            _box(ax, 0.5 + (i % 3) * 3.1, 3.5 - (i // 3) * 1.5, 2.8, 1.0, item, "#e9ecef")
            ax.texts[-1].set_color("#333")
        fig.tight_layout()
        fig.savefig(OUT / fname, dpi=150, bbox_inches="tight")
        plt.close(fig)


if __name__ == "__main__":
    arquitectura()
    pipeline_etl()
    docker_services()
    dashboard_mockups()
    print(f"Diagramas generados en {OUT}")
