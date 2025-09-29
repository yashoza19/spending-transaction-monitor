import type { Meta, StoryObj } from '@storybook/react';
import { TransactionCard } from './transaction-card';
import type { Transaction } from '../../schemas/transaction';

const meta: Meta<typeof TransactionCard> = {
  title: 'Components/TransactionCard',
  component: TransactionCard,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
  argTypes: {
    onClick: { action: 'clicked' },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

const sampleTransaction: Transaction = {
  id: 'txn_1234567890',
  amount: 45.67,
  merchant: 'Coffee Shop Downtown',
  category: 'dining',
  status: 'completed',
  time: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30 minutes ago
  type: 'purchase',
  currency: 'USD',
  description: 'Morning coffee and pastry',
};

export const Default: Story = {
  args: {
    transaction: sampleTransaction,
  },
};

export const Selected: Story = {
  args: {
    transaction: sampleTransaction,
    isSelected: true,
  },
};

export const Pending: Story = {
  args: {
    transaction: {
      ...sampleTransaction,
      status: 'pending',
      merchant: 'Online Store',
      category: 'shopping',
      amount: 129.99,
      type: 'purchase',
    },
  },
};

export const Failed: Story = {
  args: {
    transaction: {
      ...sampleTransaction,
      status: 'failed',
      merchant: 'Gas Station',
      category: 'transport',
      amount: 65.43,
      type: 'purchase',
    },
  },
};

export const LargeAmount: Story = {
  args: {
    transaction: {
      ...sampleTransaction,
      merchant: 'Electronics Store',
      category: 'shopping',
      amount: 1299.99,
      type: 'purchase',
    },
  },
};

export const LongMerchantName: Story = {
  args: {
    transaction: {
      ...sampleTransaction,
      merchant: 'Very Long Business Name That Should Truncate Properly',
      category: 'business',
      amount: 234.56,
      type: 'payment',
    },
  },
};

export const CloudService: Story = {
  args: {
    transaction: {
      ...sampleTransaction,
      merchant: 'AWS Services',
      category: 'cloud software',
      amount: 89.23,
      type: 'subscription',
    },
  },
};

export const Travel: Story = {
  args: {
    transaction: {
      ...sampleTransaction,
      merchant: 'Airline Booking',
      category: 'travel',
      amount: 456.78,
      type: 'purchase',
    },
  },
};

export const Multiple: Story = {
  render: () => (
    <div className="space-y-2 max-w-2xl">
      <TransactionCard transaction={sampleTransaction} />
      <TransactionCard
        transaction={{
          ...sampleTransaction,
          id: 'txn_0987654321',
          merchant: 'Uber Ride',
          category: 'transport',
          amount: 23.45,
          status: 'pending',
          type: 'payment',
        }}
      />
      <TransactionCard
        transaction={{
          ...sampleTransaction,
          id: 'txn_1122334455',
          merchant: 'Netflix Subscription',
          category: 'entertainment',
          amount: 15.99,
          status: 'completed',
          type: 'subscription',
        }}
        isSelected
      />
    </div>
  ),
};

export const MobileView: Story = {
  parameters: {
    viewport: {
      defaultViewport: 'mobile1',
    },
  },
  args: {
    transaction: sampleTransaction,
  },
};
