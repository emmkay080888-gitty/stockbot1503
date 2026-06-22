/**
 * auth.js — JWT Authentication Middleware
 *
 * Verifies the Bearer token on protected routes.
 * Attaches decoded user info to req.user.
 */

import jwt from 'jsonwebtoken';
import { AuthError } from '../utils/errors.js';

// In production, store this in an environment variable
const JWT_SECRET = process.env.JWT_SECRET || 'esoteric-engine-dev-secret-change-in-production';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '7d';

/**
 * Generate a JWT for a user.
 * @param {Object} user - Sanitized user object (without password)
 * @returns {string} JWT token
 */
export function generateToken(user) {
  return jwt.sign(
    { id: user.id, email: user.email },
    JWT_SECRET,
    { expiresIn: JWT_EXPIRES_IN }
  );
}

/**
 * JWT verification middleware.
 * Attaches decoded payload to req.user on success.
 */
export function requireAuth(req, res, next) {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return next(new AuthError('Missing or invalid authorization header. Use: Bearer <token>'));
  }

  const token = authHeader.split(' ')[1];

  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    if (err.name === 'TokenExpiredError') {
      return next(new AuthError('Token expired. Please log in again.'));
    }
    return next(new AuthError('Invalid token.'));
  }
}

/**
 * Optional auth middleware — attaches user if token is present, but doesn't reject.
 */
export function optionalAuth(req, res, next) {
  const authHeader = req.headers.authorization;

  if (authHeader && authHeader.startsWith('Bearer ')) {
    const token = authHeader.split(' ')[1];
    try {
      const decoded = jwt.verify(token, JWT_SECRET);
      req.user = decoded;
    } catch {
      // Silently ignore invalid tokens
    }
  }

  next();
}

export { JWT_SECRET };
