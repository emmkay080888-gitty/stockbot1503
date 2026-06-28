/**
 * Wicca & Occult Engine
 *
 * Maps current time against the user's astrological chart to determine:
 * - Current moon phase
 * - Current planetary hours / day of the week correspondences
 * - Elemental balances (Earth, Air, Fire, Water)
 * - Seasonal sabbats and esbats
 */

// ─── Moon Phase ─────────────────────────────────────────────────────────────

/**
 * Calculate the current moon phase (0 = New Moon, 4 = Full Moon).
 * Uses the known lunar cycle of ~29.53 days.
 *
 * @param {Date} [date] - Defaults to now
 * @returns {Object} Moon phase info
 */
function getMoonPhase(date = new Date()) {
  // Known new moon reference: January 1, 2000 was 5.9 days after a new moon
  const knownNewMoon = new Date('2000-01-01T00:00:00Z');
  const lunarCycle = 29.53058867; // days

  const diffDays = (date.getTime() - knownNewMoon.getTime()) / 86400000;
  const daysIntoCycle = ((diffDays % lunarCycle) + lunarCycle) % lunarCycle;
  const phasePercent = daysIntoCycle / lunarCycle;

  const phaseNames = [
    { name: 'New Moon',     symbol: '🌑', description: 'Beginnings, setting intentions, planting seeds' },
    { name: 'Waxing Crescent', symbol: '🌒', description: 'Growth, building momentum, taking action' },
    { name: 'First Quarter',   symbol: '🌓', description: 'Decisions, challenges, overcoming obstacles' },
    { name: 'Waxing Gibbous',  symbol: '🌔', description: 'Refinement, adjustment, preparation' },
    { name: 'Full Moon',       symbol: '🌕', description: 'Manifestation, peak power, illumination' },
    { name: 'Waning Gibbous',  symbol: '🌖', description: 'Gratitude, sharing, distribution' },
    { name: 'Last Quarter',    symbol: '🌗', description: 'Release, letting go, forgiveness' },
    { name: 'Waning Crescent', symbol: '🌘', description: 'Rest, surrender, dreamwork' },
  ];

  // 8 phases, each 1/8 of the cycle
  const phaseIndex = Math.floor(phasePercent * 8) % 8;
  const phase = phaseNames[phaseIndex];

  return {
    ...phase,
    daysIntoCycle: Math.round(daysIntoCycle * 100) / 100,
    illumination: Math.round((1 - Math.cos(phasePercent * 2 * Math.PI)) / 2 * 100),
    percentComplete: Math.round(phasePercent * 100),
  };
}

// ─── Day of Week Correspondences ────────────────────────────────────────────

const DAY_CORRESPONDENCES = {
  sunday:    { planet: 'Sun',     color: 'Gold',    energy: 'Success, vitality, leadership',     crystals: ['Citrine', 'Amber', 'Sunstone'] },
  monday:    { planet: 'Moon',    color: 'Silver',  energy: 'Emotions, intuition, dreams',        crystals: ['Moonstone', 'Pearl', 'Selenite'] },
  tuesday:   { planet: 'Mars',    color: 'Red',     energy: 'Courage, action, passion',           crystals: ['Ruby', 'Garnet', 'Red Jasper'] },
  wednesday: { planet: 'Mercury', color: 'Yellow',  energy: 'Communication, travel, learning',    crystals: ['Tiger\'s Eye', 'Agate', 'Azurite'] },
  thursday:  { planet: 'Jupiter', color: 'Purple',  energy: 'Abundance, expansion, luck',        crystals: ['Amethyst', 'Lapis Lazuli', 'Sapphire'] },
  friday:    { planet: 'Venus',   color: 'Green',   energy: 'Love, beauty, relationships',       crystals: ['Rose Quartz', 'Emerald', 'Jade'] },
  saturday:  { planet: 'Saturn',  color: 'Black',   energy: 'Protection, discipline, lessons',   crystals: ['Onyx', 'Obsidian', 'Hematite'] },
};

function getDayCorrespondence(date = new Date()) {
  const dayName = date.toLocaleDateString('en-US', { weekday: 'long' }).toLowerCase();
  return DAY_CORRESPONDENCES[dayName] ?? {};
}

// ─── Sabbats (Wheel of the Year) ────────────────────────────────────────────

const SABBATS = [
  { name: 'Samhain',     date: 'Oct 31',  energy: 'Death, rebirth, honoring ancestors' },
  { name: 'Yule',        date: 'Dec 21',  energy: 'Winter solstice, renewal, light returning' },
  { name: 'Imbolc',      date: 'Feb 1',   energy: 'Spring beginnings, purification, inspiration' },
  { name: 'Ostara',      date: 'Mar 20',  energy: 'Spring equinox, balance, fertility' },
  { name: 'Beltane',     date: 'May 1',   energy: 'Passion, creativity, union, fire' },
  { name: 'Litha',       date: 'Jun 21',  energy: 'Summer solstice, power, abundance' },
  { name: 'Lughnasadh',  date: 'Aug 1',   energy: 'First harvest, gratitude, strength' },
  { name: 'Mabon',       date: 'Sep 22',  energy: 'Autumn equinox, balance, thanksgiving' },
];

function getClosestSabbat(date = new Date()) {
  const now = date.getTime();
  let closest = null;
  let closestDiff = Infinity;

  for (const sabbat of SABBATS) {
    const sabbatDate = new Date(`${sabbat.date} ${date.getFullYear()}`);
    const diff = Math.abs(sabbatDate.getTime() - now);
    if (diff < closestDiff) {
      closestDiff = diff;
      closest = { ...sabbat, daysAway: Math.round(diff / 86400000) };
    }
  }

  return closest;
}

// ─── Elemental Balance (based on zodiac sign elements) ──────────────────────

const SIGN_ELEMENTS = {
  Aries:       'Fire',
  Leo:         'Fire',
  Sagittarius: 'Fire',
  Taurus:      'Earth',
  Virgo:       'Earth',
  Capricorn:   'Earth',
  Gemini:      'Air',
  Libra:       'Air',
  Aquarius:    'Air',
  Cancer:      'Water',
  Scorpio:     'Water',
  Pisces:      'Water',
};

function getElementalBalance(planets = {}) {
  const counts = { Fire: 0, Earth: 0, Air: 0, Water: 0 };

  for (const [, data] of Object.entries(planets)) {
    const element = SIGN_ELEMENTS[data.sign];
    if (element) counts[element]++;
  }

  const total = Object.values(counts).reduce((a, b) => a + b, 0) || 1;

  return {
    elements: {
      fire:  { percentage: Math.round((counts.Fire / total) * 100),   status: counts.Fire > total / 4 ? 'balanced' : 'lacking' },
      earth: { percentage: Math.round((counts.Earth / total) * 100),  status: counts.Earth > total / 4 ? 'balanced' : 'lacking' },
      air:   { percentage: Math.round((counts.Air / total) * 100),    status: counts.Air > total / 4 ? 'balanced' : 'lacking' },
      water: { percentage: Math.round((counts.Water / total) * 100),  status: counts.Water > total / 4 ? 'balanced' : 'lacking' },
    },
    dominantElement: Object.entries(counts).sort((a, b) => b[1] - a[1])[0][0],
  };
}

// ─── Main Analysis ──────────────────────────────────────────────────────────

/**
 * Full Wicca / Occult reading based on current time and user's astrological chart.
 *
 * @param {Object} params
 * @param {Object} [params.planets] - Planet positions from astrology engine
 * @param {Date}   [params.currentDate]
 * @returns {Object} Wicca reading
 */
export function analyzeWicca({ planets = {}, currentDate = new Date() }) {
  const moon = getMoonPhase(currentDate);
  const dayCorrespondence = getDayCorrespondence(currentDate);
  const closestSabbat = getClosestSabbat(currentDate);
  const elements = getElementalBalance(planets);

  return {
    moonPhase: moon,
    dayCorrespondence,
    sabbat: closestSabbat,
    elementalBalance: elements,
    planetaryHours: {
      note: 'Full planetary hours calculation requires sunrise/sunset times for user location.',
      dayRuler: dayCorrespondence.planet,
    },
    currentSeason: {
      hemisphere: 'Northern', // TODO: accept user location
      season: getSeason(currentDate),
    },
  };
}

function getSeason(date) {
  const m = date.getMonth();
  if (m >= 2 && m <= 4) return 'Spring';
  if (m >= 5 && m <= 7) return 'Summer';
  if (m >= 8 && m <= 10) return 'Autumn';
  return 'Winter';
}

export default { analyzeWicca };
