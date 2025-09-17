#!/bin/bash

# =============================================================================
# CityPulse Ollama Setup Script
# =============================================================================
# This script installs Ollama and downloads the required models for CityPulse
# Run this script to set up local AI inference capabilities

set -e  # Exit on any error

echo "🦙 Setting up Ollama for CityPulse..."
echo "This will install Ollama and download the required models (~3-4 GB total)"
echo ""

# Check if running on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="Linux"
else
    echo "❌ Unsupported platform: $OSTYPE"
    echo "Please install Ollama manually from https://ollama.ai"
    exit 1
fi

echo "📱 Detected platform: $PLATFORM"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Ollama if not already installed
if command_exists ollama; then
    echo "✅ Ollama is already installed"
    ollama --version
else
    echo "📥 Installing Ollama..."

    if [[ "$PLATFORM" == "macOS" ]]; then
        # Check if Homebrew is available
        if command_exists brew; then
            echo "🍺 Installing via Homebrew..."
            brew install ollama
        else
            echo "🌐 Installing via curl..."
            curl -fsSL https://ollama.ai/install.sh | sh
        fi
    else
        # Linux installation
        echo "🌐 Installing via curl..."
        curl -fsSL https://ollama.ai/install.sh | sh
    fi

    echo "✅ Ollama installed successfully"
fi

echo ""
echo "🚀 Starting Ollama service..."

# Start Ollama service in background
if [[ "$PLATFORM" == "macOS" ]]; then
    # On macOS, check if Ollama is running
    if ! pgrep -f "ollama" > /dev/null; then
        echo "Starting Ollama server..."
        ollama serve &
        OLLAMA_PID=$!
        echo "Ollama server started with PID: $OLLAMA_PID"
    else
        echo "✅ Ollama server is already running"
    fi
else
    # On Linux, try to start as service or background process
    if systemctl is-active --quiet ollama 2>/dev/null; then
        echo "✅ Ollama service is already running"
    elif command_exists systemctl; then
        echo "Starting Ollama service..."
        sudo systemctl start ollama
        sudo systemctl enable ollama
    else
        echo "Starting Ollama server in background..."
        ollama serve &
        OLLAMA_PID=$!
        echo "Ollama server started with PID: $OLLAMA_PID"
    fi
fi

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
sleep 3

# Check if Ollama is responding
for i in {1..10}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama is ready!"
        break
    else
        echo "Waiting for Ollama... (attempt $i/10)"
        sleep 2
    fi

    if [ $i -eq 10 ]; then
        echo "❌ Ollama failed to start. Please check the installation."
        exit 1
    fi
done

echo ""
echo "📦 Downloading required models..."

# Download LLM model for text generation
echo "🧠 Downloading LLM model: llama3.2:3b (~2GB)..."
ollama pull llama3.2:3b

# Download embedding model
echo "🔢 Downloading embedding model: nomic-embed-text (~274MB)..."
ollama pull nomic-embed-text

echo ""
echo "🎉 Setup complete! Ollama is ready for CityPulse."
echo ""
echo "📋 Installed models:"
ollama list

echo ""
echo "🔗 Ollama is running at: http://localhost:11434"
echo "📝 Your CityPulse backend is now configured to use local AI inference!"
echo ""
echo "💡 To verify everything is working:"
echo "   uv run python -c \"import ollama; print('Ollama client works!')\""
echo ""
echo "🚀 You can now start your CityPulse backend with:"
echo "   uv run uvicorn app.main:app --reload"