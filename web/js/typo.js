// Česká typografie: nezlomitelné mezery za jednopísmennými předložkami, mezi číslem a jednotkou a v datu;
// čísla s desetinnou čárkou. Všechny generované texty procházejí přes typo().
export const NB = " ";

const PREDLOZKY = /(^|[\s(„“"'])([ksvzouaiKSVZOUAI])\s+(?=\S)/g;
const JEDNOTKY = /(\d)\s+(cm|mm|m³\/s|m³|m|h|%|km|ha|let|hod|kB|MB)(?![\p{L}\d])/gu;
const DATUM = /(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})(?:\s+(\d{1,2}:\d{2}))?/g;
const TISICE = /(\d)[  ](\d{3})(?!\d)/g;

export function typo(s) {
  return String(s)
    .replace(DATUM, (m, d, mo, y, t) => `${d}.${NB}${mo}.${NB}${y}${t ? NB + t : ""}`)
    .replace(JEDNOTKY, `$1${NB}$2`)
    .replace(PREDLOZKY, `$1$2${NB}`)
    .replace(TISICE, `$1${NB}$2`);
}

export function cislo(x, mist = 0) {
  if (x == null || Number.isNaN(x)) return "–";
  const [c, d] = Math.abs(x).toFixed(mist).split(".");
  return (x < 0 ? "−" : "") + c.replace(/\B(?=(\d{3})+(?!\d))/g, NB) + (d ? "," + d : "");
}

export const jedn = (x, j, mist = 0) => cislo(x, mist) + NB + j;
export const cm = (x, mist = 0) => jedn(x, "cm", mist);
export const znamenko = (x, mist = 0) => (x >= 0 ? "+" : "−") + cislo(Math.abs(x), mist);

// Časy jsou v českém čase jako "2011-01-15T09:00"; počítáme s nimi jako s UTC, aby prohlížeč nic neposouval.
export function parseIso(iso) {
  const [d, t = "00:00"] = iso.split("T");
  const [y, m, dd] = d.split("-").map(Number);
  const [h, mi] = t.split(":").map(Number);
  return new Date(Date.UTC(y, m - 1, dd, h, mi));
}
export const isoZ = (d) => d.toISOString().slice(0, 16);
export const posun = (iso, h) => isoZ(new Date(parseIso(iso).getTime() + h * 3600e3));
const dvoj = (n) => String(n).padStart(2, "0");
export function hodina(iso) {
  const d = parseIso(iso);
  return `${d.getUTCHours()}:${dvoj(d.getUTCMinutes())}`;
}
export function datum(iso) {
  const d = parseIso(iso);
  return `${d.getUTCDate()}.${NB}${d.getUTCMonth() + 1}.${NB}${d.getUTCFullYear()}`;
}
export const datumCas = (iso) => `${datum(iso)}${NB}${hodina(iso)}`;
export function denMesic(iso) {
  const d = parseIso(iso);
  return `${d.getUTCDate()}.${NB}${d.getUTCMonth() + 1}.`;
}
