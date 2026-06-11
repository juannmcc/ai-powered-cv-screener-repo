cat > docs/providers.md << 'EOF'
# Provider Setup Guide

This project supports multiple LLM and image generation providers.
Configure your active providers in `backend/.env`.

---

## LLM Providers (text generation + embeddings)

### Ollama (recommended — free, local)
No API key needed. Runs models locally on your machine.

**Setup:**
```bash
# Mac
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download installer from https://ollama.com/download
```

```bash
ollama serve          # start server (background)
ollama pull llama3.2
ollama pull nomic-embed-text
```

```env
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
EMBED_MODEL=nomic-embed-text
OLLAMA_BASE_URL=http://localhost:11434
```

---

### Google AI Studio / Gemini (free tier — region restricted)
Free up to quota limits. **Not available in Spain and some EU regions.**
Requires Google account. No credit card for free tier.

**Setup:**
1. Go to https://aistudio.google.com/apikey
2. Create API key in a new project
3. Verify with: `uv run check-providers`

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
```

> Note: If you see `limit: 0` errors, your region is blocked on the free tier.
> You'll need to enable billing on your Google Cloud project to bypass this.
> Minimum cost: pay-as-you-go, ~$0.30 per 1M tokens (Gemini 2.0 Flash).

---

### OpenRouter (free tier available)
Access to many models including free ones (Llama, Mistral, Gemma).
Free tier has upstream rate limits — may be saturated during peak hours.

**Setup:**
1. Go to https://openrouter.ai and create account (no credit card)
2. Settings → Keys → Create key
3. For reliable use, add $5 minimum credit

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key_here
```

> Free models: `meta-llama/llama-3.3-70b-instruct:free`, `google/gemma-4-26b-a4b:free`
> Paid models (recommended): `google/gemini-2.0-flash-001` (~$0.10/1M tokens)

---

## Image Generation Providers

### Cloudflare Workers AI (recommended — free)
Generates real AI photos using FLUX. Free tier: 10,000 requests/day.
Requires free Cloudflare account. No credit card needed.

**Setup:**
1. Create free account at https://cloudflare.com
2. Go to **Workers & Pages** → note your **Account ID** (bottom right)
3. Go to **My Profile** → **API Tokens** → **Create Token**
4. Use template **"Workers AI"** or add permission `Workers AI: Read`
5. Copy the generated token

```env
IMAGE_PROVIDER=cloudflare
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_API_TOKEN=your_token
```

**Validate before use:**
```bash
curl -X POST \
  "https://api.cloudflare.com/client/v4/accounts/YOUR_ACCOUNT_ID/ai/run/@cf/black-forest-labs/flux-1-schnell" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "professional headshot portrait"}' \
  --output test.jpg
```
Note: response is JSON with base64-encoded image, not raw binary.

---

### Placeholder / Initials avatar (fallback — no setup required)
Generates colored avatar with candidate initials. No API, no internet, no limits.
Used automatically when `IMAGE_PROVIDER=placeholder` or when Cloudflare fails.

```env
IMAGE_PROVIDER=placeholder
```

---

## Quick reference

| Provider | Type | Cost | Requires |
|---|---|---|---|
| Ollama | LLM + Embeddings | Free | Local install |
| Gemini | LLM + Embeddings | Free (region limited) | Google account |
| OpenRouter | LLM | Free tier / pay-as-you-go | Account + optional credits |
| Cloudflare Workers AI | Image generation | Free (10k/day) | Free CF account |
| Placeholder | Image generation | Free | Nothing |
EOF