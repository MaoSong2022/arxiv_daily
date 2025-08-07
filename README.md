# ArXiv Daily Paper Tracker

A powerful tool for tracking, analyzing, and summarizing daily arXiv papers in your areas of interest. This tool automatically fetches papers from arXiv, generates summaries using AI, and creates both HTML and Markdown reports for easy reading and sharing.

## Features

- 🔍 **Daily Paper Tracking**: Automatically fetches papers from arXiv based on specified categories
- 🤖 **AI-Powered Summaries**: Generates TL;DR summaries and extracts keywords using advanced language models
- 📊 **Smart Categorization**: Automatically classifies papers into predefined categories
- 📝 **Multiple Output Formats**: Generates both HTML and Markdown reports
- 🎯 **Customizable Categories**: Configure which arXiv categories to track
- 🔄 **Duplicate Detection**: Automatically removes duplicate papers across categories
- 📱 **Responsive Web Interface**: View and interact with papers through a modern web interface
- 💾 **Data Export**: Export selected papers to JSON format for further processing

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/arxiv_daily.git
cd arxiv_daily
```

1. Install [uv](https://docs.astral.sh/uv/):

```bash
# install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. set API_KEY

```bash
cd arxiv_daily
touch .env
# add API_KEY and API_BASE_URL in .env file
```

## Usage

### Basic Usage

Run the main script to fetch and process today's papers:

```bash
# the first time will install dependencies
uv run src/main.py
```

### Command Line Options

- `--output_path`: Specify output directory (default: "output")
- `--retrieve`: Force retrieve papers even if output exists (default: False)
- `--html`: Regenerate HTML report (default: False)
- `--markdown`: Regenerate markdown report (default: False)
- `--resummarize`: Regenerate paper summaries (default: False)
- `--date`: Specify date to collect papers for (YYYY-MM-DD format)
- `--model`: Specify model for generating summaries (default: "ollama/qwen2.5:32b")

Example:

```bash
python -m src.main --date 2024-03-14 --model qwen-plus
```

### Output Structure

The tool generates the following outputs in the specified output directory:

```
output/
└── YYYY-MM/
    ├── YYYY-MM-DD.json                    # Raw paper data
    ├── YYYY-MM-DD_exported_papers.json    # Selected papers
    ├── YYYY-MM-DD_report.html            # HTML report
    └── YYYY-MM-DD_report.md              # Markdown report
```

## Configuration

### Categories

Configure the arXiv categories to track in `src/config/settings.py`. The tool supports all arXiv categories.

### Classifiers

The tool uses predefined classifiers to categorize papers. You can modify these in `src/config/settings.py`:

```python
classifiers = [
    "multimodal large language model",
    "large language model",
    "long context",
    # ... add your own categories
]
```

## Development

### Project Structure

```
arxiv_daily/
├── src/
│   ├── api/          # API endpoints
│   ├── config/       # Configuration files
│   ├── data/         # Data processing modules
│   ├── generation/   # Report generation
│   ├── web/          # Web interface
│   └── main.py       # Main entry point
├── tests/            # Test files
├── output/           # Generated reports
└── pyproject.toml    # Project dependencies
```

### Running Tests

```bash
poetry run pytest
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [arXiv API](https://arxiv.org/help/api/) for paper data
- [Ollama](https://ollama.ai/) for AI model integration
- [cool paper](https://papers.cool/) an excellent paper reading platform.
