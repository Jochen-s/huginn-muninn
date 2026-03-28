# Huginn & Muninn: Setup Guide

A step-by-step guide to running Huginn & Muninn on your own computer.
No programming experience required.

---

## What You'll Need

- A computer (Windows, Mac, or Linux)
- About 30 minutes for initial setup
- An internet connection (for downloading software)
- About 8 GB of free disk space (for the AI model)

## What You'll Get

A private, local fact-checking tool that:
- Analyzes claims through a 6-agent pipeline
- Names the manipulation techniques being used ("the magic trick reveal")
- Presents both the conspiracy narrative AND the scientific explanation
- Generates Socratic dialogue for constructive conversations
- Never sends your data to anyone

---

## Option A: Easiest Setup (Docker, recommended)

Docker packages everything into a container so you don't have to install
Python, dependencies, or configure anything manually.

### Step 1: Install Docker Desktop

1. Go to https://www.docker.com/products/docker-desktop/
2. Download Docker Desktop for your operating system
3. Run the installer and follow the prompts
4. After installation, open Docker Desktop and wait for it to start
   (you'll see a green "Running" status in the bottom left)

### Step 2: Install Ollama (the AI brain)

Ollama runs AI models locally on your computer. Your data stays private.

1. Go to https://ollama.ai
2. Click "Download" and install for your operating system
3. After installation, open a terminal:
   - **Windows**: Press `Win + R`, type `cmd`, press Enter
   - **Mac**: Open "Terminal" from Applications > Utilities
   - **Linux**: Open your terminal application

4. Pull a model (this downloads about 6 GB, one-time only):
   ```
   ollama pull qwen3.5:9b
   ```
   Wait for the download to complete. This may take 10-20 minutes
   depending on your internet speed.

5. Verify it works:
   ```
   ollama run qwen3.5:9b "Hello, are you working?"
   ```
   You should see a response. Press Ctrl+D to exit.

### Step 3: Get Huginn & Muninn

1. Download the project:
   - Go to https://github.com/Jochen-s/huginn-muninn
   - Click the green "Code" button
   - Click "Download ZIP"
   - Extract the ZIP to a folder you'll remember (e.g., your Desktop)

   OR if you have Git installed:
   ```
   git clone https://github.com/Jochen-s/huginn-muninn.git
   ```

2. Open a terminal and navigate to the folder:
   ```
   cd huginn-muninn
   ```

### Step 4: Configure

1. Copy the example configuration:
   ```
   cp .env.example .env
   ```

2. The default settings work for most setups. If Ollama is running
   on the same computer, you don't need to change anything.

   If Ollama is on a different machine, edit `.env` and change:
   ```
   OLLAMA_BASE_URL=http://YOUR_OLLAMA_IP:11434
   ```

### Step 5: Start

```
docker compose up -d
```

Wait about 30 seconds. Then open your browser to:

```
http://localhost:8000
```

You should see the Huginn & Muninn web interface.

### Step 6: Try It

1. In the web interface, type a claim. For example:
   ```
   The government is spraying chemicals from planes to control the population.
   ```

2. Click "Analyze" (or press Enter)

3. Wait 30-90 seconds for the full 6-agent pipeline to run

4. Read the results:
   - **Universal Needs**: What human concerns drive this belief
   - **Scientific Consensus**: What the science actually says
   - **Name the Trick**: Which manipulation techniques are being used
   - **Socratic Dialogue**: How to have a constructive conversation
   - **Common Ground**: What both sides actually agree on

### To Stop

```
docker compose down
```

### To Restart Later

```
docker compose up -d
```

---

## Option B: Command Line Setup (for slightly technical users)

If you prefer not to use Docker, you can install directly.

### Prerequisites

1. **Python 3.12 or newer**
   - Download from https://www.python.org/downloads/
   - During installation, CHECK the box "Add Python to PATH"
   - Verify: open a terminal and type `python --version`

2. **Ollama** (same as Step 2 above)

### Install

```bash
# Navigate to the project folder
cd huginn-muninn

# Install the project (this also installs all dependencies)
pip install -e .

# Verify installation
huginn --version
```

### Use: Quick Check (10 seconds)

```bash
huginn check "Vaccines cause autism in children"
```

This runs Method 1: a fast two-pass analysis. Good for a quick assessment.

### Use: Full Analysis (30-90 seconds)

```bash
huginn analyze "Vaccines cause autism in children"
```

This runs Method 2: the full 6-agent pipeline with decomposition, origin
tracing, actor mapping, technique classification, bridge building, and
adversarial audit.

### Use: JSON Output (for developers)

```bash
huginn analyze "claim text" --json-output
```

### Use: Different Model

```bash
# Pull a different model first
ollama pull llama3.1:8b

# Use it
huginn check "claim text" --model llama3.1:8b
```

### Use: API Server

```bash
# Start the server
uvicorn huginn_muninn.api:app --host 0.0.0.0 --port 8000

# Then use the web interface at http://localhost:8000
# Or call the API directly:
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"claim": "claim text here"}'
```

---

## Option C: Using with Claude Code (highest quality, requires subscription)

Claude Code can run Huginn & Muninn using Opus as the AI backend,
producing the highest quality results.

### Prerequisites

1. Claude Code installed (https://claude.ai/code)
2. Active Claude subscription (Pro or Team)
3. The project cloned locally

### Use

1. Open Claude Code in the huginn-muninn directory
2. Ask Claude to analyze a claim:
   ```
   Run the full Huginn & Muninn 6-agent pipeline on this claim:
   "The government is spraying chemicals from planes to control the population."
   Write the result to tests/results/
   ```
3. Claude will execute each agent in sequence using Opus as the backend

This produces the highest quality results because Opus has deeper
reasoning capabilities than smaller local models.

---

## Choosing a Model

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| qwen3.5:9b | ~6 GB | Fast | Good | Daily use, quick checks |
| llama3.1:8b | ~5 GB | Fast | Good | Alternative to Qwen |
| qwen3.5:32b | ~20 GB | Slower | Better | When you want more depth |
| Claude Opus (via Claude Code) | Cloud | Slower | Best | Publication-quality analysis |

For most users, `qwen3.5:9b` is the right choice. It runs on any
modern laptop and produces solid results.

---

## Troubleshooting

**"Connection refused" when starting**
- Make sure Ollama is running: `ollama serve`
- Make sure Docker Desktop is running (for Option A)

**"Model not found"**
- Pull the model first: `ollama pull qwen3.5:9b`

**Analysis takes very long (5+ minutes)**
- Smaller models are faster. Try `qwen3.5:9b` if using a larger model.
- Check your system resources (the model needs ~8 GB RAM)

**Docker won't start**
- On Windows: make sure WSL 2 is enabled (Docker Desktop will prompt you)
- On Mac: make sure you gave Docker permission in System Settings

**Results seem low quality**
- Larger models produce better results (try `qwen3.5:32b`)
- Claude Code with Opus produces the best results

---

## What the Results Mean

Each analysis produces several components:

| Component | What It Tells You |
|-----------|------------------|
| **Universal Needs** | The human concerns driving belief in this claim (safety, autonomy, fairness) |
| **Scientific Consensus** | What established science or institutional evidence says, with equal depth |
| **Name the Trick** | Which manipulation techniques are being used, explained like revealing a magic trick |
| **Inferential Gap** | Where documented facts end and unsupported leaps begin |
| **Socratic Dialogue** | A 3-round conversation script for talking about this with someone who believes it |
| **Common Ground** | What both sides actually agree on, with data |
| **Audit** | An adversarial review of the analysis itself, checking for bias and errors |

---

## Privacy

Everything runs on your computer. No data is sent to any server
(unless you choose Option C with Claude Code, which uses Anthropic's API).
Your claims, your analysis, your data. Nobody else sees it.
