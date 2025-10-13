# ArXiv Daily Paper Tracker

A Python tool for automatically tracking, analyzing, and summarizing daily arXiv papers in AI/ML categories. Features AI-powered summarization, smart categorization, and generates both HTML and Markdown reports.

## Features

- 🔍 **Daily Paper Tracking**: Fetches papers from arXiv or papers.cool
- 🤖 **AI Summarization**: Generates TL;DR summaries and keywords using LLMs
- 📊 **Smart Categorization**: Auto-classifies papers into predefined categories
- 📝 **Dual Output**: Creates both HTML and Markdown reports
- 🔄 **Duplicate Detection**: Removes duplicate papers across categories
- 📱 **Interactive HTML**: Modern web interface with paper selection

## Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

1. **Clone and setup**:

```bash
git clone https://github.com/yourusername/arxiv_daily.git
cd arxiv_daily
```

2. **Install dependencies**:

```bash
uv sync
```

3. **Configure API keys**:

```bash
# Create .env file
echo "OPENAI_API_KEY=your_key_here" > .env
echo "API_BASE_URL=your_base_url_here" >> .env
```

### Usage

**Basic usage** (process today's papers):

```bash
uv run src/main.py
```

**With options**:

```bash
uv run src/main.py --date 2024-03-14 --model qwen-plus --source arxiv
```

**Command line options**:

- `--date`: Date to collect papers (YYYY-MM-DD)
- `--model`: AI model for summarization (default: ollama/qwen2.5:32b)
- `--source`: Data source (arxiv or cool_paper)
- `--output_path`: Output directory (default: output)
- `--retrieve`: Force retrieve even if output exists
- `--html`: Regenerate HTML report
- `--markdown`: Regenerate Markdown report

## Output Structure

```
output/
└── 2024-03/
    ├── 2024-03-14.json              # Raw paper data
    ├── 2024-03-14_report.html       # Interactive HTML report
    └── 2024-03-14_report.md         # Markdown report
```

## Configuration

Edit `src/config.py` to customize:

- **Categories**: arXiv categories to track (cs.LG, cs.AI, cs.CV, cs.CL)
- **Classifiers**: Paper classification categories
- **Filters**: Categories to exclude from reports

## Development

**Project structure**:

```
src/
├── main.py              # Entry point
├── config.py            # Configuration
├── retrieve_paper.py    # Paper fetching
├── summarize.py         # AI summarization
├── postprocess.py       # Data processing
├── html_report.py       # HTML generation
├── markdown_report.py   # Markdown generation
└── utils.py             # Utilities
```

**Code formatting**:

```bash
uv run ruff format src/
uv run ruff check src/
```

## License

MIT License - see [LICENSE](LICENSE) file.

## Acknowledgments

- [arXiv API](https://arxiv.org/help/api/) for paper data
- [papers.cool](https://papers.cool/) for alternative data source
- [Ollama](https://ollama.ai/) for local AI model support
