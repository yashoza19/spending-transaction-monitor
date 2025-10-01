import { useForm } from '@tanstack/react-form';
import {
  CreateTransaction,
  CreateTransactionSchema,
  TRANSACTION_CATEGORIES,
  ACCOUNT_TYPES,
} from '../../schemas/transaction';
import { Button } from '../atoms/button/button';
import { Input } from '../atoms/input/input';
import { Label } from '../atoms/label/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../atoms/select/select';
import { Textarea } from '../atoms/textarea/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../atoms/dialog/dialog';
import { useState, useEffect } from 'react';
import { useCreateTransaction } from '../../hooks/transactions';
import { PlusIcon } from 'lucide-react';
import { toast } from 'sonner';

export function AddTransactionDialog() {
  const [open, setOpen] = useState(false);
  const createTransactionMutation = useCreateTransaction();

  const form = useForm({
    defaultValues: {
      date: new Date().toISOString().split('T')[0], // Today's date in YYYY-MM-DD format
      description: '',
      amount: 0,
      category: '',
      account: '',
      type: 'debit',
      merchant: '',
      tags: [] as string[],
      notes: '',
    } as CreateTransaction,
    onSubmit: async ({ value }) => {
      // Use the mutation to create the transaction
      createTransactionMutation.mutate(value);
    },
    validators: {
      onSubmit: CreateTransactionSchema,
    },
  });

  const handleCancel = () => {
    setOpen(false);
    form.reset();
  };

  // Handle mutation success/error with useEffect
  useEffect(() => {
    if (createTransactionMutation.isSuccess) {
      setOpen(false);
      form.reset();
      toast.success('Transaction created successfully');
    }
  }, [createTransactionMutation.isSuccess, form]);

  useEffect(() => {
    if (createTransactionMutation.isError) {
      console.error('Failed to create transaction:', createTransactionMutation.error);
      toast.error(
        createTransactionMutation.error?.message || 'Failed to create transaction',
      );
    }
  }, [createTransactionMutation.isError, createTransactionMutation.error]);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="flex items-center gap-2 w-full md:w-auto">
          <PlusIcon className="h-4 w-4" />
          Add Transaction
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Add New Transaction</DialogTitle>
          <DialogDescription>
            Enter the details for the new transaction below.
          </DialogDescription>
        </DialogHeader>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            e.stopPropagation();
            form.handleSubmit();
          }}
          className="space-y-4"
        >
          <div className="grid grid-cols-2 gap-4">
            {/* Date */}
            <form.Field
              name="date"
              validators={{
                onChange: CreateTransactionSchema.shape.date,
              }}
            >
              {(field) => (
                <div className="space-y-2">
                  <Label htmlFor={field.name}>Date *</Label>
                  <Input
                    id={field.name}
                    type="date"
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                  />
                  {field.state.meta.errors.length > 0 && (
                    <p className="text-sm text-destructive">
                      {field.state.meta.errors[0]?.message.toString()}
                    </p>
                  )}
                </div>
              )}
            </form.Field>

            {/* Amount */}
            <form.Field
              name="amount"
              validators={{
                onChange: CreateTransactionSchema.shape.amount,
              }}
            >
              {(field) => (
                <div className="space-y-2">
                  <Label htmlFor={field.name}>Amount *</Label>
                  <Input
                    id={field.name}
                    type="number"
                    step="0.01"
                    min="0"
                    placeholder="0.00"
                    value={field.state.value || ''}
                    onChange={(e) =>
                      field.handleChange(parseFloat(e.target.value) || 0)
                    }
                    onBlur={field.handleBlur}
                  />
                  {field.state.meta.errors.length > 0 && (
                    <p className="text-sm text-destructive">
                      {field.state.meta.errors[0]?.message.toString()}
                    </p>
                  )}
                </div>
              )}
            </form.Field>
          </div>

          {/* Description */}
          <form.Field
            name="description"
            validators={{
              onChange: CreateTransactionSchema.shape.description,
            }}
          >
            {(field) => (
              <div className="space-y-2">
                <Label htmlFor={field.name}>Description *</Label>
                <Input
                  id={field.name}
                  placeholder="Enter transaction description"
                  value={field.state.value}
                  onChange={(e) => field.handleChange(e.target.value)}
                  onBlur={field.handleBlur}
                />
                {field.state.meta.errors.length > 0 && (
                  <p className="text-sm text-destructive">
                    {field.state.meta.errors[0]?.message.toString()}
                  </p>
                )}
              </div>
            )}
          </form.Field>

          <div className="grid grid-cols-2 gap-4">
            {/* Category */}
            <form.Field
              name="category"
              validators={{
                onChange: CreateTransactionSchema.shape.category,
              }}
            >
              {(field) => (
                <div className="space-y-2">
                  <Label htmlFor={field.name}>Category *</Label>
                  <Select
                    value={field.state.value}
                    onValueChange={(value) => field.handleChange(value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      {TRANSACTION_CATEGORIES.map((category) => (
                        <SelectItem key={category} value={category}>
                          {category}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {field.state.meta.errors.length > 0 && (
                    <p className="text-sm text-destructive">
                      {field.state.meta.errors[0]?.message.toString()}
                    </p>
                  )}
                </div>
              )}
            </form.Field>

            {/* Account */}
            <form.Field
              name="account"
              validators={{
                onChange: CreateTransactionSchema.shape.account,
              }}
            >
              {(field) => (
                <div className="space-y-2">
                  <Label htmlFor={field.name}>Account *</Label>
                  <Select
                    value={field.state.value}
                    onValueChange={(value) => field.handleChange(value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select account" />
                    </SelectTrigger>
                    <SelectContent>
                      {ACCOUNT_TYPES.map((account) => (
                        <SelectItem key={account} value={account}>
                          {account}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {field.state.meta.errors.length > 0 && (
                    <p className="text-sm text-destructive">
                      {field.state.meta.errors[0]?.message.toString()}
                    </p>
                  )}
                </div>
              )}
            </form.Field>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {/* Type */}
            <form.Field
              name="type"
              validators={{
                onChange: CreateTransactionSchema.shape.type,
              }}
            >
              {(field) => (
                <div className="space-y-2">
                  <Label htmlFor={field.name}>Type *</Label>
                  <Select
                    value={field.state.value}
                    onValueChange={(value) =>
                      field.handleChange(value as 'debit' | 'credit')
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="debit">Debit</SelectItem>
                      <SelectItem value="credit">Credit</SelectItem>
                    </SelectContent>
                  </Select>
                  {field.state.meta.errors.length > 0 && (
                    <p className="text-sm text-destructive">
                      {field.state.meta.errors[0]?.message.toString()}
                    </p>
                  )}
                </div>
              )}
            </form.Field>

            {/* Merchant */}
            <form.Field
              name="merchant"
              validators={{
                onChange: CreateTransactionSchema.shape.merchant,
              }}
            >
              {(field) => (
                <div className="space-y-2">
                  <Label htmlFor={field.name}>Merchant</Label>
                  <Input
                    id={field.name}
                    placeholder="Enter merchant name"
                    value={field.state.value || ''}
                    onChange={(e) => field.handleChange(e.target.value || '')}
                    onBlur={field.handleBlur}
                  />
                  {field.state.meta.errors.length > 0 && (
                    <p className="text-sm text-destructive">
                      {field.state.meta.errors[0]?.message.toString()}
                    </p>
                  )}
                </div>
              )}
            </form.Field>
          </div>

          {/* Notes */}
          <form.Field
            name="notes"
            validators={{
              onChange: CreateTransactionSchema.shape.notes,
            }}
          >
            {(field) => (
              <div className="space-y-2">
                <Label htmlFor={field.name}>Notes</Label>
                <Textarea
                  id={field.name}
                  placeholder="Additional notes (optional)"
                  value={field.state.value || ''}
                  onChange={(e) => field.handleChange(e.target.value || '')}
                  onBlur={field.handleBlur}
                  rows={3}
                />
                {field.state.meta.errors.length > 0 && (
                  <p className="text-sm text-destructive">
                    {field.state.meta.errors[0]?.message.toString()}
                  </p>
                )}
              </div>
            )}
          </form.Field>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleCancel}
              disabled={createTransactionMutation.isPending}
            >
              Cancel
            </Button>
            <form.Subscribe selector={(state) => [state.canSubmit]}>
              {([canSubmit]) => (
                <Button
                  type="submit"
                  disabled={!canSubmit || createTransactionMutation.isPending}
                >
                  {createTransactionMutation.isPending
                    ? 'Adding...'
                    : 'Add Transaction'}
                </Button>
              )}
            </form.Subscribe>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
