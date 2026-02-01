# OpenAI Integration

OpenAI serves as an optional fallback provider when Gemini and Claude are unavailable.

## When OpenAI is Used

- Fallback when Gemini rate-limited
- Fallback when Claude unavailable
- Alternative for specific use cases

## Setup

### 1. Get API Key

1. Go to [OpenAI Platform](https://platform.openai.com)
2. Create account (requires credit card)
3. Generate API key in API Keys section

### 2. Configure

```bash
# Environment variable
export OPENAI_API_KEY=sk-your-key

# Or in .env file
echo "OPENAI_API_KEY=sk-your-key" >> .env
```

### 3. Verify

```bash
# OpenAI is used as fallback automatically
# Or force it with config:
devmind review src/main.py
```

## Pricing

| Model | Input | Output |
|-------|-------|--------|
| gpt-4o | $2.50/M tokens | $10/M tokens |
| gpt-4o-mini | $0.15/M tokens | $0.60/M tokens |

## Model Used

Default: `gpt-4o-mini` for cost efficiency
- Good for code tasks
- Lower cost than GPT-4
- Fast inference

## Configuration Options

In `.devmind.yaml`:

```yaml
llm:
  openai:
    model: gpt-4o-mini
    temperature: 0.1
    max_tokens: 4096
```

## Routing Priority

DevMind checks providers in this order:

1. **Gemini** - Simple/moderate tasks
2. **Claude** - Complex tasks
3. **OpenAI** - Fallback for any

If you only have OpenAI:

```bash
# Only OpenAI configured
export OPENAI_API_KEY=your-key

# All tasks route to OpenAI
devmind review src/
```

## Rate Limits

| Tier | Requests/min | Tokens/min |
|------|--------------|------------|
| Tier 1 | 500 | 30,000 |
| Tier 2 | 5,000 | 450,000 |
| Tier 3+ | Higher | Higher |

## Troubleshooting

**"Invalid API key"**
- Key format: `sk-...`
- Check for extra spaces
- Verify at platform.openai.com

**"Insufficient quota"**
- Add payment method
- Check billing settings

**"Rate limit exceeded"**
- Wait and retry
- Check tier limits

## Recommendation

OpenAI works well as a fallback but isn't the primary recommendation:

- **Gemini** - Better free tier
- **Claude** - Better for complex reasoning
- **OpenAI** - Good fallback, reliable

For most users: Use Gemini + Claude, add OpenAI for redundancy.
