/**
 * Reading Route — POST /api/v1/reading
 *
 * Accepts user input (multipart/form-data for image upload support)
 * and returns a full composite esoteric reading.
 *
 * Fields:
 *   birthDate    (required) ISO date, e.g. "1990-06-15"
 *   birthTime    (optional) HH:mm
 *   locationText (optional) Place name, city, or zipcode
 *   fullName     (optional) Full birth name
 *   gender       (optional) male | female | non-binary | prefer-not-to-say
 *   question     (optional) Life question
 *   palmImage    (optional) File upload — clear photo of palm
 *   handShape    (optional) Palmistry questionnaire
 *   heartLength, heartDepth, heartCurvature, etc.
 */

import { Router } from 'express';
import { runFullReading } from '../engines/EsotericEngine.js';
import { ValidationError, asyncHandler } from '../utils/errors.js';
import { preparePalmistryInput } from '../utils/palm-analyzer.js';
import upload from '../middleware/upload.js';

const router = Router();

/**
 * POST /api/v1/reading
 */
router.post('/', upload.single('palmImage'), asyncHandler(async (req, res) => {
  const {
    birthDate,
    birthTime,
    locationText,
    fullName,
    gender,
    question,
    handShape, heartLength, heartDepth, heartCurvature,
    headLength, headDepth, headAngle,
    lifeLength, lifeDepth, lifeShape,
  } = req.body;

  // Validate required fields
  if (!birthDate) {
    throw new ValidationError('Please provide a birth date in ISO format (e.g., "1990-06-15").');
  }

  // Validate date
  const parsedDate = new Date(birthDate);
  if (isNaN(parsedDate.getTime())) {
    throw new ValidationError('birthDate must be a valid ISO date string (e.g., "1990-06-15").');
  }

  // Validate birth time format if provided
  if (birthTime && !/^\d{2}:\d{2}$/.test(birthTime)) {
    throw new ValidationError('birthTime must be in HH:mm 24-hour format (e.g., "14:30").');
  }

  // Validate gender if provided
  if (gender && !['male', 'female', 'non-binary', 'prefer-not-to-say'].includes(gender)) {
    throw new ValidationError('gender must be one of: male, female, non-binary, prefer-not-to-say.');
  }

  // Build palmistry answers from form fields + optional image
  const palmistryAnswers = preparePalmistryInput({
    handShape, heartLength, heartDepth, heartCurvature,
    headLength, headDepth, headAngle,
    lifeLength, lifeDepth, lifeShape,
  }, req.file);

  // Run the full engine
  const reading = await runFullReading({
    birthDate,
    birthTime,
    locationText,
    fullName,
    gender,
    question,
    palmistryAnswers,
  });

  return res.json({
    success: true,
    data: reading,
  });
}));

/**
 * GET /api/v1/reading/health
 * Simple health check.
 */
router.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    version: '1.0.0',
    engines: ['numerology', 'astrology', 'wicca', 'palmistry'],
  });
});

export default router;
