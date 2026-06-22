/**
 * Numerology Engine
 * 
 * Calculates core numerological values from birth date and name.
 * All numbers are reduced to single digits unless they are Master Numbers (11, 22, 33).
 */

// ─── Helpers ────────────────────────────────────────────────────────────────

/** Reduce a number to a single digit (or Master Number). */
function reduceToDigit(n, allowMaster = true) {
  if (n === 0) return 0;
  let num = n;
  while (num > 9) {
    // Master numbers 11, 22, 33 are not reduced further
    if (allowMaster && (num === 11 || num === 22 || num === 33)) break;
    num = String(num)
      .split('')
      .reduce((sum, d) => sum + parseInt(d, 10), 0);
  }
  return num;
}

/** Sum the digit values of a date component (day, month, or year). */
function sumDigits(n) {
  return String(Math.abs(n))
    .split('')
    .reduce((sum, d) => sum + parseInt(d, 10), 0);
}

// ─── Letter → Number mapping (Pythagorean system) ───────────────────────────

const LETTER_VALUES = {
  a: 1, b: 2, c: 3, d: 4, e: 5, f: 6, g: 7, h: 8, i: 9,
  j: 1, k: 2, l: 3, m: 4, n: 5, o: 6, p: 7, q: 8, r: 9,
  s: 1, t: 2, u: 3, v: 4, w: 5, x: 6, y: 7, z: 8,
};

const VOWELS = new Set(['a', 'e', 'i', 'o', 'u']);

function letterValue(c) {
  return LETTER_VALUES[c.toLowerCase()] ?? 0;
}

function isVowel(c) {
  return VOWELS.has(c.toLowerCase());
}

/** Sum letter values in a name string, optionally filtering by vowel/consonant. */
function sumName(name, filterFn) {
  const chars = name.replace(/[^a-zA-Z]/g, '').split('');
  const filtered = filterFn ? chars.filter(filterFn) : chars;
  const total = filtered.reduce((sum, c) => sum + letterValue(c), 0);
  return reduceToDigit(total);
}

// ─── Core Number Calculations ───────────────────────────────────────────────

/**
 * Life Path Number — from birth date (month, day, year).
 * The most important number in numerology. Represents life's purpose.
 */
function lifePathNumber(birthDate) {
  const month = birthDate.getMonth() + 1;   // 1–12
  const day   = birthDate.getDate();          // 1–31
  const year  = birthDate.getFullYear();

  const monthSum = sumDigits(month);
  const daySum   = sumDigits(day);
  const yearSum  = sumDigits(year);

  // Reduce month, day, year separately first
  const monthRoot = reduceToDigit(monthSum);
  const dayRoot   = reduceToDigit(daySum);
  const yearRoot  = reduceToDigit(yearSum);

  // Sum the three roots
  const total = monthRoot + dayRoot + yearRoot;
  return reduceToDigit(total);
}

/**
 * Expression (Destiny) Number — from the full birth name.
 * Represents natural talents, abilities, and shortcomings.
 */
function expressionNumber(fullName) {
  if (!fullName) return null;
  return sumName(fullName, null);
}

/**
 * Soul Urge (Heart's Desire) Number — from vowels in the full birth name.
 * Represents innermost desires, motivations, and what the soul craves.
 */
function soulUrgeNumber(fullName) {
  if (!fullName) return null;
  return sumName(fullName, (c) => isVowel(c));
}

/**
 * Personality Number — from consonants in the full birth name.
 * Represents how others perceive you — the outer persona.
 */
function personalityNumber(fullName) {
  if (!fullName) return null;
  return sumName(fullName, (c) => !isVowel(c));
}

/**
 * Personal Year Number — based on current date + birth month/day.
 * Reveals the theme of the current year.
 */
function personalYearNumber(birthDate, currentDate = new Date()) {
  const bMonth = birthDate.getMonth() + 1;
  const bDay   = birthDate.getDate();
  const cYear  = currentDate.getFullYear();

  const total = sumDigits(bMonth) + sumDigits(bDay) + sumDigits(cYear);
  return reduceToDigit(total);
}

/**
 * Personal Month Number — Personal Year + current calendar month.
 * Reveals the theme of the current month.
 */
function personalMonthNumber(birthDate, currentDate = new Date()) {
  const py = personalYearNumber(birthDate, currentDate);
  const cMonth = currentDate.getMonth() + 1;
  return reduceToDigit(py + sumDigits(cMonth));
}

/**
 * Personal Day Number — Personal Month + current calendar day.
 * Reveals the theme of the current day.
 */
function personalDayNumber(birthDate, currentDate = new Date()) {
  const pm = personalMonthNumber(birthDate, currentDate);
  const cDay = currentDate.getDate();
  return reduceToDigit(pm + sumDigits(cDay));
}

/**
 * Life Path Cycles — divides life into three major periods based on the
 * month, day, and year roots. Each cycle lasts ~27-30 years.
 */
function lifePathCycles(birthDate) {
  const month = birthDate.getMonth() + 1;
  const day   = birthDate.getDate();
  const year  = birthDate.getFullYear();

  return {
    firstCycle:  reduceToDigit(sumDigits(month)),   // Formative years
    middleCycle: reduceToDigit(sumDigits(day)),      // Productive years
    matureCycle: reduceToDigit(sumDigits(year)),     // Mature years
  };
}

/**
 * Challenge Numbers — obstacles to overcome in life.
 * Derived from the birth date.
 */
function challengeNumbers(birthDate) {
  const month = birthDate.getMonth() + 1;
  const day   = birthDate.getDate();
  const year  = birthDate.getFullYear();

  const m = reduceToDigit(sumDigits(month));
  const d = reduceToDigit(sumDigits(day));
  const y = reduceToDigit(sumDigits(year));

  return {
    firstChallenge:  Math.abs(d - m),
    secondChallenge: Math.abs(y - d),
    thirdChallenge:  Math.abs(Math.abs(y - d) - Math.abs(d - m)),
    fourthChallenge: Math.abs(y - m),
  };
}

/**
 * Karmic Debt Numbers — appear when certain numbers come up during reduction.
 * Common debt numbers: 13, 14, 16, 19.
 */
function karmicDebts(birthDate, fullName) {
  const debts = [];

  // Check birth date for karmic debt numbers
  const month = birthDate.getMonth() + 1;
  const day   = birthDate.getDate();
  const year  = birthDate.getFullYear();

  const dateParts = [month, day, year];
  for (const part of dateParts) {
    if (part === 13 || part === 14 || part === 16 || part === 19) {
      debts.push({ source: 'birthDate', value: part });
    }
  }

  // Check name-based numbers
  if (fullName) {
    const expr = sumName(fullName, null);
    // The raw sum before reduction might be a karmic debt number
    const raw = fullName
      .replace(/[^a-zA-Z]/g, '')
      .split('')
      .reduce((sum, c) => sum + letterValue(c), 0);

    const karmicValues = [13, 14, 16, 19];
    for (const kv of karmicValues) {
      // Check if the name sum before full reduction contains karmic numbers
      const rawStr = String(raw);
      if (rawStr.includes(String(kv))) {
        debts.push({ source: 'name', value: kv });
      }
    }
  }

  return debts;
}

// ─── Number Meanings ────────────────────────────────────────────────────────

const NUMBER_MEANINGS = {
  1: { keyword: 'Independence',      positive: 'Leader, pioneer, original',      negative: 'Arrogant, aggressive, lonely' },
  2: { keyword: 'Cooperation',       positive: 'Diplomatic, patient, intuitive',  negative: 'Over-sensitive, timid, indecisive' },
  3: { keyword: 'Expression',        positive: 'Creative, social, optimistic',    negative: 'Scattered, superficial, dramatic' },
  4: { keyword: 'Stability',         positive: 'Practical, disciplined, loyal',   negative: 'Rigid, stubborn, overly cautious' },
  5: { keyword: 'Freedom',           positive: 'Adventurous, versatile, dynamic', negative: 'Restless, irresponsible, impulsive' },
  6: { keyword: 'Harmony',           positive: 'Nurturing, responsible, loving',  negative: 'Meddling, self-righteous, anxious' },
  7: { keyword: 'Wisdom',            positive: 'Analytical, spiritual, insightful', negative: 'Secretive, aloof, cynical' },
  8: { keyword: 'Abundance',         positive: 'Ambitious, authoritative, driven', negative: 'Materialistic, power-hungry, workaholic' },
  9: { keyword: 'Humanitarianism',   positive: 'Compassionate, artistic, generous', negative: 'Dramatic, resentful, emotionally turbulent' },
  11: { keyword: 'Intuition',        positive: 'Visionary, inspirational, enlightened', negative: 'Overwhelmed, anxious, disconnected' },
  22: { keyword: 'Master Builder',   positive: 'Visionary, practical, powerful manifestor', negative: 'Overwhelmed by potential, unrealistic' },
  33: { keyword: 'Master Teacher',   positive: 'Compassionate healer, selfless, elevating', negative: 'Martyr complex, emotionally drained' },
};

function getNumberMeaning(n) {
  return NUMBER_MEANINGS[n] ?? { keyword: 'Unknown', positive: '', negative: '' };
}

// ─── Main Analysis ──────────────────────────────────────────────────────────

/**
 * Full numerological analysis for a user.
 *
 * @param {Object} params
 * @param {Date}   params.birthDate
 * @param {string} [params.fullName] - Optional full birth name for Expression/Soul Urge
 * @param {Date}   [params.currentDate] - Defaults to now
 * @returns {Object} Complete numerology reading
 */
export function analyzeNumerology({ birthDate, fullName = null, currentDate = new Date() }) {
  const lp  = lifePathNumber(birthDate);
  const expr  = expressionNumber(fullName);
  const soul  = soulUrgeNumber(fullName);
  const pers  = personalityNumber(fullName);
  const py    = personalYearNumber(birthDate, currentDate);
  const pm    = personalMonthNumber(birthDate, currentDate);
  const pd    = personalDayNumber(birthDate, currentDate);
  const cycles = lifePathCycles(birthDate);
  const challenges = challengeNumbers(birthDate);
  const debts = karmicDebts(birthDate, fullName);

  return {
    lifePath: {
      number: lp,
      meaning: getNumberMeaning(lp),
      description: `Life Path ${lp}: The ${getNumberMeaning(lp).keyword} path. ${getNumberMeaning(lp).positive}.`,
    },
    expression: fullName ? {
      number: expr,
      meaning: getNumberMeaning(expr),
      description: `Expression ${expr}: ${getNumberMeaning(expr).keyword}. ${getNumberMeaning(expr).positive}.`,
    } : null,
    soulUrge: fullName ? {
      number: soul,
      meaning: getNumberMeaning(soul),
      description: `Soul Urge ${soul}: ${getNumberMeaning(soul).keyword}. Your heart desires ${getNumberMeaning(soul).positive.toLowerCase()}.`,
    } : null,
    personality: fullName ? {
      number: pers,
      meaning: getNumberMeaning(pers),
      description: `Personality ${pers}: ${getNumberMeaning(pers).keyword}. Others see you as ${getNumberMeaning(pers).positive.toLowerCase()}.`,
    } : null,
    currentTiming: {
      personalYear: {
        number: py,
        meaning: getNumberMeaning(py),
        description: `Personal Year ${py}: ${getNumberMeaning(py).keyword} year. ${getYearDescription(py)}`,
      },
      personalMonth: {
        number: pm,
        meaning: getNumberMeaning(pm),
      },
      personalDay: {
        number: pd,
        meaning: getNumberMeaning(pd),
      },
    },
    lifeCycles: {
      firstCycle:  { number: cycles.firstCycle,  meaning: getNumberMeaning(cycles.firstCycle) },
      middleCycle: { number: cycles.middleCycle, meaning: getNumberMeaning(cycles.middleCycle) },
      matureCycle: { number: cycles.matureCycle, meaning: getNumberMeaning(cycles.matureCycle) },
    },
    challenges: {
      first:  { number: challenges.firstChallenge,  description: `First Challenge: ${challenges.firstChallenge} — ${getChallengeDescription(challenges.firstChallenge)}` },
      second: { number: challenges.secondChallenge, description: `Second Challenge: ${challenges.secondChallenge} — ${getChallengeDescription(challenges.secondChallenge)}` },
      third:  { number: challenges.thirdChallenge,  description: `Third Challenge: ${challenges.thirdChallenge} — ${getChallengeDescription(challenges.thirdChallenge)}` },
      fourth: { number: challenges.fourthChallenge, description: `Fourth Challenge: ${challenges.fourthChallenge} — ${getChallengeDescription(challenges.fourthChallenge)}` },
    },
    karmicDebts: debts.length > 0 ? debts.map(d => ({
      value: d.value,
      description: `Karmic Debt ${d.value}: ${getKarmicDebtDescription(d.value)}`,
    })) : null,
  };
}

function getYearDescription(py) {
  const descriptions = {
    1: 'New beginnings, fresh starts, independence.',
    2: 'Patience, cooperation, relationships and partnerships.',
    3: 'Creativity, socializing, self-expression.',
    4: 'Hard work, discipline, building foundations.',
    5: 'Change, freedom, adventure, major shifts.',
    6: 'Family, responsibility, home and harmony.',
    7: 'Rest, reflection, spiritual growth, inner wisdom.',
    8: 'Power, success, financial abundance, career growth.',
    9: 'Completion, release, humanitarianism, endings.',
    11: 'Spiritual awakening, inspiration, heightened intuition.',
    22: 'Master building, turning dreams into reality at scale.',
    33: 'Compassionate service, teaching at a master level.',
  };
  return descriptions[py] ?? 'A year of growth and discovery.';
}

function getChallengeDescription(n) {
  const map = {
    0: 'No specific challenge — a free and easy path.',
    1: 'Learning assertiveness and independence.',
    2: 'Overcoming sensitivity and building diplomacy.',
    3: 'Focusing creative energy and avoiding scattering.',
    4: 'Building discipline and finding security.',
    5: 'Embracing change without restlessness.',
    6: 'Balancing responsibility to others with self-care.',
    7: 'Trusting your inner wisdom over external opinions.',
    8: 'Using power and abundance wisely.',
    9: 'Letting go and embracing universal love.',
  };
  return map[n] ?? 'An area of significant growth.';
}

function getKarmicDebtDescription(n) {
  const map = {
    13: 'Past-life laziness has created a need for hard work and discipline in this life.',
    14: 'Past-life abuse of freedom requires responsible use of independence now.',
    16: 'Past-life ego issues require humility and spiritual growth to overcome.',
    19: 'Past-life abuse of power requires learning independence through service.',
  };
  return map[n] ?? 'A karmic lesson to be learned.';
}

export default {
  analyzeNumerology,
  lifePathNumber,
  expressionNumber,
  soulUrgeNumber,
  personalityNumber,
  personalYearNumber,
  personalMonthNumber,
  karmicDebts,
};
