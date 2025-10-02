import type {
  AlertRecommendation,
  AlertRecommendationsResponse,
} from '../schemas/recommendation';
import { apiClient } from './apiClient';

// Alert recommendation service for real API data
export const alertRecommendationService = {
  // Get alert recommendations
  async getAlertRecommendations(): Promise<AlertRecommendationsResponse> {
    try {
      const response = await apiClient.fetch('/api/alerts/recommendations');

      if (!response.ok) {
        throw new Error(
          `Failed to fetch alert recommendations: ${response.status} ${response.statusText}`,
        );
      }

      const recommendations = await response.json();
      return recommendations;
    } catch (error) {
      console.error('Error fetching alert recommendations:', error);
      throw new Error(
        error instanceof Error
          ? error.message
          : 'Failed to fetch alert recommendations',
      );
    }
  },

  // Create rule from recommendation
  async createRuleFromRecommendation(recommendation: AlertRecommendation): Promise<{
    message: string;
    rule_id: string;
    rule_name: string;
    recommendation_used: {
      title: string;
      description: string;
      natural_language_query: string;
      category: string;
      priority: string;
      reasoning: string;
    };
  }> {
    try {
      const response = await apiClient.fetch(
        '/api/alerts/recommendations/create-rule',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(recommendation),
        },
      );

      if (!response.ok) {
        throw new Error(
          `Failed to create rule from recommendation: ${response.status} ${response.statusText}`,
        );
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Error creating rule from recommendation:', error);
      throw new Error(
        error instanceof Error
          ? error.message
          : 'Failed to create rule from recommendation',
      );
    }
  },
};
