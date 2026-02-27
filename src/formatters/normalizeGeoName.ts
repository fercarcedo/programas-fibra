const LOWERCASE_PARTICLES = new Set([
  "a",
  "al",
  "d",
  "da",
  "de",
  "del",
  "do",
  "dos",
  "e",
  "el",
  "en",
  "i",
  "la",
  "las",
  "los",
  "o",
  "u",
  "y",
]);

const TOKEN_PATTERN =
  /[A-Za-zÀ-ÖØ-öø-ÿ]+(?:'[A-Za-zÀ-ÖØ-öø-ÿ]+)?|\d+|[^A-Za-zÀ-ÖØ-öø-ÿ\d]+/g;
const ROMAN_NUMERAL_PATTERN =
  /^m{0,4}(cm|cd|d?c{0,3})(xc|xl|l?x{0,3})(ix|iv|v?i{1,3})$/;

function normalizeSimpleWord(
  word: string,
  segmentStart: boolean,
  forceCapitalize: boolean,
): string {
  if (!word) return word;
  if (ROMAN_NUMERAL_PATTERN.test(word)) return word.toUpperCase();
  if (LOWERCASE_PARTICLES.has(word) && !segmentStart && !forceCapitalize) {
    return word;
  }

  return `${word[0].toUpperCase()}${word.slice(1)}`;
}

function normalizeWord(word: string, segmentStart: boolean): string {
  const lower = word.toLowerCase();

  if (lower.includes("'")) {
    const parts = lower.split("'");
    const [first, ...rest] = parts;
    const normalizedFirst = normalizeSimpleWord(first, segmentStart, false);
    const normalizedRest = rest.map((part) =>
      normalizeSimpleWord(part, true, true),
    );
    return [normalizedFirst, ...normalizedRest].join("'");
  }

  return normalizeSimpleWord(lower, segmentStart, false);
}

export function normalizeGeoName(value?: string): string {
  if (!value) return "";

  const normalized = value.replace(/\s+/g, " ").trim();
  if (!normalized) return normalized;

  let segmentStart = true;
  const output: string[] = [];

  for (const token of normalized.match(TOKEN_PATTERN) ?? []) {
    if (/[A-Za-zÀ-ÖØ-öø-ÿ]/.test(token[0])) {
      output.push(normalizeWord(token, segmentStart));
      segmentStart = false;
    } else {
      output.push(token);
      if (
        token.includes("/") ||
        token.includes("(") ||
        token.includes("-") ||
        token.includes(",")
      ) {
        segmentStart = true;
      }
    }
  }

  return output.join("");
}
