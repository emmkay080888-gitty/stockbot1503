/**
 * EsotericEngine — Master Orchestration Service
 *
 * Accepts minimal user input (birthdate, location, question) and runs it through
 * all four mystical lenses in parallel, then synthesizes the results into a
 * unified reading with deep question-focused analysis, predictions, guidance, and remedies.
 *
 * Pipeline:
 *   1. Interpret the user's question (what domain, what do they really need?)
 *   2. Math Layer (Astrology + Numerology)
 *   3. Environmental Layer (Wicca / Occult)
 *   4. Synthesis Layer (cross-reference & alignments, weighted by question)
 *   5. Question-Focused Guidance (deeply tailored)
 *   6. Timeline Predictions (focused on the question)
 *   7. Targeted Remedies (specific to what they asked)
 */

import { analyzeNumerology } from './numerology.js';
import { analyzeAstrology } from './astrology.js';
import { analyzeWicca } from './wicca.js';
import { analyzePalmistry } from './palmistry.js';
import { geocode } from '../utils/geocoder.js';
import { interpretQuestion, GUIDANCE_TEMPLATES, getQuestionRemedies } from '../utils/question-interpreter.js';

// ─── Helpers ────────────────────────────────────────────────────────────────

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

// ─── Synthesis: Cross-Reference Engine ──────────────────────────────────────

/**
 * Finds alignments across all branches, weighted by relevance to the user's question.
 */
function synthesizeAlignments(numerology, astrology, wicca, palmistry, questionAnalysis) {
  const alignments = [];
  const py = numerology.currentTiming?.personalYear?.number;
  const astroHouses = astrology?.houses;
  const domain = questionAnalysis.primary;
  const activeDomains = questionAnalysis.activeDomains;
  const isRelevant = (domainKeywords) => domainKeywords.some(k => activeDomains.some(d =>
    d.label.toLowerCase().includes(k) || k.includes(d.label.toLowerCase())
  ));

  // ── Numerological timing × Astrological houses ──

  // Career alignment
  if (py === 8 && astroHouses?.[10]) {
    alignments.push({
      type: 'career',
      strength: 'strong',
      title: 'Career Transition',
      description: `Personal Year ${py} (${numerology.currentTiming.personalYear.meaning.keyword}) aligns with the 10th House of Career. This is a powerful time for professional advancement.`,
      sources: ['numerology', 'astrology'],
      questionRelevant: domain.label === 'Career & Finances',
    });
  }

  // Spiritual alignment
  if (py === 7 && astroHouses?.[12]) {
    alignments.push({
      type: 'spiritual',
      strength: 'strong',
      title: 'Spiritual Awakening',
      description: `Personal Year ${py} (${numerology.currentTiming.personalYear.meaning.keyword}) aligns with the 12th House of the Subconscious. A profound period for inner work.`,
      sources: ['numerology', 'astrology'],
      questionRelevant: domain.label === 'Spiritual Path',
    });
  }

  // Foundation building
  if (py === 4 && astrology?.planets?.Saturn) {
    alignments.push({
      type: 'foundation',
      strength: 'moderate',
      title: 'Building Foundations',
      description: 'Personal Year 4 meets Saturn\'s disciplined energy. Focus on creating solid structures in your life.',
      sources: ['numerology', 'astrology'],
      questionRelevant: ['Career & Finances', 'Family & Home'].includes(domain.label),
    });
  }

  // Emotional intensity
  if (wicca?.moonPhase?.name === 'Full Moon' && wicca?.elementalBalance?.dominantElement === 'Water') {
    alignments.push({
      type: 'emotional',
      strength: 'strong',
      title: 'Emotional Tides',
      description: 'The Full Moon amplifies your dominant Water element. Intuition and emotions are at their peak — ideal for release rituals.',
      sources: ['wicca', 'astrology'],
      questionRelevant: ['Love & Relationships', 'Health & Wellness'].includes(domain.label),
    });
  }

  // New beginnings
  if (wicca?.moonPhase?.name === 'New Moon' && py === 1) {
    alignments.push({
      type: 'beginnings',
      strength: 'very-strong',
      title: 'Cosmic Fresh Start',
      description: 'The New Moon aligns with Personal Year 1. The universe is clearing the path for new beginnings — set powerful intentions now.',
      sources: ['wicca', 'numerology'],
      questionRelevant: ['Life Transitions', 'Career & Finances'].includes(domain.label),
    });
  }

  // Creative expression
  const lp = numerology.lifePath?.number;
  if (lp === 3 && palmistry?.mounts?.mountOfApollo?.fullness === 'prominent') {
    alignments.push({
      type: 'creativity',
      strength: 'moderate',
      title: 'Creative Expression',
      description: 'Your Life Path 3 creative energy is reinforced by a prominent Mount of Apollo. Artistic expression is your birthright.',
      sources: ['numerology', 'palmistry'],
      questionRelevant: domain.label === 'Creativity & Expression',
    });
  }

  // Elemental deficiencies
  if (wicca?.elementalBalance?.elements) {
    for (const [element, data] of Object.entries(wicca.elementalBalance.elements)) {
      if (data.status === 'lacking') {
        alignments.push({
          type: 'elemental',
          strength: 'moderate',
          title: `${capitalize(element)} Element Deficiency`,
          description: `Your chart shows a ${element} element deficiency. ${getElementRemedy(element)}`,
          sources: ['wicca', 'astrology'],
          questionRelevant: true, // Always relevant — affects all domains
        });
      }
    }
  }

  // Karmic debts
  if (numerology.karmicDebts && numerology.karmicDebts.length > 0) {
    alignments.push({
      type: 'karmic',
      strength: 'strong',
      title: 'Karmic Lessons Active',
      description: `Your chart carries karmic debt numbers (${numerology.karmicDebts.map(d => d.value).join(', ')}). ${getKarmicAlignmentAdvice(numerology.karmicDebts)}`,
      sources: ['numerology'],
      questionRelevant: true, // Always relevant
    });
  }

  // Sort alignments: question-relevant first, then by strength
  alignments.sort((a, b) => {
    if (a.questionRelevant && !b.questionRelevant) return -1;
    if (!a.questionRelevant && b.questionRelevant) return 1;
    const strengthOrder = { 'very-strong': 0, 'strong': 1, 'moderate': 2 };
    return (strengthOrder[a.strength] ?? 3) - (strengthOrder[b.strength] ?? 3);
  });

  return alignments;
}

function getElementRemedy(element) {
  const remedies = {
    fire: 'Add more Fire energy: wear red or gold, burn candles, exercise, eat spicy foods, carry carnelian.',
    earth: 'Add more Earth energy: spend time in nature, garden, wear green or brown, carry jade or moss agate.',
    air: 'Add more Air energy: practice deep breathing, burn incense, study new topics, carry clear quartz.',
    water: 'Add more Water energy: take baths, visit lakes/oceans, drink more water, carry moonstone or amethyst.',
  };
  return remedies[element] ?? 'Consider elemental balancing rituals.';
}

function getKarmicAlignmentAdvice(debts) {
  const advice = {
    13: 'Focus on discipline and hard work without cutting corners.',
    14: 'Practice moderation and use your freedom wisely.',
    16: 'Humble yourself and seek spiritual growth over ego.',
    19: 'Lead through service and empower others rather than controlling them.',
  };
  return debts.map(d => advice[d.value] ?? '').filter(Boolean).join(' ');
}

// ─── Question-Focused Guidance Generator ───────────────────────────────────

function generateDeepGuidance(numerology, astrology, wicca, alignments, questionAnalysis) {
  const guidance = [];
  const question = questionAnalysis.questionSummary;
  const domain = questionAnalysis.primary;
  const templates = GUIDANCE_TEMPLATES[getDomainKey(domain)] || GUIDANCE_TEMPLATES.general;

  // 1. Opening — direct response to the question
  guidance.push({
    area: 'Direct Answer to Your Question',
    advice: templates.opening(question || domain.label),
    priority: 'urgent',
    domain: domain.label,
  });

  // 2. Life Path — how their core nature relates to the question
  const lp = numerology.lifePath;
  if (lp) {
    guidance.push({
      area: `How Your Life Path ${lp.number} Answers This`,
      advice: templates.lifePath(lp.number, lp.meaning),
      priority: 'primary',
      domain: domain.label,
    });
  }

  // 3. Current timing — Personal Year focused on question
  const py = numerology.currentTiming?.personalYear;
  if (py) {
    guidance.push({
      area: `This Year's (${py.number}) Influence on Your Question`,
      advice: templates.personalYear(py.number, py.meaning.keyword),
      priority: 'primary',
      domain: domain.label,
    });
  }

  // 4. Moon phase — timing advice
  if (wicca?.moonPhase) {
    guidance.push({
      area: `Lunar Timing: ${wicca.moonPhase.name}`,
      advice: templates.lunarAdvice(wicca.moonPhase),
      priority: 'daily',
      domain: domain.label,
    });
  }

  // 5. Elemental advice — how their elemental balance affects the question
  if (wicca?.elementalBalance?.elements) {
    const elemAdvice = templates.elementalAdvice(wicca.elementalBalance.elements);
    if (elemAdvice) {
      guidance.push({
        area: 'Elemental Influence',
        advice: elemAdvice,
        priority: 'important',
        domain: domain.label,
      });
    }
  }

  // 6. Day correspondence — today's energy for their question
  if (wicca?.dayCorrespondence) {
    guidance.push({
      area: `Today's Energy (${wicca.dayCorrespondence.planet})`,
      advice: `Today is ruled by ${wicca.dayCorrespondence.planet}. ${wicca.dayCorrespondence.energy}. This energy supports your question about ${question || domain.label.toLowerCase()}. Wear ${wicca.dayCorrespondence.color.toLowerCase()} and work with ${(wicca.dayCorrespondence.crystals || []).slice(0, 2).join(', ')}.`,
      priority: 'daily',
      domain: domain.label,
    });
  }

  // 7. Life challenges — obstacles relevant to the question
  if (numerology.challenges) {
    const challengeEntries = Object.entries(numerology.challenges);
    if (challengeEntries.length > 0) {
      const topChallenge = challengeEntries[0][1];
      guidance.push({
        area: 'Challenge to Address',
        advice: `Regarding your question, this challenge is most relevant: ${topChallenge.description}. Awareness of this pattern helps you navigate toward the answer you seek.`,
        priority: 'important',
        domain: domain.label,
      });
    }
  }

  // 8. Sabbat awareness
  if (wicca?.sabbat && wicca.sabbat.daysAway <= 14) {
    guidance.push({
      area: `Seasonal Gateway: ${wicca.sabbat.name}`,
      advice: `${wicca.sabbat.name} is ${wicca.sabbat.daysAway === 0 ? 'today' : `${wicca.sabbat.daysAway} days away`}. ${wicca.sabbat.energy}. This seasonal energy creates a powerful backdrop for your question about ${question || domain.label.toLowerCase()}.`,
      priority: 'important',
      domain: domain.label,
    });
  }

  // 9. Closing affirmation
  guidance.push({
    area: 'Final Wisdom',
    advice: templates.closing(domain),
    priority: 'foundational',
    domain: domain.label,
  });

  return guidance;
}

function getDomainKey(domain) {
  const map = {
    'Career & Finances': 'career',
    'Love & Relationships': 'love',
    'Health & Wellness': 'health',
    'Spiritual Path': 'spiritual',
    'Family & Home': 'general',
    'Education & Learning': 'general',
    'Creativity & Expression': 'general',
    'Life Transitions': 'general',
  };
  return map[domain?.label] || 'general';
}

// ─── Question-Focused Timeline ──────────────────────────────────────────────

function generateQuestionTimeline(numerology, wicca, questionAnalysis) {
  const now = new Date();
  const predictions = [];
  const domain = questionAnalysis.primary;
  const question = questionAnalysis.questionSummary || domain.label;

  // Current month — tailored
  if (numerology.currentTiming?.personalMonth) {
    const pm = numerology.currentTiming.personalMonth;
    predictions.push({
      period: `${now.toLocaleString('default', { month: 'long' })} ${now.getFullYear()}`,
      theme: pm.meaning.keyword,
      detail: `Regarding your question about "${question}": Personal Month ${pm.number}. ${getPersonalMonthDescription(pm.number)} ${getDomainMonthGuidance(pm.number, domain)}`,
      domain: domain.label,
    });
  }

  // Next month — projected
  const nextMonth = new Date(now.getFullYear(), now.getMonth() + 1, 1);
  const nextPM = ((numerology.currentTiming?.personalMonth?.number ?? 1) % 9) + 1;
  predictions.push({
    period: `${nextMonth.toLocaleString('default', { month: 'long' })} ${nextMonth.getFullYear()}`,
    theme: 'Forward Movement',
    detail: `As your question about "${question}" evolves: moving toward Personal Month ${nextPM}. ${getPersonalMonthDescription(nextPM)}`,
    domain: domain.label,
  });

  // Moon phase — relevant timing
  if (wicca?.moonPhase) {
    const nextPhase = getNextMoonPhase(wicca.moonPhase.daysIntoCycle);
    predictions.push({
      period: nextPhase.expectedDate,
      theme: `Next ${nextPhase.name}`,
      detail: `A key timing for your question: the ${nextPhase.name}. ${nextPhase.description} This is when insights about "${question}" may crystallize.`,
      domain: domain.label,
    });
  }

  // Sabbat timing
  if (wicca?.sabbat && wicca.sabbat.daysAway <= 30) {
    predictions.push({
      period: wicca.sabbat.name,
      theme: `Seasonal Shift: ${wicca.sabbat.name}`,
      detail: `${wicca.sabbat.name} (${wicca.sabbat.daysAway === 0 ? 'today' : `${wicca.sabbat.daysAway} days away`}). ${wicca.sabbat.energy}. This marks a powerful moment for your inquiry about "${question}".`,
      domain: domain.label,
    });
  }

  return predictions;
}

function getDomainMonthGuidance(pmNumber, domain) {
  const careerMap = {
    1: 'Professional seeds planted now will grow.',
    2: 'Build career relationships patiently.',
    3: 'Your professional reputation grows through visibility.',
    4: 'Solid career foundations are being laid.',
    5: 'Career changes are on the horizon.',
    6: 'Nurture your professional network.',
    7: 'Strategic planning serves you now.',
    8: 'Career advancement is likely. Step up.',
    9: 'A professional chapter is completing.',
  };
  const loveMap = {
    1: 'New romantic energy enters your life.',
    2: 'Partnership deepens. Be patient with love.',
    3: 'Love finds you through social connection.',
    4: 'Stability in relationships is building.',
    5: 'Romantic changes and surprises.',
    6: 'Family and love take center stage.',
    7: 'Reflect on what you truly want in love.',
    8: 'Passion and commitment intensify.',
    9: 'Release old relationship patterns.',
  };
  if (domain.label === 'Career & Finances') return careerMap[pmNumber] || '';
  if (domain.label === 'Love & Relationships') return loveMap[pmNumber] || '';
  return '';
}

function getNextMoonPhase(currentDaysIntoCycle) {
  const lunarCycle = 29.53;
  const phases = [
    { name: 'New Moon', day: 0, description: 'Set intentions, start new projects, plant seeds.' },
    { name: 'First Quarter', day: 7.38, description: 'Take action, overcome obstacles, make decisions.' },
    { name: 'Full Moon', day: 14.76, description: 'Peak power, manifest, celebrate, release what no longer serves.' },
    { name: 'Last Quarter', day: 22.15, description: 'Release, forgive, let go, clear space for new growth.' },
  ];

  for (const phase of phases) {
    if (phase.day > currentDaysIntoCycle) {
      const daysUntil = Math.round(phase.day - currentDaysIntoCycle);
      const nextDate = new Date(Date.now() + daysUntil * 86400000);
      return {
        ...phase,
        daysUntil,
        expectedDate: nextDate.toLocaleDateString('en-US', { month: 'long', day: 'numeric' }),
      };
    }
  }

  const daysUntil = Math.round(lunarCycle - currentDaysIntoCycle);
  const nextDate = new Date(Date.now() + daysUntil * 86400000);
  return {
    ...phases[0],
    daysUntil,
    expectedDate: nextDate.toLocaleDateString('en-US', { month: 'long', day: 'numeric' }),
  };
}

function getPersonalMonthDescription(n) {
  const descriptions = {
    1: 'New opportunities and fresh starts. Take initiative.',
    2: 'Cooperate, be patient, nurture relationships.',
    3: 'Socialize, create, express yourself joyfully.',
    4: 'Work hard, organize, build solid foundations.',
    5: 'Embrace change, seek adventure, stay flexible.',
    6: 'Focus on home, family, and responsibility.',
    7: 'Rest, reflect, study, go inward for wisdom.',
    8: 'Pursue goals, manage finances, claim your power.',
    9: 'Complete cycles, give back, prepare for renewal.',
  };
  return descriptions[n] ?? 'A month of growth and discovery.';
}

// ─── Question-Focused Remedies ──────────────────────────────────────────────

function generateRemedies(wicca, alignments, questionAnalysis) {
  const remedies = [];

  // 1. Domain-specific remedy from question interpreter
  const questionRemedy = getQuestionRemedies(questionAnalysis);
  remedies.push(questionRemedy);

  // 2. Moon phase ritual
  if (wicca?.moonPhase?.name) {
    remedies.push({
      type: 'moon_ritual',
      title: `${wicca.moonPhase.name} Ritual for Your Question`,
      description: `${getMoonRitual(wicca.moonPhase.name)} As you perform this ritual, hold your question about "${questionAnalysis.questionSummary || questionAnalysis.primary.label}" in your mind.`,
    });
  }

  // 3. Day correspondence
  if (wicca?.dayCorrespondence) {
    remedies.push({
      type: 'daily_practice',
      title: `Today's Practice (${wicca.dayCorrespondence.planet})`,
      description: `Today is ruled by ${wicca.dayCorrespondence.planet}. ${wicca.dayCorrespondence.energy}. To support your inquiry, carry ${(wicca.dayCorrespondence.crystals || []).join(', ')} and wear ${wicca.dayCorrespondence.color.toLowerCase()}. ${getDayRitual(wicca.dayCorrespondence.planet)}`,
      correspondence: {
        color: wicca.dayCorrespondence.color,
        crystals: wicca.dayCorrespondence.crystals,
        planet: wicca.dayCorrespondence.planet,
      },
    });
  }

  // 4. Elemental balancing
  if (wicca?.elementalBalance?.elements) {
    for (const [element, data] of Object.entries(wicca.elementalBalance.elements)) {
      if (data.status === 'lacking') {
        remedies.push({
          type: 'elemental_balancing',
          title: `Balance Your ${capitalize(element)} Element for Clarity`,
          description: getElementRemedy(element),
          element,
        });
      }
    }
  }

  // 5. Sabbat-based
  if (wicca?.sabbat && wicca.sabbat.daysAway <= 14) {
    remedies.push({
      type: 'sabbat',
      title: `${wicca.sabbat.name} Ritual for Your Question`,
      description: `${wicca.sabbat.name} is ${wicca.sabbat.daysAway === 0 ? 'today' : `${wicca.sabbat.daysAway} days away`}. ${getSabbatRemedy(wicca.sabbat.name)} Use this seasonal gateway to gain clarity on your question.`,
    });
  }

  // 6. Alignment-based remedies (only strong/very-strong or question-relevant)
  for (const alignment of alignments) {
    if (alignment.type === 'elemental') continue;
    if (alignment.strength === 'very-strong' || alignment.strength === 'strong' || alignment.questionRelevant) {
      const remedy = getAlignmentRemedy(alignment);
      if (remedy) remedies.push(remedy);
    }
  }

  return remedies;
}

function getDayRitual(planet) {
  const map = {
    Sun: 'Spend time in sunlight and set your intentions with confidence.',
    Moon: 'Keep a dream journal tonight. Your subconscious holds answers.',
    Mars: 'Take bold action on one step related to your question.',
    Mercury: 'Write down your question and journal the answer that comes.',
    Jupiter: 'Expand your perspective. Read, learn, or discuss your question with a trusted friend.',
    Venus: 'Surround yourself with beauty. Your heart knows the answer.',
    Saturn: 'Discipline and structure around your question will yield results.',
  };
  return map[planet] || 'Meditate on your question with today\'s planetary energy.';
}

function getMoonRitual(phase) {
  const rituals = {
    'New Moon': 'Light a white candle. Write your intentions on a bay leaf, then burn it. Visualize your desires taking root.',
    'Waxing Crescent': 'Create a success map or vision board. Take one concrete step toward a goal each day this week.',
    'First Quarter': 'Perform a releasing ritual for any obstacles. Write down what blocks you and tear the paper.',
    'Waxing Gibbous': 'Refine your intentions with a gratitude ritual. Thank the universe for what\'s manifesting.',
    'Full Moon': 'Charge your crystals in the moonlight. Take a full moon bath with sea salt and lavender. Write what you wish to release and burn it.',
    'Waning Gibbous': 'Share your abundance. Donate, gift, or teach something to someone.',
    'Last Quarter': 'Perform a cord-cutting ritual. Write what holds you back, tie it with black thread, and burn it.',
    'Waning Crescent': 'Rest. Meditate. Dream journal. Take a ritual bath with mugwort for prophetic dreams.',
  };
  return rituals[phase] ?? 'Meditate under the night sky and listen to your inner voice.';
}

function getSabbatRemedy(sabbat) {
  const map = {
    'Samhain': 'Set up an ancestor altar with photos, candles, and offerings. Practice divination.',
    'Yule': 'Decorate with evergreens, light a Yule log, and set intentions for the returning sun.',
    'Imbolc': 'Clean and purify your space. Light candles in every room. Plant seeds for spring goals.',
    'Ostara': 'Decorate eggs, plant seeds, and perform a balancing ritual for your life.',
    'Beltane': 'Dance around a fire or candle. Make flower crowns. Celebrate passion and creativity.',
    'Litha': 'Collect solar-charged water. Perform sun salutations. Celebrate abundance with a feast.',
    'Lughnasadh': 'Bake bread from scratch. Give thanks for the first harvest. Donate to those in need.',
    'Mabon': 'Create a gratitude altar. Share a feast with loved ones. Offer thanks for abundance.',
  };
  return map[sabbat] ?? 'Honor the turning of the Wheel of the Year with a seasonal ritual.';
}

function getAlignmentRemedy(alignment) {
  const remedies = {
    career: {
      type: 'career_ritual',
      title: 'Career Advancement Ritual',
      description: 'Write your career goals on green paper. Anoint with cinnamon oil and place under a green candle. Burn the candle on a Thursday (Jupiter\'s day) during the waxing moon. Bury the remains near your front door.',
    },
    spiritual: {
      type: 'spiritual_practice',
      title: 'Deepening Spiritual Practice',
      description: 'Create a meditation routine of 11 minutes per day. Keep a dream journal by your bed. Work with amethyst and selenite.',
    },
    emotional: {
      type: 'emotional_healing',
      title: 'Emotional Release Ritual',
      description: 'Take a ritual bath with sea salt, rose petals, and blue chamomile. As the water drains, visualize your emotional burdens washing away.',
    },
    beginnings: {
      type: 'new_beginning',
      title: 'Cosmic Fresh Start Ceremony',
      description: 'At the next new moon, cleanse your space with sage. Write your intentions for the next year on parchment. Fold it toward you three times and keep it under your pillow.',
    },
  };
  const key = alignment.type;
  if (remedies[key]) {
    return { ...remedies[key], alignment };
  }
  return null;
}

// ─── Main Orchestration ─────────────────────────────────────────────────────

/**
 * Run the full Composite Esoteric Engine pipeline.
 *
 * The user's question drives the entire reading — all guidance,
 * predictions, and remedies are tailored to their specific inquiry.
 *
 * @param {Object} userInput
 * @param {string} userInput.birthDate      - ISO date string
 * @param {string} [userInput.birthTime]     - HH:mm
 * @param {string} [userInput.locationText]  - Place name, city, or zipcode
 * @param {string} [userInput.fullName]      - Full birth name
 * @param {string} [userInput.gender]        - male | female | non-binary | prefer-not-to-say
 * @param {string} [userInput.question]      - The user's life question
 * @param {Object} [userInput.palmistryAnswers] - Palmistry data
 * @returns {Object} Unified reading with question-focused analysis, guidance, remedies
 */
export async function runFullReading(userInput) {
  const {
    birthDate: birthDateStr,
    birthTime,
    locationText,
    fullName,
    gender,
    question,
    palmistryAnswers = {},
  } = userInput;

  // Parse dates
  const birthDate = new Date(birthDateStr);
  const currentDate = new Date();

  // Geocode location text if provided
  let latitude = null;
  let longitude = null;
  let resolvedLocation = null;

  if (locationText && typeof locationText === 'string' && locationText.trim().length >= 2) {
    const coords = await geocode(locationText);
    latitude = coords.latitude;
    longitude = coords.longitude;
    resolvedLocation = coords.displayName;
  }

  // Step 1: Interpret the user's question — this shapes everything
  const questionAnalysis = interpretQuestion(question);
  const domain = questionAnalysis.primary;

  // Step 2: Math Layer — run independent engines in parallel
  const [numerology, astrology, palmistry] = await Promise.all([
    analyzeNumerology({ birthDate, fullName, currentDate }),
    analyzeAstrology({ birthDate, latitude, longitude, currentDate }),
    analyzePalmistry(palmistryAnswers),
  ]);

  // Step 3: Environmental Layer
  const wicca = analyzeWicca({ planets: astrology.planets, currentDate });

  // Step 4: Synthesis — cross-reference, weighted by question relevance
  const alignments = synthesizeAlignments(numerology, astrology, wicca, palmistry, questionAnalysis);

  // Step 5: Question-focused guidance
  const guidance = generateDeepGuidance(numerology, astrology, wicca, alignments, questionAnalysis);

  // Step 6: Question-focused timeline
  const timeline = generateQuestionTimeline(numerology, wicca, questionAnalysis);

  // Step 7: Question-focused remedies
  const remedies = generateRemedies(wicca, alignments, questionAnalysis);

  // Step 8: Assembly
  const reading = {
    metadata: {
      readingDate: currentDate.toISOString(),
      question: question ?? null,
      questionFocus: questionAnalysis.focus,
      questionDomains: questionAnalysis.activeDomains.map(d => d.label),
      birthDate: birthDateStr,
      birthTime: birthTime ?? null,
      location: latitude && longitude ? { latitude, longitude, displayName: resolvedLocation, originalQuery: locationText } : null,
      fullName: fullName ?? null,
      gender: gender ?? null,
    },
    analysis: {
      numerology,
      astrology,
      wicca,
      palmistry,
    },
    prediction: {
      timeline,
      overridingTheme: alignments.find(a => a.questionRelevant && (a.strength === 'very-strong' || a.strength === 'strong'))?.title
        ?? alignments.find(a => a.strength === 'very-strong')?.title
        ?? `${domain.icon} ${domain.label} Focus`,
    },
    guidance,
    remedies,
    alignments,
  };

  return reading;
}

export default { runFullReading };
