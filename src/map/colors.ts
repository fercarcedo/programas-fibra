type RGBA = [number, number, number, number];

const OPERATOR_COLORS: Record<string, [number, number, number]> = {
  TELEFONICA: [1, 157, 244],
  ORANGE:     [255, 94, 14],
  AVATEL:     [160, 94, 181], // Incluye todas sus filiales
  ADAMO:      [43, 195, 110],
  ASTEO:      [36, 114, 183],
  VENTO:      [59, 156, 63],
  MASMOVIL:   [255, 222, 33],
  EUSKALTEL:  [0, 85, 120],  // Grupo Euskaltel/R/Telecable
  VODAFONE:   [230, 0, 0],
  LYNTIA:     [230, 0, 126],
  OTHER:    [112, 128, 144]
};

const PROGRAM_COLORS: Record<string, [number, number, number]> = {
  PEBA_2013: [255, 255, 255],
  PEBA_2014: [60, 60, 60],
  PEBA_2015: [255, 235, 0],
  PEBA_2016: [180, 255, 0],
  PEBA_2017: [255, 100, 200],
  PEBA_2018: [0, 255, 255],
  PEBA_2019: [180, 0, 0],
  PEBA_2020: [140, 0, 255],
  PEBA_2021: [150, 75, 0],
  UNICO_2021: [0, 150, 80],
  UNICO_2022: [255, 180, 0],
  UNICO_2023: [0, 50, 200],
  UNICO_2024: [255, 0, 255]
};

const NAME_TO_OPERATOR: Record<string, string> = {
  'TELEFONICA DE ESPAÑA, S.A.': 'TELEFONICA',
  'TELEFÓNICA DE ESPAÑA S.A.': 'TELEFONICA',
  'ORANGE ESPAÑA COMUNICACIONES FIJAS S.L.U.': 'ORANGE',
  'ORANGE ESPAGNE S.A.': 'ORANGE',
  'ADAMO TELECOM IBERIA SA': 'ADAMO',
  'ASTEO RED NEUTRA SL': 'ASTEO',
  'VENTO REDE, S.L.': 'VENTO',
  'VODAFONE ESPAÑA S.A.': 'VODAFONE',
  'LYNTIA NETWORKS, S.A.': 'LYNTIA',
  'MASMOVIL BROADBAND S.A.UNIPERSONAL': 'MASMOVIL',
  'MASMOVIL BROADBAND SA': 'MASMOVIL',
  'MAS MOVIL TELECOM 3.0 S.A.': 'MASMOVIL',
  'EMBOU NUEVAS TECNOLOGIAS SL.': 'MASMOVIL',
  'XTRA TELECOM, S.A.U': 'MASMOVIL',
  'MASMOVIL IBERCOM SA': 'MASMOVIL',
  'EUSKALTEL': 'EUSKALTEL',
  'EUSKALTEL, S.A.': 'EUSKALTEL',
  'TELECABLE DE ASTURIAS, S.A': 'EUSKALTEL',
  'R CABLE Y TELECOMUNICACIONES GALICIA, S.A.': 'EUSKALTEL',
  'AVATEL TELECOM S.A.': 'AVATEL',
  'AVATEL & WIKIKER TELECOM S.L.': 'AVATEL',
  'WIKIKER BROADBAND, S.L.': 'AVATEL',
  'TELEAST DIGITAL, S.L.': 'AVATEL',
  'TVHORADADA MULTIMEDIA, S.L.': 'AVATEL',
  'TVHORADADA MAR MENOR, S.L.': 'AVATEL',
  'CIUDAD SIN CABLES TELECOM SL': 'AVATEL',
  'TELPLAY S.L.': 'AVATEL',
  'CABLEUNIÓN MEDIA, S.L.': 'AVATEL',
  'CABLEMURCIA S.L': 'AVATEL',
  'A2Z TELECOMUNICACIONES, S.L.': 'AVATEL',
  'LEBRIJA TV, S.L.': 'AVATEL',
  'FIBRAMED NETWORKS, S.L.': 'AVATEL',
  'WIFIBYTES, S.L.': 'AVATEL',
  'WIVA TELECOM, S.L.': 'AVATEL',
  'UNION DE REDES DE FIBRA OPTICA, SL': 'AVATEL',
  'TELE ALHAMA, S.L.': 'AVATEL',
  'TELEDISTRIBUCIÓN TOTANA S.L.': 'AVATEL',
  'CABLE ALBUDEITE S.L.': 'AVATEL',
  'REDFIBRA COMUNICACIONES SL': 'AVATEL',
  'ALBACETE SISTEMAS Y SERVICIOS S.L.': 'AVATEL',
  'WIFINITY GLOBAL NETWORK, S.L.': 'AVATEL',
  'OPEGAL TELECOMUNICACIONS S.L.': 'AVATEL',
  'SERVICIO TELEC. PUENTE GENIL': 'AVATEL',
  'RUSCABLE S.L.': 'AVATEL',
  'WIFI LA VALL SL': 'AVATEL',
  'VOZPLUS TELECOMUNICACIONES, S.L.L.': 'AVATEL',
  'INGERTV': 'AVATEL'
};

export const getOperatorColor = (grantee: string, alpha: number = 255): RGBA => {
  const colorKey = getOperatorKey(grantee);
  const baseColor = OPERATOR_COLORS[colorKey];

  return [...baseColor, alpha];
};

export const getProgramColor = (programName: string, alpha: number = 255): RGBA => {
  const mappedProgramName = programName.toUpperCase()
    .replace(" ", "_");

  const baseColor = PROGRAM_COLORS[mappedProgramName];

  return [...baseColor, alpha];
}

export const getOperatorColors = (): Record<string, [number, number, number]> => {
  return OPERATOR_COLORS;
}

export const getProgramColors = (): Record<string, [number, number, number]> => {
  return PROGRAM_COLORS;
}

export const getOperatorNames = (operator: string): string[] => {
  return Object.entries(NAME_TO_OPERATOR).reduce<string[]>((acc, [key, value]) => {
    if (value === operator) {
      acc.push(key);
    }
    return acc;
  }, []);
}

export const getOperatorKey = (grantee: string): string => {
  if (!grantee) return "OTHER";

  const upperName = grantee.toUpperCase();
  return NAME_TO_OPERATOR[upperName] || "OTHER";
};
