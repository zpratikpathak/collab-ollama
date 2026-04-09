# collab-ollama

Run [Ollama](https://ollama.com/) on a Google Colab GPU and access it from your local machine via a [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) — no account or configuration required.

This is useful when models run too slow on your local machine, or when you need GPU-accelerated inference for synthetic data generation in large batches.

## Quick Start

Run directly in a Colab cell with [uvx](https://docs.astral.sh/uv/guides/tools/) — no install step needed:

```bash
!uvx collab-ollama
```

Or with a specific model:

```bash
!uvx collab-ollama -m gemma:2b
```

### Alternative: pip install

If you prefer a traditional install:

```bash
!pip install collab-ollama
!collab-ollama
```

### Specifying a Model

By default, `phi3:mini` is pulled and served. Use the `-m` / `--model` flag to choose a different model:

```bash
!uvx collab-ollama --model llama3:8b
!uvx collab-ollama -m gemma:2b
```

Once setup is complete, you'll see output like:

```
Setup is complete!

  Base URL : https://xxxx-xxxxx-xxxxx-xxxxx.trycloudflare.com/v1/
  API Key  : No key required — leave it blank or use any string
  Model    : gemma:2b
```

## Usage

Use the printed **Base URL** and **Model** with any OpenAI-compatible client. No API key is needed — leave it blank or pass any arbitrary string.

### Ollama CLI

On your **local machine**, set `OLLAMA_HOST` to the base URL (without `/v1/`) and use the Ollama CLI as usual. Inference runs on the Colab GPU, but the experience feels local. Make sure you have the [Ollama CLI](https://ollama.com/download) installed locally.

```bash
export OLLAMA_HOST='https://xxxx-xxxxx-xxxxx-xxxxx.trycloudflare.com'
ollama run gemma:2b --verbose
```

You can pull and run any model that fits in the Colab GPU memory:

```bash
ollama pull llama3:8b
ollama run llama3:8b
```

### Python (OpenAI SDK)

Ollama exposes an [OpenAI-compatible API](https://ollama.com/blog/openai-compatibility). Install the SDK and use the **Base URL** directly:

```bash
pip install openai
```

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://xxxx-xxxxx-xxxxx-xxxxx.trycloudflare.com/v1/",
    api_key="ollama",  # any string works, or leave blank
)

response = client.chat.completions.create(
    model="gemma:2b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ],
)
print(response.choices[0].message.content)
```

### Node.js (OpenAI SDK)

Install the SDK:

```bash
npm install openai
```

```javascript
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "https://xxxx-xxxxx-xxxxx-xxxxx.trycloudflare.com/v1/",
  apiKey: "ollama", // any string works, or leave blank
});

const response = await client.chat.completions.create({
  model: "gemma:2b",
  messages: [
    { role: "system", content: "You are a helpful assistant." },
    { role: "user", content: "Hello!" },
  ],
});
console.log(response.choices[0].message.content);
```

## How It Works

1. **Installs Ollama** if not already present.
2. **Installs Cloudflared** if not already present.
3. **Starts `ollama serve`** with `OLLAMA_ORIGINS=*` for broad CORS support.
4. **Pulls the specified model** (default `phi3:mini`).
5. **Opens a Cloudflare quick tunnel** to `localhost:11434` and prints the **Base URL**, **API Key** info, and **Model** name.

## Requirements

- **Colab:** A Google Colab notebook with a GPU runtime.
- **Local machine:** [Ollama CLI](https://ollama.com/download) (for CLI usage), Python with [openai](https://pypi.org/project/openai/), or Node.js with [openai](https://www.npmjs.com/package/openai).

