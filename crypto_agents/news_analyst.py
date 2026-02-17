from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from tools.data_fetch import fetch_crypto_news


class NewsAnalyst:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def analyze(self, cryptocurrency: str) -> str:
        """
        Fetch and analyze recent news for a cryptocurrency.

        Args:
            cryptocurrency: Crypto symbol e.g. BTC, ETH

        Returns:
            Structured news analysis as a string
        """
        # Use the @tool function directly to fetch news
        raw_news = fetch_crypto_news.invoke({
            "cryptocurrency": cryptocurrency,
            "num_results": 5
        })

        if "Error" in raw_news or "No recent news" in raw_news:
            return f"No news analysis available: {raw_news}"

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert cryptocurrency news analyst.
            
            Analyze the provided news articles and produce a structured analysis covering:
            
            1. **Overall Sentiment**: Bullish / Bearish / Neutral with brief reasoning
            2. **Key Themes**: Main topics and narratives in the news
            3. **Notable Events**: Any significant announcements, partnerships, or developments
            4. **Market Impact**: How this news could affect the price and market
            5. **Risk Factors**: Any negative news or concerns mentioned
            
            Be objective, concise, and data-driven. Format your response clearly with 
            the sections above."""),
            ("user", "Analyze the following news for {crypto}:\n\n{news}")
        ])

        chain = prompt | self.llm

        response = chain.invoke({
            "crypto": cryptocurrency,
            "news": raw_news
        })

        return response.content