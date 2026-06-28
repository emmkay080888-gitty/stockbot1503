/**
 * Occult Remedies App — Composite Esoteric Engine
 *
 * Express server that orchestrates multi-lens esoteric analysis.
 * Uses Node `path` module for all relative path resolution.
 */

import path from 'path';
import { fileURLToPath } from 'url';
import express from 'express';
import readingRouter from './routes/reading.js';
import authRouter from './routes/auth.js';
import { errorHandler } from './utils/errors.js';

// ─── Path Setup (using Node path module) ────────────────────────────────────

const __filename = fileURLToPath(import.meta.url);
const __dirname  = path.dirname(__filename);
const PUBLIC_DIR = path.join(__dirname, '..', 'public');

// ─── App ────────────────────────────────────────────────────────────────────

const app = express();
const PORT = process.env.PORT ?? 3001;

// ─── Middleware ──────────────────────────────────────────────────────────────

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// ─── CORS ───────────────────────────────────────────────────────────────────

app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS');
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});

// ─── Static Files (Frontend Dashboard + Uploads) ────────────────────────────

app.use(express.static(PUBLIC_DIR, { extensions: ['html'] }));
app.use('/uploads', express.static(path.join(__dirname, '..', 'uploads')));

// ─── API Routes ─────────────────────────────────────────────────────────────

app.use('/api/v1/auth',     authRouter);
app.use('/api/v1/reading',  readingRouter);

// ─── 404 Handler — unmatched API routes ─────────────────────────────────────

app.use('/api', (req, res) => {
  res.status(404).json({
    success: false,
    error: {
      code: 'NOT_FOUND',
      message: `Route ${req.method} ${req.path} does not exist.`,
    },
  });
});

// ─── Centralized Error Handler (must be last) ───────────────────────────────

app.use(errorHandler);

// ─── Startup ────────────────────────────────────────────────────────────────

app.listen(PORT, () => {
  console.log(`🌙 Composite Esoteric Engine running on http://localhost:${PORT}`);
  console.log(`📡 Endpoints:`);
  console.log(`   🌐  http://localhost:${PORT}                  — Browser dashboard`);
  console.log(`   POST http://localhost:${PORT}/api/v1/auth/signup    — Create account`);
  console.log(`   POST http://localhost:${PORT}/api/v1/auth/login     — Log in`);
  console.log(`   GET  http://localhost:${PORT}/api/v1/auth/profile   — Your profile (auth)`);
  console.log(`   POST http://localhost:${PORT}/api/v1/reading        — Full esoteric reading`);
  console.log(`   GET  http://localhost:${PORT}/api/v1/reading/health — Health check`);
  console.log(`📖 Try it:`);
  console.log(`   curl -X POST http://localhost:${PORT}/api/v1/reading \\\\`);
  console.log(`     -H 'Content-Type: application/json' \\\\`);
  console.log(`     -d '{ "birthDate": "1990-06-15", "fullName": "Jane Doe" }' | python3 -m json.tool`);
});

export default app;
