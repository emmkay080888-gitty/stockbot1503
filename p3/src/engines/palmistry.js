/**
 * Palmistry Engine (Text-based Questionnaire)
 *
 * For v1, palmistry is handled via a text-based questionnaire where the user
 * describes their hand features (line lengths, depths, mounts).
 *
 * TODO v2: Image upload + CV-based hand analysis.
 */

// ─── Hand Shape Types ───────────────────────────────────────────────────────

const HAND_SHAPES = {
  earth:  { keyword: 'Earth',  description: 'Square palm, short fingers, thick skin — practical, grounded, reliable', element: 'Earth' },
  air:    { keyword: 'Air',    description: 'Square palm, long fingers, prominent knuckles — intellectual, communicative, analytical', element: 'Air' },
  water:  { keyword: 'Water',   description: 'Long palm, long fingers, flexible — intuitive, emotional, artistic', element: 'Water' },
  fire:   { keyword: 'Fire',    description: 'Square or rectangular palm, short fingers — passionate, energetic, charismatic', element: 'Fire' },
};

// ─── Line Meanings ──────────────────────────────────────────────────────────

function interpretHeartLine(length, depth, curvature) {
  const interpretations = {
    long:    'Deep capacity for love, idealism in relationships',
    medium:  'Balanced emotional expression, practical in love',
    short:   'Self-sufficient emotionally, focused on independence',
  };

  const depthInterpretations = {
    deep:    'Intense emotions, passionate nature, strong feelings',
    normal:  'Balanced emotional expression',
    faint:   'Reserved emotions, private inner world, sensitive',
  };

  const curveInterpretations = {
    curved:  'Expressive, warm, emotionally open with others',
    straight: 'More reserved,理性 logical in emotional matters',
  };

  return {
    description: `Heart Line (${length}, ${depth}, ${curvature}): ${interpretations[length] ?? ''}. ${depthInterpretations[depth] ?? ''}. ${curveInterpretations[curvature] ?? ''}`,
    traits: length === 'long' ? ['Romantic', 'Idealistic', 'Warm'] : length === 'short' ? ['Independent', 'Self-sufficient'] : ['Balanced', 'Practical'],
  };
}

function interpretHeadLine(length, depth, angle) {
  const lengthInterpretations = {
    long:    'Deep thinker, analytical, enjoys complex problem-solving',
    medium:  'Practical thinker, good balance of logic and creativity',
    short:   'Quick thinker, decisive, prefers action over analysis',
  };

  const depthInterpretations = {
    deep:    'Sharp memory, focused concentration, strong mental stamina',
    normal:  'Good mental energy, consistent thinking patterns',
    faint:   'Easily distracted, prefers intuitive over logical thinking',
  };

  const angleInterpretations = {
    downward: 'Creative, imaginative, intuitive thinker',
    straight: 'Practical, logical, realistic thinker',
    upward:   'Optimistic, idealistic, big-picture thinker',
  };

  return {
    description: `Head Line (${length}, ${depth}, ${angle}): ${lengthInterpretations[length] ?? ''}. ${depthInterpretations[depth] ?? ''}. ${angleInterpretations[angle] ?? ''}`,
    traits: length === 'long' ? ['Analytical', 'Detail-oriented'] : ['Decisive', 'Quick-thinking'],
  };
}

function interpretLifeLine(length, depth, shape) {
  const lengthInterpretations = {
    long:    'Strong vitality, robust health, enduring energy',
    medium:  'Good energy levels, normal life force',
    short:   'Intense, lives in the moment, may take risks',
  };

  const depthInterpretations = {
    deep:    'Powerful life force, resilient, strong constitution',
    normal:  'Steady energy, balanced health',
    faint:   'Sensitive energy, easily drained, needs self-care',
  };

  const shapeInterpretations = {
    curved:  'Adventurous, loves travel and new experiences',
    straight: 'Cautious, prefers routine and familiar surroundings',
    wide:    'Energetic, enthusiastic, embraces life fully',
  };

  return {
    description: `Life Line (${length}, ${depth}, ${shape}): ${lengthInterpretations[length] ?? ''}. ${depthInterpretations[depth] ?? ''}. ${shapeInterpretations[shape] ?? ''}`,
    traits: length === 'long' ? ['Energetic', 'Resilient', 'Enduring'] : ['Intense', 'Risk-taking'],
  };
}

// ─── Mounts ─────────────────────────────────────────────────────────────────

const MOUNT_INTERPRETATIONS = {
  prominent: 'Strengthened energy of that planetary influence, dominant traits',
  normal:    'Balanced expression of those qualities',
  flat:      'Underdeveloped or suppressed energy in that area',
};

const MOUNTS = {
  mountOfVenus:  { planet: 'Venus',  qualities: 'Love, passion, sensuality, creativity' },
  mountOfJupiter: { planet: 'Jupiter', qualities: 'Ambition, leadership, confidence, generosity' },
  mountOfSaturn: { planet: 'Saturn',  qualities: 'Wisdom, responsibility, discipline, solitude' },
  mountOfApollo: { planet: 'Sun',     qualities: 'Creativity, brilliance, warmth, success' },
  mountOfMercury: { planet: 'Mercury', qualities: 'Communication, wit, business acumen' },
  mountOfMars:   { planet: 'Mars',    qualities: 'Courage, aggression, resilience, drive' },
  mountOfLuna:   { planet: 'Moon',    qualities: 'Intuition, imagination, empathy, psychic ability' },
};

function interpretMount(mountName, fullness) {
  const mount = MOUNTS[mountName];
  if (!mount) return null;

  return {
    mount: mountName,
    planet: mount.planet,
    qualities: mount.qualities,
    fullness: MOUNT_INTERPRETATIONS[fullness] ?? 'Balanced expression',
  };
}

// ─── Main Analysis ──────────────────────────────────────────────────────────

/**
 * Analyze palmistry based on questionnaire answers.
 *
 * @param {Object} questionnaire - User's descriptions of their hand features
 * @param {string} [questionnaire.handShape] - 'earth', 'air', 'water', 'fire'
 * @param {string} [questionnaire.heartLength] - 'long', 'medium', 'short'
 * @param {string} [questionnaire.heartDepth] - 'deep', 'normal', 'faint'
 * @param {string} [questionnaire.heartCurvature] - 'curved', 'straight'
 * @param {string} [questionnaire.headLength] - 'long', 'medium', 'short'
 * @param {string} [questionnaire.headDepth] - 'deep', 'normal', 'faint'
 * @param {string} [questionnaire.headAngle] - 'downward', 'straight', 'upward'
 * @param {string} [questionnaire.lifeLength] - 'long', 'medium', 'short'
 * @param {string} [questionnaire.lifeDepth] - 'deep', 'normal', 'faint'
 * @param {string} [questionnaire.lifeShape] - 'curved', 'straight', 'wide'
 * @param {Object} [questionnaire.mounts] - e.g. { mountOfVenus: 'prominent', mountOfSaturn: 'normal' }
 * @returns {Object} Palmistry reading
 */
export function analyzePalmistry(questionnaire = {}) {
  const {
    handShape,
    heartLength, heartDepth, heartCurvature,
    headLength, headDepth, headAngle,
    lifeLength, lifeDepth, lifeShape,
    mounts = {},
  } = questionnaire;

  const result = {
    handShape: handShape ? HAND_SHAPES[handShape] ?? null : null,
    lines: {},
    mounts: {},
    generalCharacter: [],
  };

  // Lines
  if (heartLength && heartDepth && heartCurvature) {
    result.lines.heart = interpretHeartLine(heartLength, heartDepth, heartCurvature);
    result.generalCharacter.push(...result.lines.heart.traits);
  }

  if (headLength && headDepth && headAngle) {
    result.lines.head = interpretHeadLine(headLength, headDepth, headAngle);
    result.generalCharacter.push(...result.lines.head.traits);
  }

  if (lifeLength && lifeDepth && lifeShape) {
    result.lines.life = interpretLifeLine(lifeLength, lifeDepth, lifeShape);
    result.generalCharacter.push(...result.lines.life.traits);
  }

  // Mounts
  for (const [mountName, fullness] of Object.entries(mounts)) {
    result.mounts[mountName] = interpretMount(mountName, fullness);
  }

  // Deduplicate traits
  result.generalCharacter = [...new Set(result.generalCharacter)];

  // Questionnaire template for v1 text-based input
  result.questionnaire = {
    handShape: ['earth - Square palm, short fingers, thick skin', 'air - Square palm, long fingers, prominent knuckles', 'water - Long palm, long fingers, flexible, artistic', 'fire - Square/rectangular palm, short fingers'],
    heartLine:  { length: ['long', 'medium', 'short'], depth: ['deep', 'normal', 'faint'], curvature: ['curved', 'straight'] },
    headLine:   { length: ['long', 'medium', 'short'], depth: ['deep', 'normal', 'faint'], angle: ['downward', 'straight', 'upward'] },
    lifeLine:   { length: ['long', 'medium', 'short'], depth: ['deep', 'normal', 'faint'], shape: ['curved', 'straight', 'wide'] },
    mounts:     ['mountOfVenus', 'mountOfJupiter', 'mountOfSaturn', 'mountOfApollo', 'mountOfMercury', 'mountOfMars', 'mountOfLuna'],
  };

  return result;
}

export default { analyzePalmistry };
