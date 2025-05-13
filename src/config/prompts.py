prompt = """
Title:
{title}

Abstract:
{abstract}

You are a research assistant tasked with analyzing and categorizing AI research papers. Please analyze this paper and provide:

1. A concise TL;DR summary (1-3 sentences) capturing the main contribution and significance.
   Example: "This paper proposes a training-free method for token reduction in MLLMs that improves inference speed by 30% with minimal accuracy loss."

2. 3-5 relevant keywords using general technical terms (avoid specific model names).
   Examples: 'Large Language Models', 'Retrieval-Augmented Generation', 'Multimodal Learning', 'Diffusion Models', 'Image Generation'

3. Classify this paper into exactly ONE of these categories: {classifiers}
   Choose the most specific category that applies. Select 'Others' only if none fit.

Important guidelines:
- For TL;DR, focus on technical contributions and innovations, not just applications
- For keywords, use standardized technical terms that would help in categorization
- Avoid abbreviations in keywords; use full terms (e.g., "Large Language Models" not "LLM")
- Do not split the one keyword into multiple keywords, for example, "multimodal large language model" is one keyword, not "multimodal" and "large language model"
- Select only ONE classifier that best represents the paper's primary focus, if you cannot decide, select "Others".

Common terms reference:
- Large Language Model (LLM): Text-based AI models like GPT, LLaMA, etc.
- Multimodal Large Language Model (MLLM): Models that process both text and images/audio
- Retrieval-Augmented Generation (RAG): Systems that retrieve external knowledge to enhance generation
- Key-Value (KV) cache: Memory optimization technique for transformer models

Format your response EXACTLY as follows:
TL;DR: [your summary]
Keywords: [comma-separated keywords]
Classifier: single classifier
"""
