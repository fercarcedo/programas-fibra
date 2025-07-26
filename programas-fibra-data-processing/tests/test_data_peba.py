import pandas as pd
import numpy as np

PROJECTS_DF = pd.DataFrame({
    0: [*([np.nan] * 6),],
    1: [np.nan, np.nan, "LINEA", "A", "A", "A"],
    2: [np.nan, np.nan, "EXPEDIENTE", "TSI-061000-2018-0001", "TSI-061000-2018-0002", "TSI-061000-2018-0003"],
    3: [np.nan, np.nan, "SITUACIÓN", "FINALIZADO", "FINALIZADO", "FINALIZADO"],
    4: [np.nan, np.nan, "RAZON SOCIAL", "INFORMATICA FUENTEALBILLA S.L.", "INFORMATICA FUENTEALBILLA S.L.", "INFORMATICA FUENTEALBILLA S.L."],
    5: [np.nan, np.nan, "COMUNIDAD AUTÓNOMA", "CASTILLA LA MANCHA", "CASTILLA LA MANCHA", "C.VALENCIANA"],
    6: [np.nan, np.nan, "PRESUPUESTO_FINANCIABLE (€)", "49622", "44402", "61946.6"],
    7: [np.nan, np.nan, "AYUDA  (€)", "29773", "26641", "34070.63"],
    8: [np.nan, np.nan, "SUBVENCION (€)", "3771.07", "3374.43", "4317.68"],
    9: [np.nan, np.nan, "ANTICIPO_FEDER (€)", "26001.93", "23266.57", "29752.95"],
    10: [np.nan, np.nan, "% AYUDA", "59.999597", "59.99955", "55.0"],
    11: [np.nan, np.nan, "Tecnología", "FTTH", "FTTH", "FTTH"],
})

PROJECTS_OLD_PEBA_DF = pd.DataFrame({
    0: [*([np.nan] * 6),],
    1: [np.nan, "Linea de ayudas", "A", "A", "A", "A"],
    2: [np.nan, "Operador de Telecomunicaciones", "MAGTEL COMUNICACIONES AVANZADAS S.L.", np.nan, np.nan, np.nan],
    3: [np.nan, "Proyecto", "TSI-061000-2013-001", "TSI-061000-2013-002", "TSI-061000-2013-003", "TSI-061000-2013-004"],
    4: [np.nan, "Situación", "Cancelado", "Cancelado", "Cancelado", "Finalizado"],
    5: [np.nan, "Comunidad Autónoma", "Andalucía", "Andalucía", "Andalucía", "Andalucía"],
    6: [np.nan, "Provincias", "Cádiz", "Cádiz", "Cádiz", "Sevilla"],
    7: [np.nan, "Municipios *", "Alcala de los Gazules", "Algodonales", "Benalup", "Aznalcollar y Gerena"],
    8: [np.nan, "Inversión prevista (€)", "1419829", "1345815", "1734742", "3999766"],
    9: [np.nan, "Subvención concedida (€)", "185193", "175536", "226269", "521707"],
    10: [np.nan, "Préstamo concedido (€)", "1234636", "1170275", "1508473", "3478059"],
    11: [np.nan, "Intensidad de la ayuda", "30.57", "30.57", "30.57", "30.57"],
    12: [np.nan, "Tecnología", "FTTH", "FTTH", "FTTH", "FTTH"],
})

PROJECTS_FFILL_DF = pd.DataFrame({
    0: [*([np.nan] * 4),],
    1: [np.nan, np.nan, "LINEA", "A",],
    2: [np.nan, np.nan, "EXPEDIENTE", "TSI-061000-2016-084",],
    3: [np.nan, np.nan, "SITUACIÓN", "FINALIZADO",],
    4: [np.nan, np.nan, "RAZON SOCIAL", "EUSKALTEL",],
    5: [np.nan, np.nan, "COMUNIDAD AUTÓNOMA", "PAÍS VASCO",],
    6: [np.nan, np.nan, "PRESUPUESTO FINANCIABLE (€)", "1199597",],
    7: [np.nan, np.nan, "AYUDA (€)", "479837.99",],
    8: [np.nan, np.nan, "SUBVENCIÓN (€)", "0",],
    9: [np.nan, np.nan, "ANTICIPO FEDER (€)", "479837.99",],
    10: [np.nan, np.nan, "% AYUDA", "39.999932",],
    11: [np.nan, np.nan, "Tecnología", "FTTH",],
    12: [np.nan, np.nan, "Enlace a oferta mayorista", "https://www.euskaltel.com/empresas/soy-cliente/tengo-dudas-sobre/descargas/tarifas/condiciones-generales-de-contratacion",],
})

AREAS_DF = pd.DataFrame({
    0: [*([np.nan] * 5),],
    1: [
        np.nan,
        "Expediente",
        "TSI-061000-2018-0001",
        "TSI-061000-2018-0002",
        "TSI-061000-2018-0003",
    ],
    2: [
        np.nan,
        "Comunidad Autónoma",
        "CASTILLA LA MANCHA",
        "CASTILLA LA MANCHA",
        "C.VALENCIANA",
    ],
    3: [
        np.nan,
        "Provincia",
        "ALBACETE",
        "ALBACETE",
        "VALENCIA / VALÈNCIA",
    ],
    4: [
        np.nan,
        "Municipio",
        "Casas de Juan Núñez",
        "Albacete",
        "Real",
    ],
    5: [
        np.nan,
        "Población",
        "CASAS DE JUAN NÚÑEZ",
        "AGUAS NUEVAS",
        "REAL",
    ],
    6: [
        np.nan,
        "Código INE",
        "02021000100",
        "02003000100",
        "46212000100",
    ],
    7: [
        np.nan,
        "Código zona de excepción",
        np.nan,
        np.nan,
        np.nan,
    ],
    8: [
        np.nan,
        "Nombre zona de excepción",
        np.nan,
        np.nan,
        np.nan,
    ]
})

AREAS_OLD_PEBA_DF = pd.DataFrame({
    0: ['LINEA', 'A', 'A', 'A', 'A', 'A'],
    1: ['REF.PROYECTO', 'TSI-061000-2013-004', 'TSI-061000-2013-009', 'TSI-061000-2013-009', 'TSI-061000-2013-012', 'TSI-061000-2013-013'],
    2: ['BENEFICIARIO', 'MAGTEL COMUNICACIONES AVANZADAS, S.L.', 'MAGTEL COMUNICACIONES AVANZADAS, S.L.', 'MAGTEL COMUNICACIONES AVANZADAS, S.L.', 'MAGTEL COMUNICACIONES AVANZADAS, S.L.', 'MAGTEL COMUNICACIONES AVANZADAS, S.L.'],
    3: ['CCAA', 'Comunidad Autónoma de Andalucía', 'Comunidad Autónoma de Andalucía', 'Comunidad Autónoma de Andalucía', 'Comunidad Autónoma de Andalucía', 'Comunidad Autónoma de Andalucía'],
    4: ['PROVINCIA', 'SEVILLA', 'MÁLAGA', 'MÁLAGA', 'SEVILLA', 'MÁLAGA'],
    5: ['COD. INE MUN', '41045', '29070', '29070', '41004', '29067'],
    6: ['MUNICIPIO', 'GERENA', 'MIJAS', 'MIJAS', 'ALCALA DE GUADAIRA', 'MALAGA'],
    7: ['COD.INE NUC', '41045000101', '29070000703', '29070000799', '41004000499', '29067000199'],
    8: ['NUCLEO', 'GERENA', 'LAGUNAS (LAS)', '*DISEMINADO*', '*DISEMINADO*', '*DISEMINADO*'],
})

AREAS_DF_WITHOUT_EXCEPTION_ZONE = pd.DataFrame({
    0: [*([np.nan] * 5),],
    1: [
        np.nan,
        "Expediente",
        "TSI-061000-2018-0001",
        "TSI-061000-2018-0002",
        "TSI-061000-2018-0003",
    ],
    2: [
        np.nan,
        "Comunidad Autónoma",
        "CASTILLA LA MANCHA",
        "CASTILLA LA MANCHA",
        "C.VALENCIANA",
    ],
    3: [
        np.nan,
        "Provincia",
        "ALBACETE",
        "ALBACETE",
        "VALENCIA / VALÈNCIA",
    ],
    4: [
        np.nan,
        "Municipio",
        "Casas de Juan Núñez",
        "Albacete",
        "Real",
    ],
    5: [
        np.nan,
        "Población",
        "CASAS DE JUAN NÚÑEZ",
        "AGUAS NUEVAS",
        "REAL",
    ],
    6: [
        np.nan,
        "Código INE",
        "02021000100",
        "02003000100",
        "46212000100",
    ]
})

AREAS_FFILL_DF = pd.DataFrame({
    0: [*([np.nan] * 15),],
    1: [np.nan, "Expediente", "TSI-061000-2016-084", *([np.nan] * 12),],
    2: [np.nan, "Comunidad Autónoma", "PAIS VASCO", *([np.nan] * 12),],
    3: [np.nan, "Provincia", "ARABA/ÁLAVA", "GIPUZKOA", *([np.nan] * 5), "BIZKAIA", *([np.nan] * 5),],
    4: [np.nan, "Municipio", "ZUIA", "ADUNA", "ASTEASU", np.nan, "ATAUN", "ITSASONDO", "LARRAUL", "BAKIO", "BERRIATUA", "GATIKA", "GORDEXOLA", "URDUÑA/ORDUÑA", "ZARATAMO",],
    5: [np.nan, "Población", "MURGIA", "ADUNA", "ASTEASU", "ELIZMENDI", "SAN MARTIN", "ITSASONDO", "LARRAUL", "GIBELORRATZAGAKO SAN PELAIO", "ERRIBERA", "SERTUTXA", "SANDAMENDI", "ORDUÑA", "ZARATAMO",],
    6: [np.nan, "Código INE", "01063001100", "20002000100", "20014000100", "20014000300", "20015000300", "20047000200", "20048000100", "48012000500", "48018000400", "48040001000", "48042000600", "48074000500", "48097000500",],
    7: [np.nan, "Código zona de excepción", *([np.nan] * 7), "48012000500-zona01", *([np.nan] * 3), "48074000500-zona03", np.nan],
})

AREAS_FFILLED_DF = pd.DataFrame({
    0: [*([np.nan] * 15),],
    1: [np.nan, "Expediente", *(["TSI-061000-2016-084"] * 13),],
    2: [np.nan, "Comunidad Autónoma", *(["PAIS VASCO"] * 13),],
    3: [np.nan, "Provincia", "ARABA/ÁLAVA", *(["GIPUZKOA"] * 6), *(["BIZKAIA"] * 6),],
    4: [np.nan, "Municipio", "ZUIA", "ADUNA", "ASTEASU", "ASTEASU", "ATAUN", "ITSASONDO", "LARRAUL", "BAKIO", "BERRIATUA", "GATIKA", "GORDEXOLA", "URDUÑA/ORDUÑA", "ZARATAMO",],
    5: [np.nan, "Población", "MURGIA", "ADUNA", "ASTEASU", "ELIZMENDI", "SAN MARTIN", "ITSASONDO", "LARRAUL", "GIBELORRATZAGAKO SAN PELAIO", "ERRIBERA", "SERTUTXA", "SANDAMENDI", "ORDUÑA", "ZARATAMO",],
    6: [np.nan, "Código INE", "01063001100", "20002000100", "20014000100", "20014000300", "20015000300", "20047000200", "20048000100", "48012000500", "48018000400", "48040001000", "48042000600", "48074000500", "48097000500",],
    7: [np.nan, "Código zona de excepción", *([np.nan] * 7), "48012000500-zona01", *([np.nan] * 3), "48074000500-zona03", np.nan],
})

ENTITIES_DF = pd.DataFrame(
    {
        'CODIGOINE': [
            "1001000000",
            "1001000100",
            "1001000101",
            "1001000199",
            "1001000200",
        ],
        "NOMBRE": [
            "Alegría-Dulantzi",
            "Alegría-Dulantzi",
            "Alegría-Dulantzi",
            "Alegría-Dulantzi",
            "Egileta",
        ],
        "COD_PROV": [
            "1",
            "1",
            "1",
            "1",
            "1",
        ],
        "PROVINCIA": [
            "Araba/Álava",
            "Araba/Álava",
            "Araba/Álava",
            "Araba/Álava",
            "Araba/Álava",
        ],
        "LONGITUD_ETRS89": [
            "-2,51243731",
            "-2,51243731",
            "-2,51243731",
            "-2,51243731",
            "-2,53530168",
        ],
        "LATITUD_ETRS89": [
            "42,83981158",
            "42,83981158",
            "42,83981158",
            "42,83981158",
            "42,80973927",
        ]
    }
)