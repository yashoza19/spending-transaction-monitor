# Embedding Service Documentation

## Overview

The Embedding Service provides a unified interface for generating vector embeddings used in category normalization and semantic search. This service has been updated to use **local, self-contained embeddings** via `sentence-transformers`, eliminating the need for external services like Ollama or OpenAI.

## Architecture

### Provider Pattern

The service follows a provider pattern similar to the LLM service, allowing for multiple embedding backends:

```python
EmbeddingProvider (Abstract Base Class)
├── SentenceTransformerEmbeddingProvider (Default - Local)
├── OllamaEmbeddingProvider (Deprecated)
├── OpenAIEmbeddingProvider
└── LlamaStackEmbeddingProvider (Future)
```

## Local Embedding Provider (Recommended)

### SentenceTransformerEmbeddingProvider

**Key Benefits:**
- ✅ **Zero External Dependencies**: Runs entirely within the application
- ✅ **No API Costs**: No OpenAI or other API charges
- ✅ **Offline Capable**: Works without internet connection
- ✅ **Fast Inference**: Optimized for CPU, ~50-100ms per embedding
- ✅ **Consistent Results**: Deterministic outputs, no rate limiting
- ✅ **Privacy**: Data never leaves your infrastructure

**Model:** `sentence-transformers/all-MiniLM-L6-v2`
- 384 dimensions
- 22.7M parameters
- Optimized for semantic similarity
- Excellent performance on category matching tasks

### Configuration

```python
# config.py
EMBEDDING_PROVIDER = 'local'  # Default
EMBEDDING_MODEL = 'all-minilm'  # Maps to all-MiniLM-L6-v2
EMBEDDING_DIMENSIONS = 384
```

### Environment Variables

```bash
# .env
EMBEDDING_PROVIDER=local  # Options: local, openai, llamastack, ollama (deprecated)
EMBEDDING_MODEL=all-minilm
EMBEDDING_DIMENSIONS=384
```

## Usage

### Basic Usage

```python
from services.embedding_service import embedding_service

# Generate embedding for a category
embedding = await embedding_service.get_embedding("restaurant")
# Returns: List[float] with 384 dimensions

# Check dimensions
dims = embedding_service.get_dimensions()
# Returns: 384
```

### Integration with CategoryNormalizer

```python
from services.category_normalizer import CategoryNormalizer

# Automatically uses configured embedding provider
normalized = await CategoryNormalizer.normalize(session, "5812")
# Returns: "dining"
```

## Provider Comparison

| Provider | External Service | API Cost | Offline | Latency | Dimensions |
|----------|-----------------|----------|---------|---------|------------|
| **local** (sentence-transformers) | ❌ No | ✅ Free | ✅ Yes | ~50-100ms | 384 |
| ollama | ⚠️ Yes (self-hosted) | ✅ Free | ⚠️ If running | ~100-200ms | 384 |
| openai | ✅ Yes | ❌ Paid | ❌ No | ~200-500ms | 1536 |
| llamastack | ⚠️ Yes (self-hosted) | ✅ Free | ⚠️ If running | ~100-200ms | Variable |

## Migration from Ollama

If you're migrating from the Ollama provider:

1. **Install Dependencies**:
   ```bash
   cd packages/api
   uv sync  # Installs sentence-transformers automatically
   ```

2. **Update Configuration**:
   ```bash
   # Change in .env or config
   EMBEDDING_PROVIDER=local  # Previously: ollama
   ```

3. **Regenerate Embeddings**:
   ```bash
   python packages/db/src/db/scripts/populate_embeddings_local.py
   ```

4. **No Code Changes Required**: The CategoryNormalizer and other services will automatically use the new provider.

## Performance Considerations

### First Load
- The model (~90MB) downloads automatically on first use
- Cached in `~/.cache/huggingface/` for subsequent runs
- Initial load time: ~2-5 seconds

### Inference
- CPU optimized: ~50-100ms per embedding
- Batch processing supported for efficiency
- No network latency or rate limits

### Memory
- Model footprint: ~90MB
- Per-embedding: ~1.5KB (384 floats)
- Lightweight enough for containerized deployments

## Advanced Configuration

### Custom Models

You can use other sentence-transformers models:

```python
# config.py
EMBEDDING_MODEL = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
EMBEDDING_DIMENSIONS = 384

# Or for better quality (but slower):
EMBEDDING_MODEL = 'sentence-transformers/all-mpnet-base-v2'
EMBEDDING_DIMENSIONS = 768
```

### Async Optimization

For high-throughput scenarios, consider using `asyncio.to_thread` (Python 3.9+):

```python
import asyncio
from sentence_transformers import SentenceTransformer

async def get_embedding(text: str):
    return await asyncio.to_thread(model.encode, text)
```

## Troubleshooting

### ImportError: sentence-transformers not found

```bash
cd packages/api
uv add sentence-transformers torch
uv sync
```

### Model Download Fails

Check your internet connection on first run. The model will be cached locally after the first successful download.

### Different Dimensions Than Expected

Ensure `EMBEDDING_DIMENSIONS` matches your model:
- all-MiniLM-L6-v2: 384
- all-mpnet-base-v2: 768
- text-embedding-3-small (OpenAI): 1536

## Testing

Run the test suite:

```bash
# Test embedding service
pytest packages/api/tests/test_embedding_service.py

# Test with category normalization
python packages/db/src/db/scripts/populate_embeddings_local.py
```

## Future Enhancements

1. **Model Optimization**: Consider ONNX runtime for faster inference
2. **Batch Processing**: Add batch embedding support for bulk operations
3. **Caching**: Implement embedding cache for frequently used terms
4. **Monitoring**: Add metrics for embedding generation performance

## References

- [sentence-transformers Documentation](https://www.sbert.net/)
- [all-MiniLM-L6-v2 Model Card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)

---

*Last Updated: PR #78 - Local Embedding Implementation*

