import { Badge } from '../atoms/badge/badge';
import {
  cn,
  formatAmount,
  formatTime,
  getStatusColor,
  getCategoryIcon,
} from '../../lib/utils';
import type { Transaction } from '../../schemas/transaction';

export interface TransactionCardProps {
  transaction: Transaction;
  onClick?: (transaction: Transaction) => void;
  isSelected?: boolean;
  className?: string;
}

export function TransactionCard({
  transaction,
  onClick,
  isSelected = false,
  className,
}: TransactionCardProps) {
  return (
    <div
      className={cn(
        'rounded-lg border transition-colors group',
        onClick ? 'cursor-pointer hover:bg-muted/50' : 'cursor-default',
        isSelected
          ? 'border-primary bg-primary/5 ring-1 ring-primary/20'
          : 'border-border',
        // Responsive padding and layout
        'p-3 sm:p-4',
        className,
      )}
      onClick={() => onClick?.(transaction)}
    >
      {/* Mobile layout (stacked) */}
      <div className="flex flex-col gap-3 sm:hidden">
        {/* Top row: icon, merchant, amount */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 min-w-0 flex-1">
            <div className="text-xl flex-shrink-0">
              {getCategoryIcon(transaction.category)}
            </div>
            <div className="min-w-0 flex-1">
              <p className="font-medium text-foreground truncate">
                {transaction.merchant}
              </p>
              {transaction.category && (
                <p className="text-xs text-muted-foreground truncate mt-0.5">
                  {transaction.category}
                </p>
              )}
            </div>
          </div>
          <span className="font-semibold text-foreground text-sm flex-shrink-0 ml-2">
            {formatAmount(transaction.amount)}
          </span>
        </div>

        {/* Bottom row: status, time, transaction ID */}
        <div className="flex items-center justify-between gap-2">
          <Badge
            variant="secondary"
            className={cn('capitalize text-xs', getStatusColor(transaction.status))}
          >
            {transaction.status}
          </Badge>
          <div className="flex items-center gap-1 text-xs text-muted-foreground min-w-0">
            <span className="truncate">{transaction.id}</span>
            <span>•</span>
            <span className="flex-shrink-0">{formatTime(transaction.time)}</span>
          </div>
        </div>
      </div>

      {/* Desktop layout (horizontal) */}
      <div className="hidden sm:flex items-center justify-between">
        <div className="flex items-center gap-4 min-w-0 flex-1">
          <div className="text-2xl flex-shrink-0">
            {getCategoryIcon(transaction.category)}
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <p className="font-medium text-foreground">{transaction.merchant}</p>
              {transaction.category && (
                <span className="text-xs text-muted-foreground">
                  • {transaction.category}
                </span>
              )}
            </div>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-sm text-muted-foreground">{transaction.id}</span>
              <span className="text-sm text-muted-foreground">•</span>
              <span className="text-sm text-muted-foreground">
                {formatTime(transaction.time)}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-shrink-0">
          <Badge
            variant="secondary"
            className={cn('capitalize', getStatusColor(transaction.status))}
          >
            {transaction.status}
          </Badge>
          <span className="font-semibold text-foreground min-w-[100px] text-right">
            {formatAmount(transaction.amount)}
          </span>
        </div>
      </div>
    </div>
  );
}
