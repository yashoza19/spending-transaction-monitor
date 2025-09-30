import { Lightbulb } from 'lucide-react';
import { Card } from '../atoms/card/card';
import { Button } from '../atoms/button/button';
import { RecommendationCard } from './recommendation-card';
import { useRecommendations } from '../../hooks/recommendations';
import type { AlertRecommendation } from '../../schemas/recommendation';

export function AlertRecommendations() {
  const {
    data: recommendations,
    isLoading,
    removeRecommendation,
  } = useRecommendations();

  if (isLoading) {
    return (
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <Lightbulb className="h-5 w-5 text-primary" />
          <h2 className="text-xl font-semibold text-foreground">Recommended Alerts</h2>
        </div>
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <Card key={i} className="p-4">
              <div className="animate-pulse">
                <div className="h-5 bg-muted rounded w-3/4 mb-2" />
                <div className="h-4 bg-muted rounded w-1/2" />
              </div>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (!recommendations || recommendations.recommendations.length === 0) {
    return null; // Don't show anything if no recommendations
  }

  const { recommendation_type, recommendations: recs } = recommendations;

  return (
    <div className="mb-8">
      <div className="flex items-center gap-3 mb-4">
        <Lightbulb className="h-5 w-5 text-primary" />
        <div>
          <h2 className="text-xl font-semibold text-foreground">Recommended Rules</h2>
          <p className="text-sm text-muted-foreground">
            {recommendation_type === 'new_user'
              ? 'Get started with these essential alerts based on your profile'
              : 'Personalized alerts based on your spending patterns'}
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {recs.slice(0, 6).map((rec: AlertRecommendation) => (
          <RecommendationCard
            key={rec.natural_language_query}
            recommendation={rec}
            onCreated={() => removeRecommendation(rec.natural_language_query)}
          />
        ))}
      </div>

      {recs.length > 4 && (
        <div className="mt-3 text-center">
          <Button variant="ghost" size="sm" className="text-xs">
            View {recs.length - 4} more recommendations
          </Button>
        </div>
      )}
    </div>
  );
}
