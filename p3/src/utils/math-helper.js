/**
 * math-helper.js
 *
 * Standalone mathematical utilities for esoteric calculations.
 * Used across all engine branches for number reduction and digit operations.
 *
 * All functions are pure — no dependencies on the rest of the app.
 */

// ─── Digit Operations ───────────────────────────────────────────────────────

/** Sum the digits of a number. e.g., 1990 → 1+9+9+0 = 19 */
export function sumDigits(n) {
  return String(Math.abs(n))
    .split('')
    .reduce((sum, d) => sum + parseInt(d, 10), 0);
}

/** Reduce a number to a single digit (1–9), preserving Master Numbers (11, 22, 33). */
export function reduceToDigit(n, allowMaster = true) {
  if (n === 0) return 0;
  let num = Math.abs(n);
  while (num > 9) {
    if (allowMaster && (num === 11 || num === 22 || num === 33)) break;
    num = String(num)
      .split('')
      .reduce((sum, d) => sum + parseInt(d, 10), 0);
  }
  return num;
}

/** Check if a number is a Master Number. */
export function isMasterNumber(n) {
  return [11, 22, 33].includes(n);
}

/** Get the digit root of a number (always reduces, even Master Numbers). */
export function digitRoot(n) {
  return reduceToDigit(n, false);
}

// ─── Numerology Calculations ────────────────────────────────────────────────

/**
 * Life Path Number — the most important number in numerology.
 * Calculated from birth date (month, day, year).
 *
 * @param {number|string} month - 1–12
 * @param {number|string} day - 1–31
 * @param {number|string} year - e.g., 1990
 * @returns {{ number: number, masterNumber: boolean }}
 */
export function calculateLifePath(month, day, year) {
  const mRoot = reduceToDigit(sumDigits(month));
  const dRoot = reduceToDigit(sumDigits(day));
  const yRoot = reduceToDigit(sumDigits(year));

  const total = mRoot + dRoot + yRoot;
  const number = reduceToDigit(total);

  return {
    number,
    masterNumber: isMasterNumber(total) || isMasterNumber(number),
    roots: { month: mRoot, day: dRoot, year: yRoot },
  };
}

/**
 * Parse a birth date string into month, day, year and compute Life Path.
 *
 * @param {string} birthDateStr - ISO date string, e.g., "1990-06-15"
 * @returns {{ month: number, day: number, year: number, lifePath: { number: number, masterNumber: boolean } }}
 */
export function lifePathFromDateString(birthDateStr) {
  const date = new Date(birthDateStr);
  if (isNaN(date.getTime())) {
    throw new Error(`Invalid date string: "${birthDateStr}". Use ISO format, e.g., "1990-06-15".`);
  }

  const month = date.getMonth() + 1;
  const day = date.getDate();
  const year = date.getFullYear();

  return {
    month,
    day,
    year,
    lifePath: calculateLifePath(month, day, year),
  };
}

// ─── Number Meanings ────────────────────────────────────────────────────────

const NUMBER_MEANINGS = {
  1: { keyword: 'Independence',      element: 'Fire',    polarity: 'masculine', positive: 'Leader, pioneer, original',      negative: 'Arrogant, aggressive, lonely' },
  2: { keyword: 'Cooperation',       element: 'Water',   polarity: 'feminine',  positive: 'Diplomatic, patient, intuitive',  negative: 'Over-sensitive, timid, indecisive' },
  3: { keyword: 'Expression',        element: 'Air',     polarity: 'masculine', positive: 'Creative, social, optimistic',    negative: 'Scattered, superficial, dramatic' },
  4: { keyword: 'Stability',         element: 'Earth',   polarity: 'feminine',  positive: 'Practical, disciplined, loyal',   negative: 'Rigid, stubborn, overly cautious' },
  5: { keyword: 'Freedom',           element: 'Air',     polarity: 'masculine', positive: 'Adventurous, versatile, dynamic', negative: 'Restless, irresponsible, impulsive' },
  6: { keyword: 'Harmony',           element: 'Water',   polarity: 'feminine',  positive: 'Nurturing, responsible, loving',  negative: 'Meddling, self-righteous, anxious' },
  7: { keyword: 'Wisdom',            element: 'Water',   polarity: 'feminine',  positive: 'Analytical, spiritual, insightful', negative: 'Secretive, aloof, cynical' },
  8: { keyword: 'Abundance',         element: 'Earth',   polarity: 'masculine', positive: 'Ambitious, authoritative, driven', negative: 'Materialistic, power-hungry, workaholic' },
  9: { keyword: 'Humanitarianism',   element: 'Fire',    polarity: 'masculine', positive: 'Compassionate, artistic, generous', negative: 'Dramatic, resentful, emotionally turbulent' },
  11: { keyword: 'Intuition',        element: 'Spirit',  polarity: 'feminine',  positive: 'Visionary, inspirational, enlightened', negative: 'Overwhelmed, anxious, disconnected' },
  22: { keyword: 'Master Builder',   element: 'Spirit',  polarity: 'masculine', positive: 'Visionary, practical, powerful manifestor', negative: 'Overwhelmed by potential, unrealistic' },
  33: { keyword: 'Master Teacher',   element: 'Spirit',  polarity: 'feminine',  positive: 'Compassionate healer, selfless, elevating', negative: 'Martyr complex, emotionally drained' },
};

/** Get the full meaning object for a number. */
export function getNumberMeaning(n) {
  return NUMBER_MEANINGS[n] ?? { keyword: 'Unknown', element: 'Unknown', polarity: 'neutral', positive: '', negative: '' };
}

// ─── Modular Arithmetic / Cyclic ────────────────────────────────────────────

/** Map a number to a position on a cycle (1-based). e.g., modCycle(13, 12) → 1 */
export function modCycle(value, cycleLength) {
  return ((value - 1) % cycleLength) + 1;
}

/** Convert degrees (0–360) to zodiac sign index (0–11). */
export function degreeToSignIndex(degrees) {
  return Math.floor(((degrees % 360) / 30)) % 12;
}

/** Get zodiac sign name from index. */
export function signName(index) {
  const signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'];
  return signs[((index % 12) + 12) % 12];
}

export default {
  sumDigits,
  reduceToDigit,
  isMasterNumber,
  digitRoot,
  calculateLifePath,
  lifePathFromDateString,
  getNumberMeaning,
  modCycle,
  degreeToSignIndex,
  signName,
};
