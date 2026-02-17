# Crypto Analysis Agent 

I built this as a way to stop manually checking five different tabs every time I wanted a quick read on a cryptocurrency. You know the drill — CoinGecko for price, Twitter for sentiment, Google News for headlines, then trying to piece it all together in your head. This automates that whole process into a single terminal command.

## What It Does

You type something like *"analyze Ethereum for the last 60 days"* and it takes care of the rest — pulls historical price data, grabs recent news, runs analysis on both, and spits out a formatted report saved to a markdown file.

Under the hood it's a multi-agent system where each agent has one job:

- **Customer Communicator** — figures out what you're asking for, even if you're vague about it
- **News Analyst** — fetches and makes sense of recent news using Exa
- **Price Analyst** — pulls historical OHLCV data and calculates trends, momentum, volatility
- **Report Writer** — ties everything together into a readable markdown report

## Tech Stack

- **LangChain** — agent orchestration and LLM chaining
- **OpenAI GPT-4** — the brains behind each agent
- **yfinance** — free historical price data, no API key needed
- **Exa** — semantic news search

## Getting Started

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/crypto-analysis-agent.git
cd crypto-analysis-agent
```

**2. Set up a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up your API keys**

Copy `.env.example` to `.env` and fill in your keys:
```bash
cp .env.example .env
```

```
OPENAI_API_KEY=your_openai_api_key
EXA_API_KEY=your_exa_api_key
```

You only need two keys. Price data comes from Yahoo Finance which is completely free and requires no authentication.

**5. Run it**
```bash
python main.py
```

## Usage

The agent understands natural language so you don't need to be precise:

```
Analyze Ethereum for the last 60 days, focus on price trends and recent news
```
```
What's happening with Solana lately?
```
```
Give me a breakdown of Bitcoin
```

Reports are saved to the `Reports/` folder as markdown files, named by coin and timestamp e.g. `ETH_report_20240315_142301.md`.

## Project Structure

```
crypto-analysis-agent/
├── main.py                          # Entry point
├── crypto_agents/
│   ├── customer_communicator.py     # Parses user input
│   ├── news_analyst.py              # Fetches and analyzes news
│   ├── price_analyst.py             # Fetches and analyzes price data
│   └── report_writer.py             # Generates the final report
├── tools/
│   └── data_fetch.py                # @tool functions for Exa and yfinance
├── Reports/                         # Generated reports saved here
├── .env.example                     # Template for API keys
└── requirements.txt
```

## Supported Cryptocurrencies

Works with any coin available on Yahoo Finance. Common ones like BTC, ETH, SOL, ADA, DOT, AVAX, DOGE and more are mapped automatically. For anything else, just use the Yahoo Finance format directly e.g. `PEPE-USD`.

## Limitations

- News quality depends on Exa's index — very niche coins might not have much coverage
- Price analysis is based on historical data only, not a financial advisor
- GPT-4 inference adds a few seconds to each run

## License

MIT