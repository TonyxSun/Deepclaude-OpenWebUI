# DeepClaude for Open WebUI

A **Pipe** for Open WebUI that integrates with the DeepClaude managed API service. This allows you to harness the power of **hybrid thinking**: combining DeepSeek Reasoner's chain-of-thought capabilities with Claude's response generation to create enhanced AI responses at a lower cost.

## Overview

DeepClaude creates a powerful synergy by:
1. Using DeepSeek Reasoner for thorough step-by-step reasoning (visible in the thinking process)
2. Passing this reasoning to Claude for final response generation

This approach achieves results comparable to Claude with extended thinking mode at a fraction of the cost, typically 1/3 or less depending on usage patterns.

## Installation

Import the pipe into your Open WebUI instance:
* **Pipe**: https://openwebui.com/f/tonyxsun/deepclaude

## Features

- **Streaming Support**: Watch the AI's thinking process unfold in real-time (R1)
- **Fully Managed API**: No need to manage complex integrations - connect directly to DeepClaude's API service
- **Cost Efficient**: Optimize performance while reducing token usage costs
- **Simple Configuration**: Just add your API keys and start using

## Configuration Options

| Parameter | Description |
|-----------|-------------|
| `DEEPCLAUDE_API_BASE_URL` | DeepClaude API endpoint (defaults to https://api.deepclaude.com) |
| `DEEPSEEK_API_KEY` | Your DeepSeek API authentication token |
| `ANTHROPIC_API_KEY` | Your Anthropic API authentication token |
| `STREAM` | Enable/disable response streaming (default: true) |
| `VERBOSE` | Include detailed API responses in output (default: false) |
| `TEMPERATURE` | Temperature parameter for both models (default: 0.7) |

## Example Usage

Once installed, you can select DeepClaude from your model list and start asking questions. You'll see the thinking process enclosed in `<thinking>` tags followed by the final response:

```
User: How many "r"s appear in the word "strawberry"?

AI: <thinking>
Okay, let's see. The user is asking how many times the letter "r" appears in the word "strawberry". Hmm, I need to make sure I spell the word correctly first. Strawberry. S-T-R-A-W-B-E-R-R-Y. Let me break it down letter by letter.

Starting with the first letter: S. No r there. Then T. Still no. Third letter is R. That's one. Next is A. Then W. B, E. Now after E comes R, that's the second R. Then another R right after, so that's the third R. Finally Y. 

So in total, there are 3 instances of the letter "r" in "strawberry".
</thinking>

There are 3 "r"s in the word "strawberry".
```

## How It Works

1. Your query is sent to the DeepClaude managed API
2. DeepSeek Reasoner processes your query with detailed reasoning
3. Claude receives both your original query and DeepSeek's reasoning
4. Claude generates the final polished response
5. The entire process is streamed back to your interface

## License

MIT

---

ref: https://github.com/GrayXu/openwebui-hybrid-thinking, https://deepclaude.com/
