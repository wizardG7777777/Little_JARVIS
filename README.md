# Little_JARVIS

A modular voice assistant system that responds to and acts upon user voice prompts.

## Overview

Little_JARVIS is a comprehensive AI assistant framework featuring:
- **Voice-to-text conversion** using Whisper models
- **Large Language Model reasoning** with Qwen3 and Phi-4 models
- **Text-to-speech conversion** (in development)
- **Rule-based intent classification** for safety and risk assessment
- **Function calling and routing** with extensible registry system
- **RAG (Retrieval-Augmented Generation)** for enhanced accuracy

## How It Works

Little_JARVIS processes voice commands through a multi-stage pipeline:

```
Voice Input → Whisper (STT) → Rule Engine → Intent Router → Action Execution → Response
                                    ↓              ↓
                                 [Risk Assessment]  [LLM/RAG/Functions]
```

### Core Components

#### 1. Voice-to-Text Module (Whisper)
- **Input**: Audio data (numpy.ndarray) with sampling rate
- **Output**: Transcribed text (string)
- Converts user voice commands into text for processing

#### 2. Rule-Based Engine
- **Purpose**: Classifies user intent and assesses risk levels
- **Risk Levels**: L1-L5 mapped to actions:
  - L1: High-risk forbidden
  - L2-L3: Requires confirmation
  - L4-L5: Direct execution allowed
- **Intent Types**:
  - Device control (e.g., "打开空调")
  - Information query (e.g., "查看当前车速")
  - Daily chat (e.g., "讲个笑话")
  - Complex commands
  - System operations
- **Returns**: (intent_type, action) tuple

#### 3. Function Registry System
- **Purpose**: Unified API management for all system functions
- **Function Types**:
  - Static functions: Core application functions
  - Plugin functions: Extended capabilities (e.g., `weather.get_forecast`)
  - Third-party APIs: External services (e.g., `stripe.payment`)
- **Features**:
  - Auto-generates JSON Schema for parameters
  - Tracks execution history and statistics
  - Supports batch registration
  - Persistent registry (JSON)

#### 4. RAG Module
- **Purpose**: Reduces hallucinations and improves accuracy
- **Components**:
  - Markdown file splitter for semantic chunks
  - Vector database (ChromaDB) for storage
  - Qwen3-Embedding-0.6B for embeddings
- **Functions**:
  - `split_markdown_semantic()`: Splits documents into semantic blocks
  - `add()`: Vectorizes and stores text in database
  - `retrieve()`: Finds most relevant content for queries

#### 5. Language Model Integration
- **Models**: Qwen3 series (0.6B, 1.7B, 4B), Phi-4-mini-instruct
- **Backends**: PyTorch, VLLM, llama.cpp
- **Features**:
  - Thinking chain mode for complex reasoning
  - Batch processing
  - Streaming support

### Processing Flow

1. **Voice Input**: User speaks a command
2. **Speech Recognition**: Whisper converts audio to text
3. **Intent Classification**: Rule Engine determines intent and risk level
4. **Routing Decision**:
   - High-risk → Block with explanation
   - Needs confirmation → Ask user to confirm
   - Safe operation → Route to appropriate handler:
     - Known functions → Function Registry
     - Knowledge queries → RAG Module
     - General queries → LLM
5. **Execution**: Selected component processes the request
6. **Response Generation**: Result converted to speech (TTS - in development)

## Architecture

The system follows a modular architecture with clear separation of concerns:

1. **Voice Processing Pipeline**: Converts speech to text using Whisper
2. **Language Model Integration**: Processes text with multiple LLM backends (PyTorch, VLLM, llama.cpp)
3. **Intent Classification & Routing**: Classifies user intent and routes to appropriate handlers
4. **Function Registry System**: Dynamically registers and executes functions
5. **RAG Module**: Uses ChromaDB for semantic search over knowledge base

## Installation

```bash
pip install -r requirements_onnx.txt
```

## Usage

### Running Tests
```bash
# Test chatbot functionality
cd ChatBots && python run_chatbot_tests.py

# Test full system integration
cd SystemTest && python test_full_api_integration.py

# Test RAG functionality
cd SystemTest && python run_rag_tests.py
```

### Example Usage

```python
# Initialize components
from rule_engine import RuleEngine
from function_registry import FunctionRegistry
from rag import RAG

# Process voice command
engine = RuleEngine("Rules.json")
registry = FunctionRegistry(verbose=True)
rag = RAG()

# Example flow
user_input = "打开空调"  # From Whisper STT
intent, action = engine.process_input(user_input)

if intent == "LLM":
    # Route to LLM for general queries
    response = chat_bot.process(user_input)
elif action == "直接放行":
    # Execute through function registry
    result = registry.execute("window_control", action="open")
elif action == "需二次确认":
    # Ask for user confirmation
    confirm = ask_confirmation(user_input)
```

## Project Status

**Note: This project is currently under active development and is not complete.**

### Upcoming Features (Next Week)

1. **Pipeline Implementation**: Complete integration of STT (Speech-to-Text), LLM, and TTS (Text-to-Speech) components into a unified pipeline
2. **Optimization Method**: Implement 8-bit quantization for models to reduce memory usage and improve performance
3. **Model Management**: Transition from hard-coded model configurations to JSON-based model management system

## Technologies

- **Python** as the primary language
- **PyTorch** for deep learning
- **Transformers** (Hugging Face) for LLM management
- **ChromaDB** for vector database (RAG)
- **ONNX Runtime** for model optimization
- **Whisper** for speech-to-text
- **Qwen3** and **Phi-4** models for language understanding

## License

[License information to be added]