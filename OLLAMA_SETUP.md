# Ollama Setup for CityPulse

This guide helps you set up local AI inference using Ollama instead of OpenAI APIs.

## Quick Setup

### 1. Automated Setup (Recommended)

Run the automated setup script:

```bash
./setup_ollama.sh
```

This script will:
- Install Ollama for your platform (macOS/Linux)
- Start the Ollama service
- Download required models (~3-4 GB total)
- Verify the installation

### 2. Manual Setup

If you prefer manual installation:

#### Install Ollama

**macOS:**
```bash
# Via Homebrew
brew install ollama

# Or via curl
curl -fsSL https://ollama.ai/install.sh | sh
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Start Ollama Service

```bash
# Start Ollama server
ollama serve
```

#### Download Required Models

```bash
# LLM for text generation (~2GB)
ollama pull llama3.2:3b

# Embedding model (~274MB)
ollama pull nomic-embed-text
```

## Model Information

### Primary Models

| Model | Size | Purpose | Performance |
|-------|------|---------|-------------|
| `llama3.2:3b` | ~2GB | Text generation (titles, tags, summaries) | Fast, good quality |
| `nomic-embed-text` | ~274MB | Text embeddings for search | High quality, 768 dimensions |

### Alternative Models

If you need different performance characteristics:

**Faster/Smaller LLM:**
```bash
ollama pull gemma2:2b    # ~1.4GB, faster inference
```

**Higher Quality LLM:**
```bash
ollama pull qwen2.5:7b   # ~4.4GB, better quality
```

**Different Embedding Model:**
```bash
ollama pull mxbai-embed-large  # ~670MB, 1024 dimensions
```

## Configuration

### Environment Variables

The following environment variables control Ollama integration:

```bash
# AI Providers
TRANSCRIBE_PROVIDER=ollama     # Use local Whisper for transcription
EMBEDDINGS_PROVIDER=ollama     # Use Ollama for embeddings
LLM_PROVIDER=ollama           # Use Ollama for text generation

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434    # Ollama server address
OLLAMA_LLM_MODEL=llama3.2:3b         # LLM model name
OLLAMA_EMBEDDING_MODEL=nomic-embed-text  # Embedding model name
```

### Using Different Models

To use different models, update your `.env` file:

```bash
# For faster inference
OLLAMA_LLM_MODEL=gemma2:2b

# For better embedding quality
OLLAMA_EMBEDDING_MODEL=mxbai-embed-large
```

## Verification

### Test Ollama Installation

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Test with Python
uv run python -c "import ollama; print('✅ Ollama client works!')"
```

### Test CityPulse Integration

```bash
# Start CityPulse backend
uv run uvicorn app.main:app --reload

# Check logs for Ollama provider initialization
# Look for: "🦙 Using Ollama embedding provider" and "🦙 Using Ollama LLM provider"
```

## Performance Optimization

### Hardware Requirements

**Minimum:**
- 8GB RAM
- 4GB free disk space

**Recommended:**
- 16GB+ RAM
- SSD storage
- Apple Silicon Mac or modern CPU with AVX2

### Performance Tips

1. **GPU Acceleration** (if available):
   - Ollama automatically uses Metal on macOS
   - CUDA support on Linux with compatible GPUs

2. **Memory Management**:
   - Models stay loaded in memory for faster inference
   - Ollama automatically manages memory usage

3. **Concurrent Requests**:
   - Ollama handles multiple concurrent requests efficiently
   - No API rate limits like cloud services

## Troubleshooting

### Common Issues

**Ollama not starting:**
```bash
# Check if port 11434 is in use
lsof -i :11434

# Kill existing Ollama processes
pkill ollama

# Start fresh
ollama serve
```

**Models not downloading:**
```bash
# Check disk space
df -h

# Manually pull models
ollama pull llama3.2:3b --verbose
```

**Connection errors in CityPulse:**
```bash
# Verify Ollama is running
curl http://localhost:11434/api/tags

# Check CityPulse configuration
grep OLLAMA .env
```

### Performance Issues

**Slow inference:**
- Use smaller models (`gemma2:2b` instead of `llama3.2:3b`)
- Ensure sufficient RAM
- Close other memory-intensive applications

**High memory usage:**
- Ollama keeps models in memory for performance
- Restart Ollama to free memory: `pkill ollama && ollama serve`

## Migration from OpenAI

Your existing CityPulse data and functionality remain unchanged. The migration only affects:

1. **API Costs**: Eliminated (local inference)
2. **Privacy**: Improved (no data sent to external APIs)
3. **Reliability**: No internet dependency for AI features
4. **Performance**: Potentially faster (no network latency)

The provider architecture ensures seamless switching between OpenAI, Ollama, and mock providers.

## Support

For issues specific to:
- **Ollama**: https://github.com/ollama/ollama/issues
- **CityPulse Integration**: Check application logs and verify configuration

## Model Updates

Keep your models updated:

```bash
# Update all models
ollama list | grep -v NAME | awk '{print $1}' | xargs -I {} ollama pull {}

# Update specific model
ollama pull llama3.2:3b
```