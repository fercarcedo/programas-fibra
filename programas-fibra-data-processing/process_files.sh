#!/bin/bash
#ogr2ogr -f GeoJSON -t_srs EPSG:4326 ZonasElegiblesFinales2024.geojson '/home/fer/Ficheros_programas_fibra/UNICO_2024/ZonasElegiblesFinales2024.shp'
#uv run main.py unico -e ZonasElegiblesFinales2024.geojson -a '/home/fer/Ficheros_programas_fibra/Relacion_proyectos_aprobados_UNICO_Banda_Ancha_2024_19_12_2025.xlsx' -p "UNICO 2024"
#tippecanoe -z18 --projection=EPSG:4326 -o unico2024.pmtiles -l output out.geojson --force
#tile-join -o merged.pmtiles unico2024.pmtiles --force
#ogr2ogr -f GeoJSON -t_srs EPSG:4326 ZonasElegibles2023.geojson '/home/fer/Ficheros_programas_fibra/UNICO_2023/ZonasElegibles2023.shp'
#uv run main.py unico -e ZonasElegibles2023.geojson -a '/home/fer/Ficheros_programas_fibra/Relacion_proyectos_aprobados_UNICO_Banda_Ancha_2023_19_12_2025.xlsx' -p "UNICO 2023"
#tippecanoe -z18 --projection=EPSG:4326 -o unico2023.pmtiles -l output out.geojson --force
#ogr2ogr -f GeoJSON -t_srs EPSG:4326 ZonasElegibles2022_UNICO_BA.geojson '/home/fer/Ficheros_programas_fibra/UNICO_2022/ZonasElegibles2022_UNICO_BA.shp'
#uv run main.py unico -e ZonasElegibles2022_UNICO_BA.geojson -a '/home/fer/Ficheros_programas_fibra/Relacion_proyectos_aprobados_UNICO_Banda_Ancha_2022_19_12_2025.xlsx' -p "UNICO 2022"
#tippecanoe -z18 --projection=EPSG:4326 -o unico2022.pmtiles -l output out.geojson --force
ogr2ogr -f GeoJSON -t_srs EPSG:4326 ZonasBG_Resultado.geojson '/home/fer/Ficheros_programas_fibra/UNICO_2021/ZonasBG_Resultado.shp'
uv run main.py unico -e ZonasBG_Resultado.geojson -a '/home/fer/Ficheros_programas_fibra/Relacion_proyectos_aprobados_UNICO_Banda_Ancha_2021_19-12-2025.xlsx' -p "UNICO 2021"
tippecanoe -z18 --projection=EPSG:4326 -o unico2021.pmtiles -l output out.geojson --force