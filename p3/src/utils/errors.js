/**
 * errors.js
 *
 * Custom error classes and centralized error handler middleware.
 * Provides consistent error responses across the API.
 */

import path from 'path';
import { fileURLToPath } from 'url';

// ─── Custom Error Classes ───────────────────────────────────────────────────

export class AppError extends Error {
  constructor(message, statusCode = 500, code = 'INTERNAL_ERROR') {
    super(message);
    this.name = 'AppError';
    this.statusCode = statusCode;
    this.code = code;
    this.isOperational = true;
    Error.captureStackTrace(this, this.constructor);
  }
}

export class ValidationError extends AppError {
  constructor(message = 'Validation failed') {
    super(message, 400, 'VALIDATION_ERROR');
    this.name = 'ValidationError';
  }
}

export class AuthError extends AppError {
  constructor(message = 'Authentication failed') {
    super(message, 401, 'AUTH_ERROR');
    this.name = 'AuthError';
  }
}

export class NotFoundError extends AppError {
  constructor(resource = 'Resource') {
    super(`${resource} not found`, 404, 'NOT_FOUND');
    this.name = 'NotFoundError';
  }
}

export class RateLimitError extends AppError {
  constructor(message = 'Too many requests') {
    super(message, 429, 'RATE_LIMIT');
    this.name = 'RateLimitError';
  }
}

// ─── Error Handler Middleware ───────────────────────────────────────────────

/**
 * Centralized error handler for Express.
 * Must have 4 parameters for Express to recognize it as error middleware.
 */
export function errorHandler(err, req, res, _next) {
  // Determine status code and message
  const statusCode = err.statusCode || 500;
  const code = err.code || 'INTERNAL_ERROR';
  const message = err.isOperational
    ? err.message
    : 'An unexpected error occurred';

  // Log server errors with stack
  if (statusCode >= 500) {
    const __dirname = path.dirname(fileURLToPath(import.meta.url));
    const relativePath = path.relative(process.cwd(), __dirname);
    console.error(`[${new Date().toISOString()}] ${statusCode} ${code}:`, err.message);
    console.error(`  File: ${path.join(relativePath, err.stack?.split('\n')[1]?.trim() || '')}`);
    if (process.env.NODE_ENV !== 'production') {
      console.error(err.stack);
    }
  }

  // Response
  res.status(statusCode).json({
    success: false,
    error: {
      code,
      message,
      ...(process.env.NODE_ENV !== 'production' && { stack: err.stack?.split('\n').slice(0, 4).join('\n') }),
    },
  });
}

/**
 * Wrap async route handlers so errors are forwarded to Express error middleware.
 */
export function asyncHandler(fn) {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}

export default { AppError, ValidationError, AuthError, NotFoundError, RateLimitError, errorHandler, asyncHandler };
