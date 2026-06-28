/**
 * User Model (In-Memory)
 *
 * Simple user storage for authentication.
 * Swap for MongoDB/Mongoose when ready for production.
 *
 * Each user has:
 * - id:        UUID
 * - email:     unique login identifier
 * - password:  bcrypt-hashed
 * - profile:   name, birthDate, etc.
 * - history:   array of past reading references
 * - createdAt: ISO timestamp
 */

import { v4 as uuidv4 } from 'uuid';
import bcrypt from 'bcryptjs';

const SALT_ROUNDS = 10;

// In-memory store (replace with DB later)
const users = new Map();

class UserModel {
  /**
   * Create a new user.
   * @param {string} email
   * @param {string} password - plain text (will be hashed)
   * @param {Object} [profile]
   * @returns {Promise<Object>} The new user object (without password)
   */
  static async create(email, password, profile = {}) {
    // Check if email already exists
    const existing = await this.findByEmail(email);
    if (existing) {
      throw Object.assign(new Error('Email already registered'), { statusCode: 409, code: 'EMAIL_EXISTS' });
    }

    const hash = await bcrypt.hash(password, SALT_ROUNDS);
    const user = {
      id: uuidv4(),
      email: email.toLowerCase().trim(),
      password: hash,
      profile: {
        fullName: profile.fullName || '',
        birthDate: profile.birthDate || null,
        birthTime: profile.birthTime || null,
        locationText: profile.locationText || null,
        latitude: profile.latitude || null,
        longitude: profile.longitude || null,
        gender: profile.gender || null,
        palmImage: profile.palmImage || null,
      },
      history: [],
      createdAt: new Date().toISOString(),
      lastLogin: null,
    };

    users.set(user.id, user);
    return this.sanitize(user);
  }

  /**
   * Verify email + password.
   * @returns {Promise<Object|null>} User object (without password) or null
   */
  static async authenticate(email, password) {
    const user = await this.findByEmail(email);
    if (!user) return null;

    const match = await bcrypt.compare(password, user.password);
    if (!match) return null;

    user.lastLogin = new Date().toISOString();
    return this.sanitize(user);
  }

  /**
   * Find user by email.
   * @returns {Promise<Object|undefined>}
   */
  static async findByEmail(email) {
    const lowerEmail = email.toLowerCase().trim();
    for (const user of users.values()) {
      if (user.email === lowerEmail) return user;
    }
    return undefined;
  }

  /**
   * Find user by ID.
   * @returns {Promise<Object|undefined>}
   */
  static async findById(id) {
    return users.get(id) || undefined;
  }

  /**
   * Update user profile fields.
   * @returns {Promise<Object>} Updated user (without password)
   */
  static async updateProfile(id, updates) {
    const user = users.get(id);
    if (!user) return null;

    if (updates.profile) {
      Object.assign(user.profile, updates.profile);
    }
    if (updates.fullName !== undefined) user.profile.fullName = updates.fullName;
    if (updates.birthDate !== undefined) user.profile.birthDate = updates.birthDate;
    if (updates.birthTime !== undefined) user.profile.birthTime = updates.birthTime;
    if (updates.locationText !== undefined) user.profile.locationText = updates.locationText;
    if (updates.latitude !== undefined) user.profile.latitude = updates.latitude;
    if (updates.longitude !== undefined) user.profile.longitude = updates.longitude;
    if (updates.gender !== undefined) user.profile.gender = updates.gender;
    if (updates.palmImage !== undefined) user.profile.palmImage = updates.palmImage;

    return this.sanitize(user);
  }

  /**
   * Add a reading reference to user history.
   */
  static async addReadingToHistory(userId, readingId) {
    const user = users.get(userId);
    if (!user) return;
    user.history.push({ readingId, timestamp: new Date().toISOString() });
    // Keep last 50
    if (user.history.length > 50) user.history = user.history.slice(-50);
  }

  /**
   * Get all users (admin only — no passwords).
   * @returns {Promise<Array>}
   */
  static async getAll() {
    return Array.from(users.values()).map(u => this.sanitize(u));
  }

  /** Strip password from user object before returning. */
  static sanitize(user) {
    if (!user) return null;
    const { password, ...safe } = user;
    return safe;
  }
}

export default UserModel;
