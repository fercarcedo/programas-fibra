import pandas as pd
import numpy as np

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