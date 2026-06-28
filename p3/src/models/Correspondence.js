/**
 * Correspondence Model — MongoDB Schema Shell
 *
 * Represents the "Universal Correspondence Table" that links
 * different esoteric branches together via common tags.
 *
 * Each document stores lore for a single element/sign/number
 * and its associations across all branches.
 *
 * Schema design:
 * {
 *   element: "Fire",
 *   tags: ["fire", "passion", "energy", "aries", "leo", "sagittarius"],
 *   astrology_associations: ["Aries", "Leo", "Sagittarius", "Mars", "Sun"],
 *   numerology_associations: [1, 9],
 *   wicca_witchcraft_lore: {
 *     herbs: ["Cinnamon", "Ginger", "Cayenne"],
 *     crystals: ["Carnelian", "Clear Quartz", "Tiger's Eye"],
 *     rituals: "Candle magic, banishing stagnation, amplifying personal drive",
 *     colors: ["Red", "Gold", "Orange"],
 *     incense: ["Frankincense", "Dragon's Blood"],
 *   },
 *   palmistry_indicators: "Strong, deeply etched Life and Heart lines, prominent Mount of Mars",
 *   oracle_correspondences: {
 *     tarot: ["The Sun", "The Tower (reversed)", "Wands suit"],
 *     runes: ["Fehu", "Sowilo", "Kenaz"],
 *   },
 *   traditional_remedies: [
 *     "Burn red candles on Tuesdays to amplify drive",
 *     "Carry carnelian for courage and motivation",
 *     "Take action-oriented risks during the waxing moon",
 *   ],
 * }
 *
 * Usage with MongoDB:
 *   import Correspondence from './models/Correspondence.js';
 *   const fireLore = await Correspondence.findOne({ tags: 'fire' });
 *   const remedies = fireLore.wicca_witchcraft_lore;
 *
 * To integrate: npm install mongoose, then uncomment the schema below.
 */

/*
import mongoose from 'mongoose';

const correspondenceSchema = new mongoose.Schema({
  element: {
    type: String,
    enum: ['Fire', 'Earth', 'Air', 'Water', 'Spirit'],
    required: true,
  },
  tags: {
    type: [String],
    index: true,
    required: true,
  },
  astrology_associations: [String],
  numerology_associations: [Number],
  wicca_witchcraft_lore: {
    herbs: [String],
    crystals: [String],
    rituals: String,
    colors: [String],
    incense: [String],
  },
  palmistry_indicators: String,
  oracle_correspondences: {
    tarot: [String],
    runes: [String],
    ogham: [String],
  },
  traditional_remedies: [String],
}, {
  timestamps: true,
});

// Index for fast tag-based lookups
correspondenceSchema.index({ tags: 1 });
correspondenceSchema.index({ element: 1 });

const Correspondence = mongoose.model('Correspondence', correspondenceSchema);

export default Correspondence;
*/

/**
 * In-memory fallback for the Universal Correspondence Table.
 * Used until MongoDB is connected.
 */

const CORRESPONDENCE_TABLE = {
  fire: {
    element: 'Fire',
    tags: ['fire', 'passion', 'energy', 'aries', 'leo', 'sagittarius'],
    astrologyAssociations: ['Aries', 'Leo', 'Sagittarius', 'Mars', 'Sun'],
    numerologyAssociations: [1, 9],
    wiccaLore: {
      herbs: ['Cinnamon', 'Ginger', 'Cayenne', 'Rosemary', 'Basil'],
      crystals: ['Carnelian', 'Clear Quartz', 'Tiger\'s Eye', 'Ruby', 'Fire Agate'],
      rituals: 'Candle magic, bonfire rituals, sun salutations, banishing stagnation',
      colors: ['Red', 'Gold', 'Orange', 'Crimson'],
      incense: ['Frankincense', 'Dragon\'s Blood', 'Sandalwood'],
    },
    palmistryIndicators: 'Strong, deeply etched Life and Heart lines, prominent Mount of Mars, warm skin tone',
    oracleCorrespondences: {
      tarot: ['The Sun', 'The Tower (reversed)', 'Wands suit', 'Strength'],
      runes: ['Fehu', 'Sowilo', 'Kenaz', 'Dagaz'],
    },
    traditionalRemedies: [
      'Burn red candles on Tuesdays to amplify personal drive',
      'Carry carnelian in your pocket for courage and motivation',
      'Perform a sun salutation at dawn to align with solar energy',
      'Spend time near a fireplace or bonfire to reconnect with your inner fire',
      'Eat warming foods: ginger tea, cayenne, garlic, and spicy dishes',
    ],
  },
  earth: {
    element: 'Earth',
    tags: ['earth', 'stability', 'grounding', 'taurus', 'virgo', 'capricorn'],
    astrologyAssociations: ['Taurus', 'Virgo', 'Capricorn', 'Saturn', 'Venus'],
    numerologyAssociations: [4, 6],
    wiccaLore: {
      herbs: ['Patchouli', 'Vetiver', 'Oak', 'Pine', 'Cedar'],
      crystals: ['Jade', 'Moss Agate', 'Hematite', 'Green Tourmaline', 'Smoky Quartz'],
      rituals: 'Grounding meditation, gardening, earthing, prosperity spells',
      colors: ['Green', 'Brown', 'Black', 'Tan'],
      incense: ['Patchouli', 'Cedar', 'Pine', 'Myrrh'],
    },
    palmistryIndicators: 'Square palms, short thick fingers, deep clear lines, practical and grounded hand shape',
    oracleCorrespondences: {
      tarot: ['The Empress', 'The Hierophant', 'Pentacles suit', 'The World'],
      runes: ['Jera', 'Berkana', 'Ingwaz', 'Othala'],
    },
    traditionalRemedies: [
      'Walk barefoot on grass or soil for 11 minutes to ground your energy',
      'Carry a small piece of moss agate for stability and abundance',
      'Plant a seed or tend a garden to connect with earth energy',
      'Perform a grounding visualization: imagine roots growing from your feet into the earth',
      'Cook with root vegetables: potatoes, carrots, beets, and onions',
    ],
  },
  air: {
    element: 'Air',
    tags: ['air', 'communication', 'intellect', 'gemini', 'libra', 'aquarius'],
    astrologyAssociations: ['Gemini', 'Libra', 'Aquarius', 'Mercury', 'Uranus'],
    numerologyAssociations: [3, 5],
    wiccaLore: {
      herbs: ['Lavender', 'Dill', 'Anise', 'Mint', 'Clover'],
      crystals: ['Clear Quartz', 'Amethyst', 'Citrine', 'Apophyllite'],
      rituals: 'Incense work, meditation, study rituals, communication spells',
      colors: ['Yellow', 'Light Blue', 'White', 'Silver'],
      incense: ['Lavender', 'Frankincense', 'Mugwort', 'Copal'],
    },
    palmistryIndicators: 'Square palms with long fingers, prominent knuckles, many fine lines on the palm',
    oracleCorrespondences: {
      tarot: ['The Magician', 'The Lovers', 'Justice', 'Swords suit'],
      runes: ['Ansuz', 'Raido', 'Gebo', 'Laguz'],
    },
    traditionalRemedies: [
      'Practice deep breathing exercises for 5 minutes each morning',
      'Burn lavender or frankincense to clear mental fog',
      'Keep a journal to express thoughts and ideas freely',
      'Hang wind chimes near your window to attract clear communication energy',
      'Study something new to satisfy intellectual curiosity',
    ],
  },
  water: {
    element: 'Water',
    tags: ['water', 'emotion', 'intuition', 'cancer', 'scorpio', 'pisces'],
    astrologyAssociations: ['Cancer', 'Scorpio', 'Pisces', 'Moon', 'Neptune'],
    numerologyAssociations: [2, 7],
    wiccaLore: {
      herbs: ['Moonwort', 'Chamomile', 'Jasmine', 'Willow', 'Lotus'],
      crystals: ['Moonstone', 'Pearl', 'Amethyst', 'Aquamarine', 'Lapis Lazuli'],
      rituals: 'Moon rituals, bath magic, scrying, dreamwork, emotional healing',
      colors: ['Blue', 'Silver', 'Sea Green', 'Purple'],
      incense: ['Jasmine', 'Sage', 'Myrrh', 'Lotus'],
    },
    palmistryIndicators: 'Long palm with long flexible fingers, flowing lines, webbed or flexible thumbs',
    oracleCorrespondences: {
      tarot: ['The High Priestess', 'The Moon', 'The Hanged Man', 'Cups suit'],
      runes: ['Hagalaz', 'Isa', 'Ehwaz', 'Perthro'],
    },
    traditionalRemedies: [
      'Take a ritual bath with sea salt and lavender to cleanse your emotional body',
      'Carry moonstone to enhance intuition and emotional balance',
      'Spend time near water: ocean, lake, river, or even a fountain',
      'Keep a dream journal by your bed and record your dreams each morning',
      'Drink moon-charged water for emotional healing and psychic clarity',
    ],
  },
};

/**
 * Query the correspondence table by tag.
 *
 * @param {string} tag - e.g., 'fire', 'career', 'love'
 * @returns {Array} Matching correspondence entries
 */
export function queryCorrespondences(tag) {
  const results = [];
  const lowerTag = tag.toLowerCase();

  for (const [, entry] of Object.entries(CORRESPONDENCE_TABLE)) {
    if (entry.tags.some(t => t.includes(lowerTag))) {
      results.push(entry);
    }
  }

  return results;
}

/**
 * Get correspondence by element name.
 */
export function getCorrespondenceByElement(element) {
  const key = element.toLowerCase();
  return CORRESPONDENCE_TABLE[key] ?? null;
}

export default { queryCorrespondences, getCorrespondenceByElement, CORRESPONDENCE_TABLE };
