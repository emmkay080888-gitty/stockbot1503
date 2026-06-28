/**
 * geocoder.js
 *
 * Converts a place name, city, or zipcode to latitude/longitude coordinates
 * using OpenStreetMap's Nominatim API (free, no API key required).
 *
 * Usage:
 *   import { geocode } from './geocoder.js';
 *   const coords = await geocode('London, UK');
 *   // => { latitude: 51.5074, longitude: -0.1278, displayName: 'London, UK' }
 */

const NOMINATIM_BASE = 'https://nominatim.openstreetmap.org';

/**
 * Geocode a location string (place name, city, zipcode, address).
 *
 * @param {string} query - e.g., "London", "10001", "Mumbai, India"
 * @returns {Promise<{latitude: number|null, longitude: number|null, displayName: string|null}>}
 */
export async function geocode(query) {
  if (!query || typeof query !== 'string' || query.trim().length < 2) {
    return { latitude: null, longitude: null, displayName: null };
  }

  const params = new URLSearchParams({
    q: query.trim(),
    format: 'json',
    limit: 1,
    addressdetails: 0,
  });

  const url = `${NOMINATIM_BASE}/search?${params}`;

  try {
    const response = await fetch(url, {
      headers: {
        // Nominatim requires a User-Agent for fair use
        'User-Agent': 'EsotericEngine/1.0 (occult-remedies-app)',
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      console.warn(`Nominatim geocoding failed: ${response.status}`);
      return { latitude: null, longitude: null, displayName: null };
    }

    const data = await response.json();

    if (!Array.isArray(data) || data.length === 0) {
      console.warn(`No results found for: "${query}"`);
      return { latitude: null, longitude: null, displayName: query };
    }

    const result = data[0];
    return {
      latitude: parseFloat(result.lat) || null,
      longitude: parseFloat(result.lon) || null,
      displayName: result.display_name || query,
    };
  } catch (err) {
    console.error('Geocoding error:', err.message);
    return { latitude: null, longitude: null, displayName: query };
  }
}

/**
 * Reverse geocode — convert lat/lng to a place name.
 *
 * @param {number} latitude
 * @param {number} longitude
 * @returns {Promise<{displayName: string|null}>}
 */
export async function reverseGeocode(latitude, longitude) {
  if (!latitude || !longitude) {
    return { displayName: null };
  }

  const params = new URLSearchParams({
    lat: String(latitude),
    lon: String(longitude),
    format: 'json',
  });

  try {
    const response = await fetch(`${NOMINATIM_BASE}/reverse?${params}`, {
      headers: {
        'User-Agent': 'EsotericEngine/1.0 (occult-remedies-app)',
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      return { displayName: null };
    }

    const data = await response.json();
    return {
      displayName: data.display_name || null,
    };
  } catch {
    return { displayName: null };
  }
}

export default { geocode, reverseGeocode };
