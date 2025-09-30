import { useState, useEffect } from 'react';
import { Card } from '../atoms/card/card';
import { Button } from '../atoms/button/button';
import { Badge } from '../atoms/badge/badge';
import {
  Lightbulb,
  ChevronRight,
  Shield,
  CreditCard,
  MapPin,
  TrendingUp,
  AlertTriangle,
  Loader2,
  Wifi,
  WifiOff,
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { useWebSocket } from '../../hooks/useWebSocket';

interface AlertRecommendation {
  title: string;
  description: string;
  natural_language_query: string;
  category: string;
  priority: 'high' | 'medium' | 'low';
  reasoning: string;
}

interface AlertRecommendationsResponse {
  user_id: string;
  recommendation_type: 'new_user' | 'transaction_based' | 'placeholder';
  recommendations: AlertRecommendation[];
  generated_at: string;
  is_placeholder?: boolean;
  message?: string;
}

interface AlertRecommendationsProps {
  recommendations: AlertRecommendationsResponse | null;
  isLoading: boolean;
  onCreateRule: (recommendation: AlertRecommendation) => Promise<void>;
  userId: string;
  onRecommendationsUpdate?: (recommendations: AlertRecommendationsResponse) => void;
}

const categoryIcons = {
  fraud_protection: Shield,
  spending_threshold: CreditCard,
  location_based: MapPin,
  merchant_monitoring: TrendingUp,
  subscription_monitoring: TrendingUp,
} as const;

const priorityColors = {
  high: 'bg-red-100 text-red-800 border-red-200 dark:bg-red-950 dark:text-red-300 dark:border-red-800',
  medium:
    'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-950 dark:text-yellow-300 dark:border-yellow-800',
  low: 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-950 dark:text-blue-300 dark:border-blue-800',
};

export function AlertRecommendations({
  recommendations,
  isLoading,
  onCreateRule,
  userId,
  onRecommendationsUpdate,
}: AlertRecommendationsProps) {
  const [expandedCard, setExpandedCard] = useState<number | null>(null);
  const [createdRules, setCreatedRules] = useState<Set<string>>(new Set());
  const [creatingIndex, setCreatingIndex] = useState<number | null>(null);
  const [isGeneratingPersonalized, setIsGeneratingPersonalized] = useState(false);

  // WebSocket connection for real-time updates
  const { isConnected } = useWebSocket({
    userId,
    onRecommendationsReady: (newRecommendations) => {
      setIsGeneratingPersonalized(false);
      if (onRecommendationsUpdate) {
        onRecommendationsUpdate(newRecommendations);
      }
    },
  });

  // Check if we're showing placeholder recommendations
  const isPlaceholder = recommendations?.is_placeholder || recommendations?.recommendation_type === 'placeholder';
  
  // Set generating state when we have placeholder recommendations
  useEffect(() => {
    if (isPlaceholder && !isGeneratingPersonalized) {
      setIsGeneratingPersonalized(true);
    }
  }, [isPlaceholder, isGeneratingPersonalized]);

  const handleCreateRule = async (
    index: number,
    recommendation: AlertRecommendation,
  ) => {
    try {
      setCreatingIndex(index);
      await onCreateRule(recommendation);

      // Mark this rule as created using the natural language query as stable identifier
      setCreatedRules((prev) =>
        new Set(prev).add(recommendation.natural_language_query),
      );
    } catch (error) {
      console.error('Failed to create rule:', error);
    } finally {
      setCreatingIndex(null);
    }
  };

  const toggleExpanded = (index: number) => {
    setExpandedCard(expandedCard === index ? null : index);
  };

  if (isLoading) {
    return (
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <Lightbulb className="h-5 w-5 text-primary" />
          <h2 className="text-xl font-semibold text-foreground">Recommended Rules</h2>
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
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <Lightbulb className="h-5 w-5 text-primary" />
          <div>
            <h2 className="text-xl font-semibold text-foreground">Recommended Alerts</h2>
            <p className="text-sm text-muted-foreground">
              {recommendation_type === 'new_user'
                ? 'Get started with these essential alerts based on your profile'
                : recommendation_type === 'placeholder'
                  ? 'Showing general recommendations while we analyze your spending patterns...'
                  : 'Personalized alerts based on your spending patterns'}
            </p>
          </div>
        </div>
        
        {/* Status indicators */}
        <div className="flex items-center gap-2">
          {/* WebSocket connection status */}
          <div className="flex items-center gap-1 text-xs">
            {isConnected ? (
              <Wifi className="h-3 w-3 text-green-500" />
            ) : (
              <WifiOff className="h-3 w-3 text-red-500" />
            )}
            <span className={cn(
              'text-xs',
              isConnected ? 'text-green-600' : 'text-red-600'
            )}>
              {isConnected ? 'Live' : 'Offline'}
            </span>
          </div>
          
          {/* Generating personalized recommendations indicator */}
          {isGeneratingPersonalized && (
            <div className="flex items-center gap-1 text-xs text-blue-600">
              <Loader2 className="h-3 w-3 animate-spin" />
              <span>Generating personalized recommendations...</span>
            </div>
          )}
        </div>
      </div>

      <div className="space-y-3">
        {recs.slice(0, 6).map((rec: AlertRecommendation, index: number) => {
          const IconComponent = categoryIcons[rec.category as keyof typeof categoryIcons] || AlertTriangle;
          const isExpanded = expandedCard === index;
          const isCreated = createdRules.has(rec.natural_language_query);
          const isCreating = creatingIndex === index;

          return (
            <Card
              key={rec.natural_language_query}
              className={cn(
                'p-4 transition-all duration-200 hover:shadow-md',
                isExpanded && 'shadow-lg ring-2 ring-primary/20',
                isCreated && 'bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-800'
              )}
            >
              <div className="space-y-3">
                {/* Header */}
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1">
                    <div className="flex-shrink-0 mt-1">
                      <IconComponent className="h-5 w-5 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-foreground truncate">
                          {rec.title}
                        </h3>
                        <Badge
                          variant="secondary"
                          className={cn(
                            'text-xs',
                            priorityColors[rec.priority]
                          )}
                        >
                          {rec.priority}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {rec.description}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 ml-4">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleExpanded(index)}
                      className="text-muted-foreground hover:text-foreground"
                    >
                      <ChevronRight
                        className={cn(
                          'h-4 w-4 transition-transform',
                          isExpanded && 'rotate-90'
                        )}
                      />
                    </Button>
                  </div>
                </div>

                {/* Expanded Content */}
                {isExpanded && (
                  <div className="space-y-3 pt-3 border-t border-border">
                    <div>
                      <h4 className="text-sm font-medium text-foreground mb-2">
                        Natural Language Query
                      </h4>
                      <p className="text-sm text-muted-foreground font-mono bg-muted p-2 rounded">
                        "{rec.natural_language_query}"
                      </p>
                    </div>
                    
                    <div>
                      <h4 className="text-sm font-medium text-foreground mb-2">
                        Reasoning
                      </h4>
                      <p className="text-sm text-muted-foreground">
                        {rec.reasoning}
                      </p>
                    </div>

                    {/* Action Button */}
                    <div className="flex justify-end pt-2">
                      <Button
                        onClick={() => handleCreateRule(index, rec)}
                        disabled={isCreated || isCreating}
                        className={cn(
                          'min-w-[120px]',
                          isCreated && 'bg-green-100 text-green-800 hover:bg-green-100 dark:bg-green-900 dark:text-green-200'
                        )}
                      >
                        {isCreating ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Creating...
                          </>
                        ) : isCreated ? (
                          '✓ Created'
                        ) : (
                          'Create Rule'
                        )}
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </Card>
          );
        })}
      </div>

      {recs.length > 6 && (
        <div className="mt-3 text-center">
          <Button variant="ghost" size="sm" className="text-xs">
            View {recs.length - 6} more recommendations
          </Button>
        </div>
      )}
    </div>
  );
}
