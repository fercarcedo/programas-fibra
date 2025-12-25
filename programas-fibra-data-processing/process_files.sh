#!/bin/bash
ogr2ogr -f GeoJSON -t_srs EPSG:4326 ZonasElegiblesFinales2024.geojson '/home/fer/Ficheros_programas_fibra/UNICO_2024/ZonasElegiblesFinales2024.shp'
uv run main.py unico -e ZonasElegiblesFinales2024.geojson -a '/home/fer/Ficheros_programas_fibra/Relacion_proyectos_aprobados_UNICO_Banda_Ancha_2024_19_12_2025.xlsx' -o unico2024.geojson -p "UNICO 2024"
tippecanoe -z18 --projection=EPSG:4326 -o unico2024.pmtiles -l output unico2024.geojson --force
tile-join -o merged.pmtiles unico2024.pmtiles --force
ogr2ogr -f GeoJSON -t_srs EPSG:4326 ZonasElegibles2023.geojson '/home/fer/Ficheros_programas_fibra/UNICO_2023/ZonasElegibles2023.shp'
uv run main.py unico -e ZonasElegibles2023.geojson -a '/home/fer/Ficheros_programas_fibra/Relacion_proyectos_aprobados_UNICO_Banda_Ancha_2023_19_12_2025.xlsx' -o  unico2023.geojson -p "UNICO 2023"
tippecanoe -z18 --projection=EPSG:4326 -o unico2023.pmtiles -l output unico2023.geojson --force
ogr2ogr -f GeoJSON -t_srs EPSG:4326 ZonasElegibles2022_UNICO_BA.geojson '/home/fer/Ficheros_programas_fibra/UNICO_2022/ZonasElegibles2022_UNICO_BA.shp'
uv run main.py unico -e ZonasElegibles2022_UNICO_BA.geojson -a '/home/fer/Ficheros_programas_fibra/Relacion_proyectos_aprobados_UNICO_Banda_Ancha_2022_19_12_2025.xlsx' -o unico2022.geojson -p "UNICO 2022"
tippecanoe -z18 --projection=EPSG:4326 -o unico2022.pmtiles -l output unico2022.geojson --force
ogr2ogr -f GeoJSON -t_srs EPSG:4326 ZonasBG_Resultado.geojson '/home/fer/Ficheros_programas_fibra/UNICO_2021/ZonasBG_Resultado.shp'
uv run main.py unico -e ZonasBG_Resultado.geojson -a '/home/fer/Ficheros_programas_fibra/Relacion_proyectos_aprobados_UNICO_Banda_Ancha_2021_19-12-2025.xlsx' -o unico2021.geojson -p "UNICO 2021"
tippecanoe -z18 --projection=EPSG:4326 -o unico2021.pmtiles -l output unico2021.geojson --force
ogrmerge.py -single -f GeoJSON -t_srs EPSG:4326 -o Zonas_2020.geojson '/home/fer/Ficheros_programas_fibra/PEBA_2020/_shapefile/*.shp'
# We use unico with PEBA 2020 and 2021 because both have a UNICO-like syntax and an areas file
uv run main.py unico -e Zonas_2020.geojson -a '/home/fer/Ficheros_programas_fibra/Relacion-proyectos-aprobados-2021.xlsx' -o peba2021.geojson -p "PEBA 2021"
uv run main.py unico -e Zonas_2020.geojson -a '/home/fer/Ficheros_programas_fibra/Relacion_proyectos_aprobados_2020.xlsx' -o peba2020.geojson -p "PEBA 2020"
uv run main.py peba -f '/home/fer/Ficheros_programas_fibra/Relacion-proyectos-aprobados-2019.xlsx' -e ENTIDADES.csv -o peba2019.geojson -p "PEBA 2019"
uv run main.py peba -f '/home/fer/Ficheros_programas_fibra/Relacion-proyectos-aprobados-2018.xlsx' -e ENTIDADES.csv -o peba2018.geojson -p "PEBA 2018"
uv run main.py peba -f '/home/fer/Ficheros_programas_fibra/Relacion-proyectos-aprobados-2017.xlsx' -e ENTIDADES.csv -o peba2017.geojson -p "PEBA 2017"
uv run main.py peba -f '/home/fer/Ficheros_programas_fibra/Relacion-proyectos-aprobados-2016_RV-octubre21.xlsx' -e ENTIDADES.csv -o peba2016.geojson -p "PEBA 2016"
uv run main.py peba -f '/home/fer/Ficheros_programas_fibra/Relacion-proyectos-aprobados-2015.xlsx' -e ENTIDADES.csv -o peba2015.geojson -p "PEBA 2015"
uv run main.py peba -f '/home/fer/Ficheros_programas_fibra/Relacion-proyectos-aprobados-2014.xlsx' -e ENTIDADES.csv -o peba2014.geojson -p "PEBA 2014"
uv run main.py peba -f '/home/fer/Ficheros_programas_fibra/Relacion-proyectos-aprobados-2013.xlsx' -e ENTIDADES.csv -o peba2013.geojson -p "PEBA 2013"
