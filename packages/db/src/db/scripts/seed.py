"""Seed database with sample data"""

import asyncio
import uuid
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import yaml
from sqlalchemy import select

from db.database import SessionLocal
from db.models import (
    AlertRule,
    AlertType,
    CreditCard,
    NotificationMethod,
    Transaction,
    User,
)


async def seed() -> None:
    async with SessionLocal() as session:  # type: AsyncSession
        # Load test users from shared data file
        test_users_file = (
            Path(__file__).parent.parent.parent.parent.parent.parent
            / 'data'
            / 'test_users.yaml'
        )

        try:
            with open(test_users_file) as f:
                test_users = yaml.safe_load(f)
            print(f'📂 Loaded {len(test_users)} test users from {test_users_file.name}')
        except FileNotFoundError:
            print(f'⚠️  Test users file not found at {test_users_file}')
            print('   Using fallback user data')
            test_users = [
                {
                    'email': 'john.doe@example.com',
                    'first_name': 'John',
                    'last_name': 'Doe',
                }
            ]

        # Check if already seeded (check for first user)
        first_user_email = test_users[0]['email']
        existing = await session.execute(
            select(User).where(User.email == first_user_email)
        )
        if existing.scalar_one_or_none():
            print('Database already seeded; skipping.')
            return

        # Create users from test_users.yaml
        created_users = []
        for test_user in test_users:
            user_id = str(uuid.uuid4())
            card_id = str(uuid.uuid4())

            # Create user with all fields from YAML
            user = User(
                id=user_id,
                email=test_user['email'],
                first_name=test_user.get('first_name', test_user['username']),
                last_name=test_user.get('last_name', 'User'),
                phone_number=test_user.get('phone_number', '+1-555-0000'),
                address_street=test_user.get('address_street', ''),
                address_city=test_user.get('address_city', ''),
                address_state=test_user.get('address_state', ''),
                address_zipcode=test_user.get('address_zipcode', ''),
                address_country=test_user.get('address_country', 'US'),
                credit_limit=Decimal(str(test_user.get('credit_limit', '10000.00'))),
                credit_balance=Decimal(str(test_user.get('credit_balance', '0.00'))),
                location_consent_given=test_user.get('location_consent_given', False),
                last_app_location_latitude=test_user.get('last_app_location_latitude'),
                last_app_location_longitude=test_user.get(
                    'last_app_location_longitude'
                ),
                last_app_location_timestamp=datetime.fromisoformat(
                    test_user['last_app_location_timestamp']
                )
                if test_user.get('last_app_location_timestamp')
                else None,
                last_app_location_accuracy=test_user.get('last_app_location_accuracy'),
                last_transaction_latitude=test_user.get('last_transaction_latitude'),
                last_transaction_longitude=test_user.get('last_transaction_longitude'),
                last_transaction_timestamp=datetime.fromisoformat(
                    test_user['last_transaction_timestamp']
                )
                if test_user.get('last_transaction_timestamp')
                else None,
                last_transaction_city=test_user.get('last_transaction_city', ''),
                last_transaction_state=test_user.get('last_transaction_state', ''),
                last_transaction_country=test_user.get(
                    'last_transaction_country', 'US'
                ),
            )
            session.add(user)
            created_users.append(
                {'user_id': user_id, 'card_id': card_id, 'email': test_user['email']}
            )

            # Create a credit card for each user using YAML data
            card = CreditCard(
                id=card_id,
                user_id=user_id,
                card_number=test_user.get('card_number', '0000'),
                card_type=test_user.get('card_type', 'Visa'),
                bank_name=test_user.get('bank_name', 'Example Bank'),
                card_holder_name=f'{test_user.get("first_name", "")} {test_user.get("last_name", "")}'.strip(),
                expiry_month=test_user.get('card_expiry_month', 12),
                expiry_year=test_user.get('card_expiry_year', 2027),
            )
            session.add(card)

        print(f'✅ Created {len(created_users)} users from test data')

        # Create sample transactions and alert rules for the first user only
        # (to avoid cluttering the database with too much test data)
        first_user = created_users[0]
        user_id = first_user['user_id']
        card_id = first_user['card_id']

        txs = [
            Transaction(
                id=str(uuid.uuid4()),
                user_id=user_id,
                credit_card_num=card_id,
                amount=Decimal('89.99'),
                description='Grocery shopping',
                merchant_name='Whole Foods Market',
                merchant_category='Grocery',
                transaction_date=datetime.fromisoformat('2024-01-15T10:30:00+00:00'),
                merchant_city='San Francisco',
                merchant_state='CA',
                merchant_country='US',
                status=None,  # default
            ),
            Transaction(
                id=str(uuid.uuid4()),
                user_id=user_id,
                credit_card_num=card_id,
                amount=Decimal('1299.99'),
                description='Laptop purchase',
                merchant_name='Apple Store',
                merchant_category='Electronics',
                transaction_date=datetime.fromisoformat('2024-01-16T14:45:00+00:00'),
                merchant_city='San Francisco',
                merchant_state='CA',
                merchant_country='US',
            ),
            Transaction(
                id=str(uuid.uuid4()),
                user_id=user_id,
                credit_card_num=card_id,
                amount=Decimal('45.50'),
                description='Dinner',
                merchant_name='Restaurant ABC',
                merchant_category='Dining',
                transaction_date=datetime.fromisoformat('2024-01-17T19:20:00+00:00'),
                merchant_city='San Francisco',
                merchant_state='CA',
                merchant_country='US',
            ),
        ]
        session.add_all(txs)

        rules = [
            AlertRule(
                id=str(uuid.uuid4()),
                user_id=user_id,
                name='High Amount Alert',
                description='Alert for transactions over $1000',
                alert_type=AlertType.AMOUNT_THRESHOLD,
                amount_threshold=Decimal('1000.00'),
                notification_methods=[NotificationMethod.EMAIL, NotificationMethod.SMS],
            ),
            AlertRule(
                id=str(uuid.uuid4()),
                user_id=user_id,
                name='Electronics Purchase Alert',
                description='Alert for all electronics purchases',
                alert_type=AlertType.MERCHANT_CATEGORY,
                merchant_category='Electronics',
                notification_methods=[NotificationMethod.EMAIL],
            ),
            AlertRule(
                id=str(uuid.uuid4()),
                user_id=user_id,
                name='AI Smart Alert',
                description='Smart pattern-based alerts using AI',
                alert_type=AlertType.PATTERN_BASED,
                natural_language_query='Alert me when I spend more than usual on dining in a week',
                notification_methods=[NotificationMethod.PUSH],
            ),
        ]
        session.add_all(rules)

        await session.commit()
        print('Seeded sample user, card, transactions, and rules.')


if __name__ == '__main__':
    asyncio.run(seed())
