from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from tools.data_fetch import fetch_current_price, fetch_historical_prices


class PriceAnalyst:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def analyze(self, cryptocurrency: str, days: int = 30) -> str:
        """
        Fetch and analyze price data for a cryptocurrency.

        Args:
            cryptocurrency: Crypto symbol e.g. BTC, ETH
            days: Number of days of historical data

        Returns:
            Structured price analysis as a string
        """
        # Fetch both current and historical data using @tool functions
        current_data = fetch_current_price.invoke({
            "cryptocurrency": cryptocurrency
        })

        historical_data = fetch_historical_prices.invoke({
            "cryptocurrency": cryptocurrency,
            "days": days
        })

        if "Error" in current_data and "Error" in historical_data:
            return f"Could not retrieve price data for {cryptocurrency}"

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert cryptocurrency price analyst.
            
            Analyze the provided price data and produce a structured analysis covering:
            
            1. **Current Market Position**: Where the price stands right now
            2. **Trend Analysis**: Is it in an uptrend, downtrend, or consolidation?
            3. **Volatility Assessment**: How volatile has it been recently?
            4. **Support & Resistance**: Key price levels based on the data
            5. **Moving Averages**: What the SMAs suggest about momentum
            6. **Short-term Outlook**: What the data suggests may happen next
            
            Be technical, precise, and back your analysis with the numbers provided.
            Format your response clearly with the sections above."""),
            ("user", """Analyze the following price data for {crypto} over the last {days} days:

CURRENT DATA:
{current}

HISTORICAL DATA:
{historical}
""")
        ])

        chain = prompt | self.llm

        response = chain.invoke({
            "crypto": cryptocurrency,
            "days": days,
            "current": current_data,
            "historical": historical_data
        })

        return response.content