/**
 * palm-analyzer.js
 *
 * Stub for palmistry image analysis.
 *
 * For v1: saves the uploaded image to disk, validates it's an image,
 * and returns basic metadata. The actual palm line/mount analysis
 * via CV/ML will be a future enhancement.
 *
 * Future v2: Integrate with a hand landmark detection model (e.g.,
 * MediaPipe Hands, TensorFlow.js, or a custom CV pipeline) to extract:
 *   - Heart line length/depth
 *   - Head line length/depth
 *   - Life line length/depth
 *   - Mount prominence
 *   - Hand shape classification
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const UPLOADS_DIR = path.join(__dirname, '..', '..', 'uploads', 'palmistry');

// Allowed MIME types
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

/**
 * Process an uploaded palm image.
 *
 * @param {Object} file - Multer file object { originalname, mimetype, path, size, filename }
 * @returns {Object} Analysis result
 */
export function processPalmImage(file) {
  if (!file) {
    return { uploaded: false, note: 'No palm image provided.' };
  }

  // Validate type
  if (!ALLOWED_TYPES.includes(file.mimetype)) {
    // Clean up invalid file
    try { fs.unlinkSync(file.path); } catch {}
    return {
      uploaded: false,
      error: `Invalid file type "${file.mimetype}". Accepted: JPEG, PNG, WebP, GIF.`,
    };
  }

  // Validate size
  if (file.size > MAX_FILE_SIZE) {
    try { fs.unlinkSync(file.path); } catch {}
    return {
      uploaded: false,
      error: 'File too large. Maximum size is 10 MB.',
    };
  }

  const imageUrl = `/uploads/palmistry/${file.filename}`;

  return {
    uploaded: true,
    imageUrl,
    filename: file.filename,
    originalName: file.originalname,
    size: file.size,
    mimeType: file.mimetype,
    // Future: analysis results from CV model go here
    analysis: {
      status: 'pending',
      note: 'Palm image stored. CV-based line analysis is coming in a future update. For now, use the palmistry questionnaire for line interpretation.',
    },
  };
}

/**
 * Validate and prepare palmistry data — combines questionnaire answers
 * with uploaded image data.
 *
 * @param {Object} questionnaire - Palmistry questionnaire answers from form
 * @param {Object} [imageFile] - Multer file object (optional)
 * @returns {Object} Combined palmistry input for the engine
 */
export function preparePalmistryInput(questionnaire = {}, imageFile = null) {
  const input = { ...questionnaire };

  if (imageFile) {
    const imageResult = processPalmImage(imageFile);
    if (imageResult.uploaded) {
      input.palmImage = imageResult;
    }
  }

  return input;
}

export default { processPalmImage, preparePalmistryInput };
