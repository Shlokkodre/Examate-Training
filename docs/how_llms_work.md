# How LLMs Work - Explained Simply

## What is an LLM?

A **Large Language Model (LLM)** is an AI system trained on massive amounts of text data to understand and generate human-like language. Think of it as a sophisticated pattern recognition system that has learned the statistical relationships between words, phrases, and concepts.

## Core Components

### 1. **Tokens**
Text is broken down into smaller pieces called tokens (words, subwords, or characters). For example:
- "HealthLabelCheck" might become: `["Health", "Label", "Check"]`
- Each token gets converted to numbers that the model can process

### 2. **Embeddings**
Tokens are converted into high-dimensional vectors (lists of numbers) that capture their meaning and relationships. Words with similar meanings have similar vectors.

```
Example:
"food" → [0.23, -0.45, 0.78, ...]
"snack" → [0.25, -0.42, 0.81, ...]  (similar to "food")
"regulation" → [-0.61, 0.33, -0.12, ...]  (different context)
```

### 3. **Transformer Architecture**

The breakthrough that powers modern LLMs. It uses **attention mechanisms** to understand context:

```
┌─────────────────────────────────────────────────────────┐
│                    LLM Architecture                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Input: "What must be on a food label?"                 │
│                         ↓                                │
│  ┌──────────────────────────────────────────┐           │
│  │  Tokenization & Embedding                │           │
│  │  [What, must, be, on, food, label]       │           │
│  │      ↓      ↓     ↓     ↓     ↓     ↓   │           │
│  │  [vectors representing each token]       │           │
│  └──────────────────────────────────────────┘           │
│                         ↓                                │
│  ┌──────────────────────────────────────────┐           │
│  │  Multi-Head Attention Layers             │           │
│  │  • Each word attends to other words      │           │
│  │  • Understands: "label" relates to       │           │
│  │    "food" and "must" indicates required  │           │
│  │  • Multiple attention heads = different  │           │
│  │    aspects of meaning                    │           │
│  └──────────────────────────────────────────┘           │
│                         ↓                                │
│  ┌──────────────────────────────────────────┐           │
│  │  Feed-Forward Neural Networks            │           │
│  │  • Processes attended information        │           │
│  │  • Builds deeper understanding           │           │
│  └──────────────────────────────────────────┘           │
│                         ↓                                │
│  ┌──────────────────────────────────────────┐           │
│  │  Output Layer (Next Token Prediction)    │           │
│  │  Predicts: "According" (86% probability) │           │
│  │           "Based" (8% probability)       │           │
│  │           "The" (3% probability)         │           │
│  └──────────────────────────────────────────┘           │
│                         ↓                                │
│  Output: "According to FSSAI regulations..."            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 4. **Self-Attention Mechanism**

This is the magic that lets the model understand context:

- When processing the word "label", the model looks at ALL other words in the input
- It calculates how much each word relates to "label"
- High attention weights mean stronger relationships

Example with "What must be on a food **label**?":
- "label" pays strong attention to: "food" (what kind of label?), "must" (requirement), "on" (location)
- This helps generate relevant answers about food labelling requirements

## Training Process

### Pre-training
1. **Massive Text Corpus**: Models are trained on billions of words from books, websites, code, etc.
2. **Objective**: Learn to predict the next word
   - Input: "Name of" → Predict: "Food"
   - Input: "FSSAI License" → Predict: "Number"
3. **Result**: The model learns grammar, facts, reasoning patterns, and world knowledge

### Fine-tuning (Optional)
- Train on specific domain data (e.g., FSSAI regulations)
- Align with human preferences through feedback
- Make the model more helpful and accurate

## How Generation Works

When you ask: "What are the mandatory label requirements?"

1. **Encode**: Convert question to tokens and embeddings
2. **Process**: Run through transformer layers to understand context
3. **Predict**: Generate one token at a time:
   - "There" → "are" → "10" → "mandatory" → "declarations" → ...
4. **Repeat**: Each new token is fed back as input to predict the next
5. **Stop**: Continue until reaching a stopping condition (end token, max length)

## Key Parameters

- **Temperature**: Controls randomness
  - Low (0.1): More focused, deterministic
  - High (0.9): More creative, varied
  
- **Top-p / Top-k**: Limits which tokens can be selected
  - Prevents nonsensical completions
  
- **Max Tokens**: Maximum length of response

## Limitations

1. **No Real Understanding**: LLMs recognize patterns but don't truly "understand" like humans
2. **Training Data Cutoff**: Only knows information up to training date
3. **Hallucinations**: Can confidently generate false information
4. **Context Window**: Limited memory (can only process a certain number of tokens)
5. **No Real-time Data**: Can't access live information without external tools

## Why This Matters for HealthLabelCheck

Our project uses LLMs to:
- **Answer Questions**: Convert FSSAI regulations into user-friendly answers
- **Search**: Understand semantic similarity between user queries and regulations
- **Extract Information**: Pull relevant details from regulation documents
- **Generate Guidance**: Provide actionable advice for food label compliance

By combining LLMs with our structured FSSAI data (RAG - Retrieval Augmented Generation), we get:
- ✅ Accurate answers grounded in regulations
- ✅ Natural language interaction
- ✅ Context-aware responses
- ✅ Reduced hallucinations (verified against source data)

## Real-World Example

**User**: "My chakli pouch is 12cm × 8cm, what font size do I need?"

**Without LLM**: User must manually read through regulations, find Table I, calculate area, look up font size

**With LLM + RAG**:
1. Understands: User needs font size for a specific package
2. Retrieves: Regulation 6.1 and font size table
3. Calculates: 12 × 8 = 96 cm²
4. Looks up: 96 cm² falls in 40-170 cm² range
5. Answers: "Your panel area is 96 cm². According to FSSAI Regulation 6.1, the minimum letter height required is 1.5 mm."

---

*Note: This explanation simplifies complex concepts. Real LLMs involve advanced mathematics, billions of parameters, and sophisticated training techniques.*
