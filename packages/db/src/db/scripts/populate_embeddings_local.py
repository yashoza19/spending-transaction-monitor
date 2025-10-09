#!/usr/bin/env python3
"""
Local Embedding Population Script
Generates embeddings using sentence-transformers (all-MiniLM-L6-v2) running locally.
No external services required - fully self-contained.
"""

import asyncio
import sys
from typing import List

from sentence_transformers import SentenceTransformer
from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from db.models import MerchantCategoryEmbedding

# Model configuration
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
EXPECTED_DIMENSIONS = 384

# Canonical categories (matching updated seed_category_data.py from real CSV data)
CANONICAL_CATEGORIES = [
    'dining',
    'grocery',
    'retail',
    'entertainment',
    'fuel',
    'health_fitness',
    'personal_care',
    'travel',
    'home',
    'kids_pets',
    'misc_net',
    'misc_pos',
]


def load_model() -> SentenceTransformer:
    """Load the sentence-transformers model"""
    print(f'🤖 Loading sentence-transformers model: {MODEL_NAME}')
    try:
        model = SentenceTransformer(MODEL_NAME)
        print(f'✅ Successfully loaded model ({EXPECTED_DIMENSIONS} dimensions)')
        return model
    except Exception as e:
        print(f'❌ Failed to load model: {e}')
        print('💡 Tip: Install with: pip install sentence-transformers')
        sys.exit(1)


def generate_embedding(model: SentenceTransformer, text: str) -> List[float]:
    """Generate embedding using sentence-transformers"""
    try:
        # encode returns numpy array, convert to list
        embedding = model.encode(text.lower(), convert_to_tensor=False)
        embedding_list = embedding.tolist()

        if len(embedding_list) != EXPECTED_DIMENSIONS:
            raise ValueError(
                f'Expected {EXPECTED_DIMENSIONS} dimensions, got {len(embedding_list)}'
            )

        return embedding_list

    except Exception as e:
        print(f'❌ Error generating embedding for "{text}": {e}')
        raise


async def clear_existing_embeddings(session: AsyncSession) -> None:
    """Clear existing embeddings for fresh population"""
    print('🧹 Clearing existing embeddings...')
    await session.execute(delete(MerchantCategoryEmbedding))
    await session.commit()
    print('✅ Cleared existing embeddings')


async def update_database_schema(session: AsyncSession) -> None:
    """Update the embedding column to match model dimensions"""
    print(f'🔧 Updating database schema for {EXPECTED_DIMENSIONS} dimensions...')

    try:
        # Drop and recreate the column with correct dimensions
        await session.execute(
            text('ALTER TABLE merchant_category_embeddings DROP COLUMN IF EXISTS embedding')
        )
        await session.execute(
            text(
                f'ALTER TABLE merchant_category_embeddings ADD COLUMN embedding vector({EXPECTED_DIMENSIONS})'
            )
        )
        await session.commit()
        print(f'✅ Updated embedding column to {EXPECTED_DIMENSIONS} dimensions')
    except Exception as e:
        print(f'⚠️  Schema update note: {e}')
        # Column might already be the right size or table might be empty
        await session.rollback()


async def populate_category_embeddings(
    session: AsyncSession, model: SentenceTransformer
) -> None:
    """Generate and store embeddings for all canonical categories"""
    print(f'📊 Generating embeddings for {len(CANONICAL_CATEGORIES)} categories')
    print(f'🤖 Using local model: {MODEL_NAME}')

    successful_embeddings = 0

    for i, category in enumerate(CANONICAL_CATEGORIES, 1):
        print(
            f'  [{i}/{len(CANONICAL_CATEGORIES)}] Generating embedding for "{category}"...'
        )

        try:
            # Generate embedding using local model
            embedding = generate_embedding(model, category)

            # Store in database
            embedding_obj = MerchantCategoryEmbedding(
                category=category, embedding=embedding
            )
            session.add(embedding_obj)
            successful_embeddings += 1

            print(f'    ✅ Generated {len(embedding)}-dimensional embedding')

        except Exception as e:
            print(f'    ❌ Failed to generate embedding for "{category}": {e}')
            continue

    # Commit all embeddings
    await session.commit()
    print(
        f'✅ Successfully generated {successful_embeddings}/{len(CANONICAL_CATEGORIES)} embeddings'
    )


async def validate_embeddings(session: AsyncSession) -> None:
    """Validate that embeddings were stored correctly"""
    print('🔍 Validating stored embeddings...')

    result = await session.execute(select(MerchantCategoryEmbedding))
    embeddings = result.scalars().all()

    print(f'✅ Found {len(embeddings)} embeddings in database')

    # Validate embedding dimensions
    for embedding_obj in embeddings:
        if len(embedding_obj.embedding) != EXPECTED_DIMENSIONS:
            print(
                f'❌ Invalid embedding dimension for "{embedding_obj.category}": {len(embedding_obj.embedding)}'
            )
        else:
            print(
                f'✅ "{embedding_obj.category}" embedding: {len(embedding_obj.embedding)} dimensions ✓'
            )


async def test_semantic_search(
    session: AsyncSession, model: SentenceTransformer
) -> None:
    """Test semantic search functionality using local embeddings"""
    print('🧪 Testing semantic search...')

    test_queries = [
        'food',
        'restaurant',
        'gas station',
        'hotel',
        'computer',
        'netflix',
        'walmart',
        'gym',
    ]

    for query in test_queries:
        try:
            # Generate embedding for test query
            query_embedding = generate_embedding(model, query)

            # Convert to PostgreSQL vector format
            vector_str = '[' + ','.join(map(str, query_embedding)) + ']'

            # Find most similar category using vector distance
            result = await session.execute(
                text(f"""
                SELECT category, embedding <-> '{vector_str}'::vector as distance
                FROM merchant_category_embeddings
                ORDER BY embedding <-> '{vector_str}'::vector
                LIMIT 1
            """)
            )

            row = result.fetchone()
            if row:
                category, distance = row
                print(f'  "{query}" → "{category}" (distance: {distance:.4f})')
            else:
                print(f'  "{query}" → No match found')

        except Exception as e:
            print(f'  "{query}" → Error: {e}')


async def main():
    """Main embedding population function"""
    print('🚀 Starting Local Embedding Population (sentence-transformers)')
    print(f'📊 Will generate embeddings for {len(CANONICAL_CATEGORIES)} categories')
    print(f'🤖 Using model: {MODEL_NAME} ({EXPECTED_DIMENSIONS} dimensions)')
    print()

    # Load the model first
    model = load_model()

    # Get async database session
    db_gen = get_db()
    session = await db_gen.__anext__()

    try:
        await update_database_schema(session)
        await clear_existing_embeddings(session)
        await populate_category_embeddings(session, model)
        await validate_embeddings(session)

        # Optional: Test semantic search if all embeddings were successful
        result = await session.execute(select(MerchantCategoryEmbedding))
        if len(result.scalars().all()) == len(CANONICAL_CATEGORIES):
            await test_semantic_search(session, model)
    finally:
        await session.close()

    print()
    print('🎉 Local embedding population completed successfully!')
    print()
    print('📋 Categories with Embeddings:')
    for category in sorted(CANONICAL_CATEGORIES):
        print(f'  • {category}')
    print()
    print('✨ Benefits of Local Embeddings:')
    print('  ✓ No external service dependencies (Ollama, OpenAI, etc.)')
    print('  ✓ Fully self-contained within the application')
    print('  ✓ Fast inference on CPU')
    print('  ✓ No API costs or rate limits')
    print('  ✓ Works offline')
    print()
    print('🔗 Next steps:')
    print('  1. CategoryNormalizer will use local embeddings automatically')
    print('  2. Test with transaction creation pipeline')
    print('  3. Verify semantic search in queries')

    return 0


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    if exit_code:
        sys.exit(exit_code)

