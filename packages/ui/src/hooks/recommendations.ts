import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { realAlertService as alertService } from '../services/api-transaction';
import type { AlertRecommendation } from '../schemas/recommendation';

// Custom hook for recommendations with local state management
export const useRecommendations = () => {
  const [localRemovedIds, setLocalRemovedIds] = useState<Set<string>>(new Set());

  const {
    data: serverData,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['alertRecommendations'],
    queryFn: () => alertService.getAlertRecommendations(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Merge server data with local state (removing locally created recommendations)
  const recommendations = serverData?.recommendations?.filter(
    (rec: AlertRecommendation) => !localRemovedIds.has(rec.natural_language_query)
  ) || [];

  const removeRecommendation = (naturalLanguageQuery: string) => {
    setLocalRemovedIds(prev => new Set(prev).add(naturalLanguageQuery));
  };

  return {
    data: serverData ? {
      ...serverData,
      recommendations,
    } : null,
    isLoading,
    error,
    refetch,
    removeRecommendation,
  };
};

export const useCreateRuleFromRecommendation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (recommendation: AlertRecommendation) =>
      alertService.createRuleFromRecommendation(recommendation),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alertRules'] });
      queryClient.invalidateQueries({ queryKey: ['alertRecommendations'] });
    },
  });
};