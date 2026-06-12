#!/bin/bash
#genera diagramas png desde archivos mermaid en docs/
#requiere: npm install -g @mermaid-js/mermaid-cli

DOCS_DIR="$(dirname "$0")/../docs"
OUT_DIR="$DOCS_DIR/diagramas"

mkdir -p "$OUT_DIR"

for md in "$DOCS_DIR"/arquitectura.md "$DOCS_DIR"/diagrama_etl.md "$DOCS_DIR"/diagrama_docker.md "$DOCS_DIR"/modelo_er.md; do
    name=$(basename "$md" .md)
    #extrae bloque mermaid y genera png
    sed -n '/```mermaid/,/```/p' "$md" | sed '1d;$d' > "/tmp/${name}.mmd"
    if command -v mmdc &> /dev/null; then
        mmdc -i "/tmp/${name}.mmd" -o "$OUT_DIR/${name}.png" -b transparent
        echo "generado: $OUT_DIR/${name}.png"
    else
        echo "mmdc no instalado - instalar con: npm install -g @mermaid-js/mermaid-cli"
        exit 1
    fi
done
