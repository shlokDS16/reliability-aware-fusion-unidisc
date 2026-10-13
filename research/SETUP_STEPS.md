# Steps only you can do (checked on this machine, 2026-10-13)

Ordered by when they block work. CLI steps were verified here today; website labels were not
clicked through, so each step gives the direct URL instead of a menu path.

## 1. Free disk space (blocks Gate 4)
C: has 66.7 GB free. Planned footprint: environment about 8 GB, one 8B checkpoint about 16 to
18 GB each (MMaDA-8B-Base, LLaDA-8B-Instruct, Dream-7B), small DLMs under 2 GB, datasets 10 to
20 GB, saved activations up to 50 GB. **Target 150 GB free.** 70 GB is enough to start with one
large model. Model cache will be set to `models/` inside this project so it is easy to delete later.

## 2. Hugging Face login (blocks Gate 4; 2 minutes)
The CLI is installed (`hf`, huggingface-hub 2.2.0) at `C:\Users\Shlok\.local\bin`, which is not on
PATH yet.

```bash
uv tool update-shell
```

Open a new terminal, then:

```bash
hf auth login
```

It offers a browser login, or paste a token created at https://huggingface.co/settings/tokens
(a **Read** token is enough). Do this yourself; do not paste the token into chat. Check with:

```bash
hf auth whoami
```

## 3. Paywalled papers through VIT eGateway (as needed from Gate 1)
Most DLM papers are open on arXiv and OpenReview, so this is needed only for publisher-only
articles. When one comes up I will list the DOIs in `research/sources/WANTED.md`. Log in to
eGateway in your own Chrome, open each DOI through it, and save the PDF into
`research/sources/pdfs/` named `<doi-with-slashes-as-underscores>.pdf`. I never handle the login.

## 4. Python environment (I run this; needs your yes because of the download size)
About 6 to 8 GB: Python 3.12 through `uv`, PyTorch with a CUDA build that supports the RTX 50
series, transformers, bitsandbytes, accelerate, datasets. The exact wheel index is checked against
the PyTorch install page on the day, then locked in `uv.lock`.

## 5. Optional, not blocking
- **Plugin MCP logins** (Exa plugin, GitHub plugin, Hugging Face plugin) need `/mcp` in an
  interactive `claude` terminal. Not required: the Exa connector, `gh` CLI and `hf` CLI already
  cover the same work in this app.
- **Codex plugin** for the independent GPT review at Gates 2, 5 and 8: run `/codex:setup` once.
- **NotebookLM** for the Gemini review: first use opens a browser tab for you to sign in.
- **Broken connectors, unused here:** n8n (endpoint not found), task-master-ai, Telegram, Zoom.
- **Extra usage** is disabled on the Claude plan. With the weekly limit at 29 percent on day one,
  expect this project to need most of two weekly windows; say if another project has priority.
