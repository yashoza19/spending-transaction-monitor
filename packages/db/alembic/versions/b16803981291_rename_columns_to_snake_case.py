"""rename_columns_to_snake_case

Revision ID: b16803981291
Revises: 1b64d9695755
Create Date: 2025-09-10 17:48:17.102317

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b16803981291'
down_revision = '1b64d9695755'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if specific camelCase columns still exist and need to be renamed
    
    from sqlalchemy import text
    
    connection = op.get_bind()
    
    # Check for specific camelCase columns that need to be renamed
    tables_to_check = {
        'transactions': ['userId', 'creditCardId', 'merchantName', 'merchantCategory', 'transactionDate', 'transactionType', 'merchantCity', 'merchantState', 'merchantCountry', 'authorizationCode', 'referenceNumber', 'createdAt', 'updatedAt'],
        'credit_cards': ['userId', 'cardNumber', 'cardType', 'cardHolderName', 'bankName', 'expiryMonth', 'expiryYear', 'isActive', 'createdAt', 'updatedAt'],
        'alert_rules': ['userId', 'naturalLanguageQuery', 'isActive', 'alertType', 'amountThreshold', 'merchantCategory', 'merchantName', 'notificationMethods', 'triggerCount', 'lastTriggered', 'sqlQuery', 'createdAt', 'updatedAt'],
        'alert_notifications': ['userId', 'alertRuleId', 'transactionId', 'notificationMethod', 'sentAt', 'deliveredAt', 'readAt', 'createdAt', 'updatedAt']
    }
    
    # Check if any camelCase columns exist and collect them
    camel_case_columns = {}
    for table_name, columns in tables_to_check.items():
        camel_case_columns[table_name] = []
        for column in columns:
            result = connection.execute(text(f"""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = '{table_name}' AND column_name = '{column}'
            """))
            if result.fetchone():
                print(f"Found camelCase column {column} in table {table_name}")
                camel_case_columns[table_name].append(column)
    
    # Check if any camelCase columns exist at all
    has_camel_case = any(columns for columns in camel_case_columns.values())
    
    if not has_camel_case:
        print("No camelCase columns found, skipping migration")
        return
    
    # Dynamic migration logic for camelCase to snake_case conversion
    print("Converting camelCase columns to snake_case")
    
    # Define the camelCase to snake_case mapping
    column_mapping = {
        'userId': 'user_id',
        'creditCardId': 'credit_card_id',
        'merchantName': 'merchant_name',
        'merchantCategory': 'merchant_category',
        'transactionDate': 'transaction_date',
        'transactionType': 'transaction_type',
        'merchantCity': 'merchant_city',
        'merchantState': 'merchant_state',
        'merchantCountry': 'merchant_country',
        'authorizationCode': 'authorization_code',
        'referenceNumber': 'reference_number',
        'createdAt': 'created_at',
        'updatedAt': 'updated_at',
        'cardNumber': 'card_number',
        'cardType': 'card_type',
        'cardHolderName': 'card_holder_name',
        'bankName': 'bank_name',
        'expiryMonth': 'expiry_month',
        'expiryYear': 'expiry_year',
        'isActive': 'is_active',
        'naturalLanguageQuery': 'natural_language_query',
        'alertType': 'alert_type',
        'amountThreshold': 'amount_threshold',
        'notificationMethods': 'notification_methods',
        'triggerCount': 'trigger_count',
        'lastTriggered': 'last_triggered',
        'sqlQuery': 'sql_query',
        'alertRuleId': 'alert_rule_id',
        'transactionId': 'transaction_id',
        'notificationMethod': 'notification_method',
        'sentAt': 'sent_at',
        'deliveredAt': 'delivered_at',
        'readAt': 'read_at'
    }
    
    # Rename only the columns that exist in camelCase format
    for table_name, columns in camel_case_columns.items():
        if columns:  # Only process tables that have camelCase columns
            print(f"Processing table {table_name}")
            for camel_column in columns:
                snake_column = column_mapping.get(camel_column)
                if snake_column:
                    print(f"  Renaming {camel_column} to {snake_column}")
                    op.alter_column(table_name, camel_column, new_column_name=snake_column)
                else:
                    print(f"  Warning: No mapping found for column {camel_column}")


def downgrade() -> None:
    # Rename columns back to camelCase in alert_notifications table
    op.alter_column('alert_notifications', 'user_id', new_column_name='userId')
    op.alter_column('alert_notifications', 'alert_rule_id', new_column_name='alertRuleId')
    op.alter_column('alert_notifications', 'transaction_id', new_column_name='transactionId')
    op.alter_column('alert_notifications', 'notification_method', new_column_name='notificationMethod')
    op.alter_column('alert_notifications', 'sent_at', new_column_name='sentAt')
    op.alter_column('alert_notifications', 'delivered_at', new_column_name='deliveredAt')
    op.alter_column('alert_notifications', 'read_at', new_column_name='readAt')
    op.alter_column('alert_notifications', 'created_at', new_column_name='createdAt')
    op.alter_column('alert_notifications', 'updated_at', new_column_name='updatedAt')
    
    # Rename columns back to camelCase in alert_rules table
    op.alter_column('alert_rules', 'user_id', new_column_name='userId')
    op.alter_column('alert_rules', 'natural_language_query', new_column_name='naturalLanguageQuery')
    op.alter_column('alert_rules', 'is_active', new_column_name='isActive')
    op.alter_column('alert_rules', 'alert_type', new_column_name='alertType')
    op.alter_column('alert_rules', 'amount_threshold', new_column_name='amountThreshold')
    op.alter_column('alert_rules', 'merchant_category', new_column_name='merchantCategory')
    op.alter_column('alert_rules', 'merchant_name', new_column_name='merchantName')
    op.alter_column('alert_rules', 'notification_methods', new_column_name='notificationMethods')
    op.alter_column('alert_rules', 'trigger_count', new_column_name='triggerCount')
    op.alter_column('alert_rules', 'last_triggered', new_column_name='lastTriggered')
    op.alter_column('alert_rules', 'sql_query', new_column_name='sqlQuery')
    op.alter_column('alert_rules', 'created_at', new_column_name='createdAt')
    op.alter_column('alert_rules', 'updated_at', new_column_name='updatedAt')
    
    # Rename columns back to camelCase in credit_cards table
    op.alter_column('credit_cards', 'user_id', new_column_name='userId')
    op.alter_column('credit_cards', 'card_number', new_column_name='cardNumber')
    op.alter_column('credit_cards', 'card_type', new_column_name='cardType')
    op.alter_column('credit_cards', 'card_holder_name', new_column_name='cardHolderName')
    op.alter_column('credit_cards', 'bank_name', new_column_name='bankName')
    op.alter_column('credit_cards', 'expiry_month', new_column_name='expiryMonth')
    op.alter_column('credit_cards', 'expiry_year', new_column_name='expiryYear')
    op.alter_column('credit_cards', 'is_active', new_column_name='isActive')
    op.alter_column('credit_cards', 'created_at', new_column_name='createdAt')
    op.alter_column('credit_cards', 'updated_at', new_column_name='updatedAt')
    
    # Rename columns back to camelCase in transactions table
    op.alter_column('transactions', 'user_id', new_column_name='userId')
    op.alter_column('transactions', 'credit_card_id', new_column_name='creditCardId')
    op.alter_column('transactions', 'merchant_name', new_column_name='merchantName')
    op.alter_column('transactions', 'merchant_category', new_column_name='merchantCategory')
    op.alter_column('transactions', 'transaction_date', new_column_name='transactionDate')
    op.alter_column('transactions', 'transaction_type', new_column_name='transactionType')
    op.alter_column('transactions', 'merchant_city', new_column_name='merchantCity')
    op.alter_column('transactions', 'merchant_state', new_column_name='merchantState')
    op.alter_column('transactions', 'merchant_country', new_column_name='merchantCountry')
    op.alter_column('transactions', 'authorization_code', new_column_name='authorizationCode')
    op.alter_column('transactions', 'reference_number', new_column_name='referenceNumber')
    op.alter_column('transactions', 'created_at', new_column_name='createdAt')
    op.alter_column('transactions', 'updated_at', new_column_name='updatedAt')
