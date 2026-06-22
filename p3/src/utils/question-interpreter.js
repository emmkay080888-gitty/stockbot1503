/**
 * question-interpreter.js
 *
 * Analyzes the user's question to determine the domain, intent,
 * and relevant esoteric focus areas. The result drives how the
 * EsotericEngine tailors predictions, guidance, and remedies.
 *
 * Instead of generic output, every section of the reading
 * directly addresses the user's specific question.
 */

// ─── Question Domains ───────────────────────────────────────────────────────

const DOMAINS = {
  career: {
    keywords: ['career', 'job', 'work', 'business', 'profession', 'money', 'finance', 'wealth', 'success', 'promotion', 'boss', 'coworker', 'interview', 'startup', 'entrepreneur', 'income', 'salary', 'invest', 'retire'],
    houses: [2, 6, 10],
    numbers: [8, 4],
    elements: ['Earth'],
    planets: ['Saturn', 'Jupiter', 'Mars'],
    responseStyle: 'practical',
    label: 'Career & Finances',
    icon: '💼',
  },
  love: {
    keywords: ['love', 'relationship', 'partner', 'marriage', 'soulmate', 'romance', 'dating', 'heart', 'crush', 'ex', 'breakup', 'divorce', 'commitment', 'intimacy', 'single', 'twin flame', 'husband', 'wife', 'boyfriend', 'girlfriend'],
    houses: [5, 7, 8],
    numbers: [2, 6],
    elements: ['Water'],
    planets: ['Venus', 'Moon'],
    responseStyle: 'emotional',
    label: 'Love & Relationships',
    icon: '❤️',
  },
  health: {
    keywords: ['health', 'body', 'illness', 'pain', 'energy', 'exercise', 'diet', 'sleep', 'anxiety', 'stress', 'heal', 'recovery', 'sick', 'doctor', 'medical', 'fitness', 'wellness', 'mental', 'depression'],
    houses: [1, 6, 12],
    numbers: [4, 7],
    elements: ['Earth', 'Water'],
    planets: ['Moon', 'Mercury', 'Saturn'],
    responseStyle: 'nurturing',
    label: 'Health & Wellness',
    icon: '💚',
  },
  spiritual: {
    keywords: ['spiritual', 'soul', 'purpose', 'meaning', 'awakening', 'meditation', 'enlightenment', 'faith', 'belief', 'god', 'universe', 'karma', 'destiny', 'fate', 'psychic', 'intuition', 'dream', 'past life'],
    houses: [9, 12],
    numbers: [7, 9, 11, 22],
    elements: ['Water', 'Spirit'],
    planets: ['Neptune', 'Jupiter', 'Moon'],
    responseStyle: 'mystical',
    label: 'Spiritual Path',
    icon: '✨',
  },
  family: {
    keywords: ['family', 'parent', 'child', 'mother', 'father', 'sibling', 'home', 'house', 'move', 'pregnancy', 'baby', 'ancestor', 'relative', 'marriage', 'wedding'],
    houses: [4, 5, 10],
    numbers: [6, 2],
    elements: ['Earth', 'Water'],
    planets: ['Moon', 'Saturn', 'Venus'],
    responseStyle: 'warm',
    label: 'Family & Home',
    icon: '🏠',
  },
  education: {
    keywords: ['study', 'learn', 'school', 'university', 'college', 'exam', 'course', 'degree', 'teacher', 'student', 'skill', 'knowledge', 'read', 'write', 'research', 'phd', 'master'],
    houses: [3, 9],
    numbers: [5, 7, 3],
    elements: ['Air'],
    planets: ['Mercury', 'Jupiter'],
    responseStyle: 'analytical',
    label: 'Education & Learning',
    icon: '📚',
  },
  creativity: {
    keywords: ['creative', 'art', 'write', 'music', 'paint', 'dance', 'perform', 'create', 'project', 'hobby', 'passion', 'talent', 'gift', 'invent', 'design', 'build'],
    houses: [5, 3, 10],
    numbers: [3, 1, 5],
    elements: ['Fire', 'Air'],
    planets: ['Sun', 'Venus', 'Mercury'],
    responseStyle: 'inspiring',
    label: 'Creativity & Expression',
    icon: '🎨',
  },
  transition: {
    keywords: ['change', 'move', 'travel', 'relocate', 'new beginning', 'start over', 'fresh start', 'transition', 'uncertain', 'lost', 'direction', 'next step', 'path', 'choice', 'decision', 'future'],
    houses: [1, 3, 9],
    numbers: [1, 5],
    elements: ['Fire', 'Air'],
    planets: ['Uranus', 'Jupiter', 'Mars'],
    responseStyle: 'encouraging',
    label: 'Life Transitions',
    icon: '🦋',
  },
  general: {
    keywords: [],
    houses: [1],
    numbers: [],
    elements: [],
    planets: [],
    responseStyle: 'balanced',
    label: 'General Guidance',
    icon: '🔮',
  },
};

// ─── Question Analysis ──────────────────────────────────────────────────────

/**
 * Analyze the user's question to determine which domain(s) it belongs to.
 *
 * @param {string} question - The user's free-text question
 * @returns {Object} { domain, domains (scored), focus, keyPhrases }
 */
export function interpretQuestion(question) {
  if (!question || typeof question !== 'string' || question.trim().length === 0) {
    return {
      primary: DOMAINS.general,
      activeDomains: [DOMAINS.general],
      allScores: [{ domain: DOMAINS.general, score: 1 }],
      focus: 'General Guidance',
      keyPhrases: [],
      questionSummary: null,
    };
  }

  const lower = question.toLowerCase().trim();
  const words = lower.split(/\s+/);
  const phrases = extractPhrases(lower);

  // Score each domain
  const scores = Object.entries(DOMAINS).map(([key, domain]) => {
    let score = 0;

    // Score by keyword matches
    for (const keyword of domain.keywords) {
      if (lower.includes(keyword)) {
        // Weight by how central the keyword is (longer = more specific = higher weight)
        const weight = keyword.length > 6 ? 3 : keyword.length > 4 ? 2 : 1;
        score += weight;
      }
    }

    // Bonus for phrase matches
    for (const phrase of phrases) {
      if (domain.keywords.some(k => phrase.includes(k))) {
        score += 2;
      }
    }

    return { domain, score, key };
  });

  // Sort by score descending
  scores.sort((a, b) => b.score - a.score);

  // If no domains scored, use general
  const primary = scores[0].score > 0 ? scores[0].domain : DOMAINS.general;

  // Get the top domains (score > 0)
  const activeDomains = scores.filter(s => s.score > 0).map(s => s.domain);

  return {
    primary,
    activeDomains: activeDomains.length > 0 ? activeDomains : [DOMAINS.general],
    allScores: scores,
    focus: primary.label,
    keyPhrases: phrases,
    questionSummary: summarizeQuestion(question),
  };
}

/**
 * Extract meaningful 2-3 word phrases from the question.
 */
function extractPhrases(text) {
  const words = text.split(/\s+/).filter(w => w.length > 2);
  const phrases = [];

  // 2-word phrases
  for (let i = 0; i < words.length - 1; i++) {
    phrases.push(`${words[i]} ${words[i + 1]}`);
  }

  // 3-word phrases
  for (let i = 0; i < words.length - 2; i++) {
    phrases.push(`${words[i]} ${words[i + 1]} ${words[i + 2]}`);
  }

  return phrases;
}

/**
 * Create a concise summary of what the user is asking about.
 */
function summarizeQuestion(question) {
  const lower = question.toLowerCase();
  const stopWords = ['a', 'an', 'the', 'is', 'am', 'are', 'was', 'were', 'i', 'me', 'my', 'we', 'you', 'he', 'she', 'it', 'they', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'have', 'has', 'had', 'what', 'when', 'where', 'how', 'can'];
  const words = lower.split(/\s+/).filter(w => w.length > 2 && !stopWords.includes(w));
  return words.slice(0, 6).join(' ') || question.slice(0, 80);
}

// ─── Domain-Specific Guidance Templates ────────────────────────────────────

const GUIDANCE_TEMPLATES = {
  career: {
    opening: (question) => `Your question about "${question}" speaks directly to your professional path. The celestial bodies align to give you clear direction on this.`,
    lifePath: (lp, meaning) => `As a Life Path ${lp} (${meaning.keyword}), your career journey is naturally one of ${meaning.keyword.toLowerCase()}. ${meaning.positive} — these are strengths to lead with professionally. Be mindful of: ${meaning.negative}.`,
    personalYear: (py, desc) => `This Personal Year ${py} energy — "${desc}" — is directly relevant to your career question. ${getPersonalYearCareerGuidance(py)}`,
    lunarAdvice: (phase) => `In terms of timing: the ${phase.name} supports ${getCareerMoonAdvice(phase.name)}.`,
    elementalAdvice: (elements) => getCareerElementAdvice(elements),
    closing: (domain) => getCareerClosing(domain),
  },
  love: {
    opening: (question) => `"${question}" — the heart's deepest questions are written in the stars. Let's explore what the cosmos reveals about your love life.`,
    lifePath: (lp, meaning) => `With Life Path ${lp} (${meaning.keyword}), your approach to love is shaped by ${meaning.keyword.toLowerCase()}. ${meaning.positive} enriches your relationships. Be conscious of: ${meaning.negative}.`,
    personalYear: (py, desc) => `This Personal Year ${py} — "${desc}" — colors your love life significantly. ${getPersonalYearLoveGuidance(py)}`,
    lunarAdvice: (phase) => `The ${phase.name} ${phase.symbol} amplifies romantic energy. ${getLoveMoonAdvice(phase.name)}`,
    elementalAdvice: (elements) => getLoveElementAdvice(elements),
    closing: (domain) => getLoveClosing(domain),
  },
  health: {
    opening: (question) => `Your concern about "${question}" reflects deep self-awareness. The esoteric wisdom reveals how to restore balance and vitality.`,
    lifePath: (lp, meaning) => `Life Path ${lp} (${meaning.keyword}) influences your relationship with your body and well-being. ${meaning.positive} supports your health journey. Watch for: ${meaning.negative}.`,
    personalYear: (py, desc) => `Personal Year ${py} — "${desc}" — affects your health. ${getPersonalYearHealthGuidance(py)}`,
    lunarAdvice: (phase) => `The ${phase.name} is ${getHealthMoonAdvice(phase.name)} for healing work.`,
    elementalAdvice: (elements) => getHealthElementAdvice(elements),
    closing: (domain) => getHealthClosing(domain),
  },
  spiritual: {
    opening: (question) => `"${question}" — this is a soul-level inquiry. The mystical branches have much to reveal about your spiritual journey.`,
    lifePath: (lp, meaning) => `Your Life Path ${lp} (${meaning.keyword}) is the soul contract you signed for this lifetime. ${meaning.positive} guides your spiritual evolution. The shadow: ${meaning.negative}.`,
    personalYear: (py, desc) => `Personal Year ${py} — "${desc}" — is a spiritual checkpoint. ${getPersonalYearSpiritualGuidance(py)}`,
    lunarAdvice: (phase) => `The ${phase.name} ${phase.symbol} opens a portal for ${getSpiritualMoonAdvice(phase.name)}.`,
    elementalAdvice: (elements) => getSpiritualElementAdvice(elements),
    closing: (domain) => getSpiritualClosing(domain),
  },
  general: {
    opening: (question) => question ? `Reflecting on "${question}" — the cosmos weaves its wisdom through every branch of esoteric knowledge to guide you.` : `A general reading unfolds before you. The celestial patterns reveal their wisdom across all areas of life.`,
    lifePath: (lp, meaning) => `Your Life Path ${lp} (${meaning.keyword}) is the central theme of your journey. ${meaning.positive}. Your edge of growth: ${meaning.negative}.`,
    personalYear: (py, desc) => `You are in a Personal Year ${py} — ${desc}. This sets the tone for all areas of your life.`,
    lunarAdvice: (phase) => `The ${phase.name} ${phase.symbol} influences your daily energy. ${phase.description}.`,
    elementalAdvice: (elements) => getGeneralElementAdvice(elements),
    closing: () => 'Trust the journey. The universe reveals what you need, when you need it.',
  },
};

// ─── Domain-Specific Sub-Guidance Functions ─────────────────────────────────

function getPersonalYearCareerGuidance(py) {
  const map = {
    1: 'A year to launch that career move you\'ve been contemplating. Plant professional seeds.',
    2: 'Focus on workplace relationships and collaboration. Patience pays off professionally.',
    3: 'Your creative talents are your career currency this year. Communicate your ideas boldly.',
    4: 'Build solid professional foundations. Discipline now creates career security later.',
    5: 'Career changes and new opportunities are敲门. Say yes to the unexpected.',
    6: 'Your career may involve mentoring or service. Balance work with personal responsibilities.',
    7: 'A year for professional reflection. Study, strategize, and plan your next big move.',
    8: 'Peak career year. Leadership, financial growth, and professional power are yours to claim.',
    9: 'Professional completion and transition. Tie up loose ends and prepare for renewal.',
  };
  return map[py] || 'Your career path is evolving. Trust the process.';
}

function getPersonalYearLoveGuidance(py) {
  const map = {
    1: 'Love takes initiative this year. If single, you may meet someone new and exciting.',
    2: 'Deep partnership energy. Existing relationships deepen; patience attracts love.',
    3: 'Love finds you through social circles. Have fun, flirt, and keep things light.',
    4: 'A year to build solid relationship foundations. Commitment and stability in love.',
    5: 'Love brings change and adventure. An unexpected romance or relationship evolution.',
    6: 'Family and home take priority in love. Nurturing and responsibility deepen bonds.',
    7: 'A spiritual approach to love. You may need solitude to understand what you truly desire.',
    8: 'Power dynamics in relationships come up. Balance personal ambition with partnership.',
    9: 'Release old relationship patterns. Complete karmic cycles in love to make space for new.',
  };
  return map[py] || 'Your heart\'s path is guided by the stars.';
}

function getPersonalYearHealthGuidance(py) {
  const map = {
    1: 'A year to start new health routines. Your body responds to fresh beginnings.',
    2: 'Focus on emotional health. Stress reduction and gentle movement support you.',
    3: 'Creative expression heals. Dance, art, or singing boosts your vitality.',
    4: 'Discipline in health routines pays off. Structure around diet and exercise.',
    5: 'Try new approaches to wellness. Your body craves variety and adventure.',
    6: 'Nurturing others? Don\'t neglect your own health. Balance care with self-care.',
    7: 'Rest and restoration are vital. Your health improves with stillness and introspection.',
    8: 'Listen to your body\'s power. Strength training and discipline support vitality.',
    9: 'Release health patterns that no longer serve you. Let go of stress and tension.',
  };
  return map[py] || 'Your well-being evolves with each season.';
}

function getPersonalYearSpiritualGuidance(py) {
  const map = {
    1: 'A spiritual rebirth. New beliefs, practices, and spiritual connections emerge.',
    2: 'Your intuition sharpens. Pay attention to signs, synchronicities, and dreams.',
    3: 'Creative spirituality. Express your faith through art, music, or writing.',
    4: 'Build a consistent spiritual practice. Discipline deepens your connection.',
    5: 'Spiritual exploration and expansion. Study different traditions and philosophies.',
    6: 'Sacred service. Your spirituality expresses through helping and healing others.',
    7: 'Deep spiritual year. Meditation, study, and inner work yield profound insights.',
    8: 'Manifest through faith. Your spiritual practice can create tangible results.',
    9: 'Spiritual completion. Release old belief systems and transcend limitations.',
  };
  return map[py] || 'Your spirit evolves on its own timeline.';
}

function getCareerMoonAdvice(phase) {
  const map = {
    'New Moon': 'setting career intentions and visualizing professional goals.',
    'Waxing Crescent': 'taking the first concrete steps toward your career aspirations.',
    'First Quarter': 'overcoming professional obstacles with decisive action.',
    'Waxing Gibbous': 'refining your career strategy and adjusting your approach.',
    'Full Moon': 'celebrating career achievements and releasing what no longer serves.',
    'Waning Gibbous': 'sharing professional wisdom and mentoring others.',
    'Last Quarter': 'letting go of career paths that have reached their conclusion.',
    'Waning Crescent': 'resting and preparing for the next professional cycle.',
  };
  return map[phase] || 'aligning your career moves with the lunar rhythm.';
}

function getLoveMoonAdvice(phase) {
  const map = {
    'New Moon': 'perfect for setting romantic intentions. Write down what you desire in a partner.',
    'Waxing Crescent': 'take small romantic risks. Send that message. Flirt. Open your heart.',
    'First Quarter': 'address relationship issues directly. Honest conversations heal.',
    'Waxing Gibbous': 'nurture your relationship. Small gestures of love compound beautifully.',
    'Full Moon': 'romantic culmination. A powerful night for love declarations or intimacy.',
    'Waning Gibbous': 'gratitude in love. Appreciate what your partner brings to your life.',
    'Last Quarter': 'release old relationship wounds. Forgive yourself and others.',
    'Waning Crescent': 'rest in solitude. Love starts with loving yourself first.',
  };
  return map[phase] || 'letting your heart be guided by the moon.';
}

function getHealthMoonAdvice(phase) {
  const map = {
    'New Moon': 'the best time to start a new health regimen or detox.',
    'Waxing Crescent': 'build momentum in your wellness routine. Consistency is key.',
    'First Quarter': 'push through health challenges. Your body is stronger than you think.',
    'Waxing Gibbous': 'fine-tune your diet and exercise. Small adjustments yield big results.',
    'Full Moon': 'a powerful time for healing rituals and releasing emotional blockages.',
    'Waning Gibbous': 'share your health journey. Teaching others reinforces your own wellness.',
    'Last Quarter': 'release physical and emotional toxins. Great time for a cleanse.',
    'Waning Crescent': 'rest deeply. Your body heals best when you surrender to stillness.',
  };
  return map[phase] || 'aligned with your body\'s natural healing rhythms.';
}

function getSpiritualMoonAdvice(phase) {
  const map = {
    'New Moon': 'setting soul intentions and planting spiritual seeds.',
    'Waxing Crescent': 'taking inspired action on your spiritual insights.',
    'First Quarter': 'facing spiritual challenges that strengthen your faith.',
    'Waxing Gibbous': 'deepening your practice through devotion and discipline.',
    'Full Moon': 'psychic peak. Meditation, divination, and dreamwork are amplified.',
    'Waning Gibbous': 'sharing spiritual wisdom. Teaching deepens your own understanding.',
    'Last Quarter': 'releasing spiritual attachments and old belief patterns.',
    'Waning Crescent': 'surrendering to the divine. Rest in cosmic trust.',
  };
  return map[phase] || 'deepening your connection to the divine.';
}

function getCareerElementAdvice(elements) {
  const lacking = Object.entries(elements).filter(([, v]) => v.status === 'lacking');
  if (lacking.length === 0) return '';
  return `Your chart shows a lack of ${lacking.map(([e]) => e).join(' and ')} element energy. For career, this means ${getCareerElementLackingAdvice(lacking[0][0])}`;
}

function getCareerElementLackingAdvice(element) {
  const map = {
    fire: 'you may need more assertiveness. Take bold risks. Speak up in meetings.',
    earth: 'ground your career goals with practical plans. Build systems and routines.',
    air: 'network more. Share your ideas. Your professional voice needs to be heard.',
    water: 'trust your intuition about people and situations. Emotional intelligence is your career edge.',
  };
  return map[element] || 'bring more balance to your professional life.';
}

function getLoveElementAdvice(elements) {
  const lacking = Object.entries(elements).filter(([, v]) => v.status === 'lacking');
  if (lacking.length === 0) return '';
  return `Your elemental imbalance affects your love life. ${getLoveElementLackingAdvice(lacking[0][0])}`;
}

function getLoveElementLackingAdvice(element) {
  const map = {
    fire: 'bring more passion and spontaneity into your relationships.',
    earth: 'create stability and security in love. Be reliable and present.',
    air: 'communicate your feelings openly. Intellectual connection deepens intimacy.',
    water: 'allow yourself to be vulnerable. Emotional depth creates true intimacy.',
  };
  return map[element] || 'bring more balance to your heart.';
}

function getHealthElementAdvice(elements) {
  const lacking = Object.entries(elements).filter(([, v]) => v.status === 'lacking');
  if (lacking.length === 0) return '';
  return `Your ${lacking[0][0]} element deficiency affects your vitality. ${getHealthElementLackingAdvice(lacking[0][0])}`;
}

function getHealthElementLackingAdvice(element) {
  const map = {
    fire: 'boost your metabolism with movement and spicy foods. Ignite your vitality.',
    earth: 'ground your health routine. Eat whole foods. Walk in nature daily.',
    air: 'breathe deeply. Practice pranayama or yoga. Fresh air is your medicine.',
    water: 'hydrate deeply. Take baths. Your body needs emotional release through water.',
  };
  return map[element] || 'listen to what your body is telling you.';
}

function getSpiritualElementAdvice(elements) {
  const lacking = Object.entries(elements).filter(([, v]) => v.status === 'lacking');
  if (lacking.length === 0) return '';
  return `Your spiritual growth is supported by balancing your elements. ${getSpiritualElementLackingAdvice(lacking[0][0])}`;
}

function getSpiritualElementLackingAdvice(element) {
  const map = {
    fire: 'ignite your spiritual practice with passion. Candle meditation. Sun salutations.',
    earth: 'ground your spirituality. Practice in nature. Use crystals and stones.',
    air: 'study sacred texts. Practice breathwork. Your spiritual intellect expands.',
    water: 'deepen your intuition through dreams, moon rituals, and emotional release.',
  };
  return map[element] || 'your spirit seeks balance. Listen.';
}

function getGeneralElementAdvice(elements) {
  const lacking = Object.entries(elements).filter(([, v]) => v.status === 'lacking');
  if (lacking.length === 0) return 'Your elements are balanced — a harmonious foundation for growth.';
  return `Your chart shows an imbalance in the ${lacking.map(([e]) => e).join(' and ')} elements. ${lacking.map(([e]) => `Bring more ${e} energy: ${getElementRemedyFast(e)}`).join(' ')}`;
}

function getElementRemedyFast(element) {
  const map = {
    fire: 'wear red, light candles, exercise.',
    earth: 'spend time in nature, garden, use green stones.',
    air: 'burn incense, practice deep breathing, study.',
    water: 'take baths, drink more water, use moonstone.',
  };
  return map[element] || 'bring balance.';
}

function getCareerClosing(domain) {
  return `Remember: ${domain.icon} Your career is not just about livelihood — it's about expressing your soul's purpose through your work. The stars support your professional journey. ${getRandomAffirmation('career')}`;
}

function getLoveClosing(domain) {
  return `${domain.icon} Love is the highest vibration. The cosmos supports your heart's desires. Trust that the right love flows to you at the right time. ${getRandomAffirmation('love')}`;
}

function getHealthClosing(domain) {
  return `${domain.icon} Your body is your temple. The esoteric wisdom shows that true health is harmony between body, mind, and spirit. Heal deeply. ${getRandomAffirmation('health')}`;
}

function getSpiritualClosing(domain) {
  return `${domain.icon} You are a spiritual being having a human experience. The cosmos whispers — are you listening? Your soul's evolution is the ultimate journey. ${getRandomAffirmation('spiritual')}`;
}

const AFFIRMATIONS = {
  career: ['You are exactly where you need to be on your professional path.', 'Your unique gifts are needed in this world.', 'Abundance flows to you through your authentic work.'],
  love: ['You are worthy of deep, authentic love.', 'Love flows to and through you freely.', 'Your heart knows the way — trust it.'],
  health: ['Your body has an incredible capacity to heal.', 'Every breath is a chance to renew your vitality.', 'Wellness is your natural state of being.'],
  spiritual: ['The universe is guiding you, always.', 'You are connected to something greater than yourself.', 'Your spirit chose this journey for a reason.'],
  general: ['Trust the timing of your life.', 'The stars are on your side.', 'You have everything you need within you.'],
};

function getRandomAffirmation(domain) {
  const affirmations = AFFIRMATIONS[domain] || AFFIRMATIONS.general;
  return affirmations[Math.floor(Math.random() * affirmations.length)];
}

// ─── Question-Specific Remedy Enhancement ───────────────────────────────────

const REMEDY_ENHANCEMENTS = {
  career: {
    prefix: 'For your career question',
    rituals: [
      'Write your career goal on a bay leaf and burn it under a waxing Jupiter candle.',
      'Create a professional vision board during the new moon. Include images of your ideal work life.',
      'Carry tiger\'s eye in your pocket during interviews and important meetings.',
      'Anoint your computer or workspace with cinnamon oil for professional success.',
    ],
  },
  love: {
    prefix: 'For your heart\'s question',
    rituals: [
      'On a Friday (Venus\'s day), light a pink candle and write what you desire in a partner. Fold the paper toward you and keep it under your pillow.',
      'Wear rose quartz over your heart chakra to attract loving energy.',
      'Take a rose petal bath during the full moon to open your heart.',
      'Write a letter to your future partner (or your current partner) and keep it in a special box.',
    ],
  },
  health: {
    prefix: 'For your health concern',
    rituals: [
      'Perform a full moon water charging ritual. Drink the charged water for vital energy.',
      'Create a healing sachet with amethyst, lavender, and chamomile. Keep it under your pillow.',
      'Practice grounding meditation: visualize roots from your feet into the earth, drawing up healing energy.',
      'Take a salt bath on the waning moon to release physical and emotional toxins.',
    ],
  },
  spiritual: {
    prefix: 'For your spiritual inquiry',
    rituals: [
      'Keep a dream journal by your bed. Set the intention before sleep to receive guidance in your dreams.',
      'Create a sacred space or altar dedicated to your spiritual practice.',
      'Meditate with amethyst on your third eye during the new moon.',
      'Practice automatic writing: ask your question and write whatever flows without judgment.',
    ],
  },
  general: {
    prefix: 'For your question',
    rituals: [
      'Light a white candle and meditate on your question for 11 minutes.',
      'Write your question on paper, fold it, and keep it in a special place. Return to it after one lunar cycle.',
      'Take a mindful walk in nature. Notice signs and synchronicities that answer your question.',
      'Perform a simple tarot or oracle card pull with the intention of gaining clarity.',
    ],
  },
};

/**
 * Get remedies tailored to the user's question domain.
 */
export function getQuestionRemedies(questionAnalysis) {
  const domain = questionAnalysis.primary;
  const domainKey = Object.entries(DOMAINS).find(([, d]) => d.label === domain.label)?.[0] || 'general';
  const enhancement = REMEDY_ENHANCEMENTS[domainKey] || REMEDY_ENHANCEMENTS.general;

  return {
    type: 'question_specific',
    title: `${domain.icon} Remedies for Your Question`,
    description: `${enhancement.prefix}, focus on these practices:`,
    rituals: enhancement.rituals,
  };
}

export { DOMAINS, GUIDANCE_TEMPLATES };

export default {
  interpretQuestion,
  DOMAINS,
  GUIDANCE_TEMPLATES,
  getQuestionRemedies,
};
