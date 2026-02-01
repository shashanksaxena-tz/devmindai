# Qdrant Setup

Qdrant provides vector search capabilities for semantic queries and RAG.

## What Qdrant Enables

| Feature | Description |
|---------|-------------|
| Semantic code search | Find similar code patterns |
| ADR indexing | Search architecture decisions by meaning |
| Documentation search | Natural language queries |
| Similar vulnerability search | Find related CVEs |
| RAG enhancement | Better context for LLM queries |

## Quick Setup (Docker)

```bash
# Using docker-compose (recommended)
docker-compose up -d qdrant

# Or standalone
docker run -d \
  --name devmind-qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v qdrant_data:/qdrant/storage \
  qdrant/qdrant
```

## Configuration

Set the connection URL:

```bash
# Environment variable
export QDRANT_URL=http://localhost:6333

# Or in .env
QDRANT_URL=http://localhost:6333
```

## Collections

DevMind creates these vector collections:

| Collection | Purpose | Dimensions |
|------------|---------|------------|
| `code_embeddings` | Code snippets | 1536 |
| `doc_embeddings` | Documentation | 1536 |
| `adr_embeddings` | Architecture decisions | 1536 |
| `vuln_embeddings` | Vulnerability descriptions | 1536 |

## Use Cases

### Semantic Code Search

```python
# Find code similar to a query
results = qdrant.search(
    collection="code_embeddings",
    query_vector=embed("authentication middleware"),
    limit=10
)
```

### ADR Search

```python
# Find relevant architecture decisions
results = qdrant.search(
    collection="adr_embeddings",
    query_vector=embed("how do we handle database migrations?"),
    limit=5
)
```

### Similar Vulnerabilities

```python
# Find similar CVEs
results = qdrant.search(
    collection="vuln_embeddings",
    query_vector=embed("SQL injection in user input"),
    limit=10
)
```

## Indexing Content

### Index Code Files

```python
from src.integrations.qdrant import QdrantClient

client = QdrantClient(QDRANT_URL)
await client.index_code_file(
    file_path="src/auth.py",
    content=code_content,
    metadata={"language": "python", "repo": "devmind"}
)
```

### Index ADRs

The ADR Recorder agent automatically indexes decisions:

```bash
# Record and index an ADR
devmind adr record "Use PostgreSQL for persistence"
```

## Web Dashboard

Qdrant provides a web UI:

```
http://localhost:6333/dashboard
```

Features:
- View collections
- Browse vectors
- Run search queries
- Monitor performance

## Managed Services

### Qdrant Cloud

1. Sign up at [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create cluster
3. Get API key and URL

```bash
QDRANT_URL=https://xxx.qdrant.io:6333
QDRANT_API_KEY=your-api-key
```

## Performance Tuning

### Collection Configuration

```python
# For large collections
qdrant.create_collection(
    collection_name="code_embeddings",
    vectors_config={
        "size": 1536,
        "distance": "Cosine",
    },
    hnsw_config={
        "m": 16,
        "ef_construct": 100,
    }
)
```

### Memory Usage

Qdrant loads vectors into memory for fast search:

| Vectors | Approximate RAM |
|---------|-----------------|
| 100K | ~500MB |
| 1M | ~5GB |
| 10M | ~50GB |

### Disk Mode

For large datasets, use disk-based mode:

```yaml
# qdrant config
storage:
  on_disk: true
```

## Embedding Models

DevMind uses OpenAI's `text-embedding-3-small` by default:
- 1536 dimensions
- Good for code and text
- Requires `OPENAI_API_KEY`

Alternative (local, no API key):

```yaml
embeddings:
  model: sentence-transformers/all-MiniLM-L6-v2
  dimensions: 384
```

## Troubleshooting

**"Connection refused"**
```bash
# Check Qdrant is running
curl http://localhost:6333/health

# Check Docker
docker-compose ps qdrant
```

**"Collection not found"**
```python
# Create collections
from src.integrations.qdrant import init_collections
await init_collections()
```

**"Vector dimension mismatch"**
- Ensure embedding model matches collection configuration
- Delete and recreate collection if needed

**"Out of memory"**
- Enable disk storage
- Reduce HNSW parameters
- Use quantization

## Security Considerations

- Use API key in production
- Don't expose ports externally
- Regular backups of storage volume

```bash
# With API key
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your-api-key
```

## Without Qdrant

If you don't need semantic search:
- Skip Qdrant entirely
- Core CLI features work without it
- ADR recording works (files only, no search)
- No similarity search capabilities
