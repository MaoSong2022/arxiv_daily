# Categories to query
categories = ["cs.LG", "cs.AI", "cs.CV", "cs.CL"]


# Day delta configuration for different weekdays
day_delta: dict[int, tuple[int, int]] = {
    0: (4, 3),  # monday: last thursday to last friday
    1: (4, 1),  # tuesday: last friday to last sunday
    2: (2, 1),  # wednesday: last saturday to last monday
    3: (2, 1),  # thursday: last monday to last tuesday
    4: (2, 1),  # friday: last tuesday to last wednesday
}

# Define classifiers for the prompt
classifiers = [
    "multimodal large language model",
    "large language model",
    "long context",
    "key value cache",
    "image generation",
    "video generation",
    "diffusion/flow matching/consistency",
    "retrieval augmented generation",
    "agent",
    "survey",
    "benchmark",
    "autonomous driving",
    "point cloud",
    "vision language action",
    "gauss splatting",
    "slam",
    "anomaly detection",
    "segmentation",
    "neural radiance fields",
    "3d scene generation",
    "reinforcement learning",
    "others",
]

# Categories to filter out papers
filtered_categories: list[str] = [
    "gauss splatting",
    "autonomous driving",
    "point cloud",
    "vision language action",
    "3d scene generation",
    "others",
]

super_categories: dict[str, str] = {
    "image generation": "Generation",
    "video generation": "Generation",
    "diffusion/flow matching/consistency": "Generation",
    "long context": "LLM",
    "key value cache": "LLM",
    "retrieval augmented generation": "RAG",
    "multimodal large language model": "MLLM",
    "large language model": "LLM",
    "agent": "Agent",
    "survey": "Survey",
    "benchmark": "Benchmark",
    "reinforcement learning": "LLM",
}


boring_sections = ["others"]

# Prompt template for paper summarization
prompt_template: str = """
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
