# Gemini Integration

Google's Gemini is the primary LLM provider for DevMind, handling simple and moderate complexity tasks.

## Why Gemini?

- **Free tier** - 60 requests/minute, sufficient for CLI usage
- **Fast** - Low latency for simple tasks
- **Cost-effective** - Cheaper than Claude/OpenAI for simple tasks
- **Good enough** - Handles style review, documentation, basic analysis well

## Setup

### 1. Get API Key

1. Go to [Google AI Studio](https://aistudio.google.com)
2. Click "Get API key"
3. Create a new key or use existing

### 2. Configure

```bash
# Environment variable
export GOOGLE_API_KEY=your-key-here

# Or in .env file
echo "GOOGLE_API_KEY=your-key" >> .env
```

### 3. Verify

```bash
# Test with a simple command
devmind document . --analyze
```

## Free Tier Limits

| Limit | Value |
|-------|-------|
| Requests per minute | 60 |
| Requests per day | 1,500 |
| Tokens per minute | 32,000 |

These limits are sufficient for normal CLI usage. If you hit limits, wait a minute.

## Model Used

DevMind uses `gemini-3-flash-preview` by default:
- Fast inference
- Good for code understanding
- Lower cost than Pro models

## Tasks Routed to Gemini

| Task | Complexity | Notes |
|------|------------|-------|
| Style review | SIMPLE | Code style, formatting |
| Documentation review | SIMPLE | Doc completeness |
| Project analysis | SIMPLE | Structure detection |
| Documentation generation | MODERATE | AI assistant docs |
| Basic test generation | MODERATE | Simple test cases |

## Configuration Options

In `.devmind.yaml`:

```yaml
llm:
  default_provider: gemini
  gemini:
    model: gemini-3-flash-preview  # or gemini-1.5-pro
    temperature: 0.1
    max_tokens: 4096
```

## Rate Limit Handling

DevMind handles rate limits automatically:
- Retries with exponential backoff
- Falls back to other providers if available

If you consistently hit limits:
1. Wait between commands
2. Add Claude for complex tasks
3. Consider paid tier

## Troubleshooting

**"API key not valid"**
- Verify key at [aistudio.google.com](https://aistudio.google.com)
- Check for extra spaces in environment variable

**"Rate limit exceeded"**
- Wait 60 seconds
- Add Claude for complex tasks

**"Model not found"**
- Update DevMind to latest version
- Check if model is available in your region

## Cost Optimization

Gemini is already cost-effective, but to minimize usage:

```bash
# Use --analyze first (no generation)
devmind document . --analyze

# Generate only needed formats
devmind document . -w -f claude -f copilot

# Avoid --all unless necessary
```
