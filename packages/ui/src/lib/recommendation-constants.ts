import {
  Shield,
  CreditCard,
  MapPin,
  TrendingUp,
} from 'lucide-react';

export const categoryIcons = {
  fraud_protection: Shield,
  spending_threshold: CreditCard,
  location_based: MapPin,
  merchant_monitoring: TrendingUp,
  subscription_monitoring: TrendingUp,
} as const;

export const priorityColors = {
  high: 'bg-red-100 text-red-800 border-red-200 dark:bg-red-950 dark:text-red-300 dark:border-red-800',
  medium:
    'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-950 dark:text-yellow-300 dark:border-yellow-800',
  low: 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-950 dark:text-blue-300 dark:border-blue-800',
} as const;