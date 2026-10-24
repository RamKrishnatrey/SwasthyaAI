import type { Caregiver } from '../types/agent';

export const RANKING_WEIGHTS = {
  skillFit: 0.35,
  distance: 0.25,
  availability: 0.20,
  language: 0.10,
  rating: 0.10,
} as const;

export interface RankedCaregiver extends Caregiver {
  score: number;
  contributions: {
    skillFit: number;
    distance: number;
    availability: number;
    language: number;
    rating: number;
  };
}

/**
 * Demo ranking only. Mandatory eligibility checks must happen before this function.
 * Scores are configurable engineering weights, not clinical quality or outcome probabilities.
 */
export function rankCaregiver(caregiver: Caregiver): RankedCaregiver {
  const distanceScore = Math.max(0, Math.min(1, 1 - caregiver.distanceKm / 20));
  const contributions = {
    skillFit: caregiver.skillFit * RANKING_WEIGHTS.skillFit,
    distance: distanceScore * RANKING_WEIGHTS.distance,
    availability: caregiver.slotSuitability * RANKING_WEIGHTS.availability,
    language: caregiver.languageFit * RANKING_WEIGHTS.language,
    rating: caregiver.ratingScore * RANKING_WEIGHTS.rating,
  };
  const score = Object.values(contributions).reduce((sum, value) => sum + value, 0);
  return { ...caregiver, score, contributions };
}
