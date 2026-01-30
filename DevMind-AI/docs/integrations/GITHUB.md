# GitHub Integration

GitHub integration enables PR automation, webhooks, and bot commands.

## Features

| Feature | Requires |
|---------|----------|
| `devmind generate-pr` | GitHub CLI (`gh`) |
| `devmind pr-review` | GitHub token |
| Auto PR review | GitHub App |
| Bot commands | GitHub App |
| Check runs | GitHub App |

## Quick Setup (CLI Only)

For basic CLI features (`generate-pr`, `pr-review`):

```bash
# Install GitHub CLI
brew install gh  # macOS
# or: sudo apt install gh  # Linux

# Authenticate
gh auth login

# Now you can use
devmind generate-pr owner/repo
devmind pr-review owner/repo#123
```

## GitHub Token Setup

For programmatic access without `gh` CLI:

```bash
# Create token at github.com/settings/tokens
# Required scopes: repo, read:user

export GITHUB_TOKEN=ghp_your-token

# Or in .env
echo "GITHUB_TOKEN=ghp_your-token" >> .env
```

## GitHub App Setup (Full Automation)

For automated PR reviews and bot commands, create a GitHub App.

### 1. Create the App

1. Go to github.com/settings/apps
2. Click "New GitHub App"
3. Configure:
   - **Name**: DevMind AI (or your choice)
   - **Homepage URL**: Your deployment URL
   - **Webhook URL**: `https://your-domain/api/v1/webhooks/github`
   - **Webhook secret**: Generate a secure random string

### 2. Set Permissions

| Permission | Access |
|------------|--------|
| Contents | Read |
| Issues | Read & Write |
| Pull requests | Read & Write |
| Checks | Read & Write |
| Metadata | Read |

### 3. Subscribe to Events

- Pull request
- Issue comment
- Check run

### 4. Generate Private Key

1. In app settings, scroll to "Private keys"
2. Click "Generate a private key"
3. Save the `.pem` file to `config/github-app.pem`

### 5. Configure Environment

```bash
# .env
GITHUB_APP_ID=123456
GITHUB_CLIENT_ID=Iv1.abc123
GITHUB_CLIENT_SECRET=your-secret
GITHUB_PRIVATE_KEY_PATH=./config/github-app.pem
GITHUB_WEBHOOK_SECRET=your-webhook-secret
```

### 6. Install the App

1. Go to your app's public page
2. Click "Install"
3. Select repositories to enable

## Webhook Events

### Pull Request Events

```
pull_request.opened     → Triggers auto-review
pull_request.synchronize → Re-reviews on push
pull_request.reopened   → Re-reviews
```

### Bot Commands

Comment on any PR to trigger actions:

```
/devmind review          → Full code review
/devmind review security → Security-focused review
/devmind scan           → Vulnerability scan
/devmind help           → Show available commands
```

## Auto PR Review

When configured, DevMind automatically:

1. Receives webhook on PR open/update
2. Fetches changed files
3. Runs code review
4. Posts results as PR comment
5. Creates check run with status

### Disable Auto Review

For specific repos, set in repository config:

```json
{
  "auto_review": false
}
```

## PR Generation

Generate documentation and create PRs:

```bash
# Basic usage
devmind generate-pr owner/repo

# With options
devmind generate-pr owner/repo \
  --branch docs/ai-assistant-files \
  --title "Add AI coding assistant documentation" \
  --all

# Dry run (no PR created)
devmind generate-pr owner/repo --dry-run
```

### What It Does

1. Clones repository to temp directory
2. Runs `devmind document` on project
3. Creates new branch
4. Commits generated files
5. Pushes and creates PR

## PR Review

Review existing PRs:

```bash
# Review a PR
devmind pr-review owner/repo#123

# Focus on specific area
devmind pr-review owner/repo#123 --focus security

# Output as JSON
devmind pr-review owner/repo#123 --format json
```

## Troubleshooting

**"gh: command not found"**
```bash
# Install GitHub CLI
brew install gh  # macOS
sudo apt install gh  # Linux
```

**"Permission denied"**
- Check token scopes
- Verify app installation
- Check repository access

**"Webhook delivery failed"**
- Verify webhook URL is accessible
- Check webhook secret matches
- Look at github.com/settings/apps → Advanced → Recent Deliveries

**"App not responding to comments"**
- Verify Issue comment event is subscribed
- Check Issues permission is Read & Write
- Look at API server logs

## Rate Limits

| Resource | Limit |
|----------|-------|
| API requests (token) | 5,000/hour |
| API requests (app) | 5,000/hour/installation |
| Webhooks | No limit |

## Security Considerations

- Store private key securely (never commit)
- Use webhook secrets
- Limit app installation to needed repos
- Review app permissions periodically
