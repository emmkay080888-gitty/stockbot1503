/**
 * Auth Routes — /api/v1/auth
 *
 * POST /signup   — Register a new user
 * POST /login    — Authenticate and receive JWT
 * GET  /profile  — Get current user profile (requires auth)
 * PATCH /profile — Update user profile (requires auth)
 */

import { Router } from 'express';
import UserModel from '../models/User.js';
import { generateToken, requireAuth } from '../middleware/auth.js';
import { ValidationError, AuthError, asyncHandler } from '../utils/errors.js';

const router = Router();

// ─── POST /signup ──────────────────────────────────────────────────────────

router.post('/signup', asyncHandler(async (req, res) => {
  const { email, password, fullName, birthDate } = req.body;

  // Validation
  if (!email || !password) {
    throw new ValidationError('Email and password are required.');
  }
  if (typeof email !== 'string' || !email.includes('@')) {
    throw new ValidationError('Please provide a valid email address.');
  }
  if (password.length < 6) {
    throw new ValidationError('Password must be at least 6 characters.');
  }
  if (birthDate) {
    const parsed = new Date(birthDate);
    if (isNaN(parsed.getTime())) {
      throw new ValidationError('birthDate must be a valid ISO date (e.g., "1990-06-15").');
    }
  }

  // Create user
  const user = await UserModel.create(email, password, { fullName, birthDate });
  const token = generateToken(user);

  res.status(201).json({
    success: true,
    data: {
      user,
      token,
      message: 'Account created. Welcome to the Esoteric Engine.',
    },
  });
}));

// ─── POST /login ───────────────────────────────────────────────────────────

router.post('/login', asyncHandler(async (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    throw new ValidationError('Email and password are required.');
  }

  const user = await UserModel.authenticate(email, password);
  if (!user) {
    throw new AuthError('Invalid email or password.');
  }

  const token = generateToken(user);

  res.json({
    success: true,
    data: {
      user,
      token,
    },
  });
}));

// ─── GET /profile ──────────────────────────────────────────────────────────

router.get('/profile', requireAuth, asyncHandler(async (req, res) => {
  const user = await UserModel.findById(req.user.id);
  if (!user) {
    throw new AuthError('User not found.');
  }

  res.json({
    success: true,
    data: user,
  });
}));

// ─── PATCH /profile ────────────────────────────────────────────────────────

router.patch('/profile', requireAuth, asyncHandler(async (req, res) => {
  const allowedFields = ['fullName', 'birthDate', 'birthTime', 'locationText', 'latitude', 'longitude', 'gender'];
  const updates = {};

  for (const field of allowedFields) {
    if (req.body[field] !== undefined) {
      updates[field] = req.body[field];
    }
  }

  const user = await UserModel.updateProfile(req.user.id, updates);
  if (!user) {
    throw new AuthError('User not found.');
  }

  res.json({
    success: true,
    data: user,
  });
}));

export default router;
