from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
import re
import os


class ReportWriter:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def generate(
        self,
        cryptocurrency: str,
        days: int,
        focus: str,
        news_analysis: str,
        price_analysis: str
    ) -> str:
        """
        Synthesize news and price analyses into a comprehensive markdown report.

        Args:
            cryptocurrency: Crypto symbol
            days: Analysis timeframe in days
            focus: User's area of interest
            news_analysis: Output from NewsAnalyst
            price_analysis: Output from PriceAnalyst

        Returns:
            Full markdown report as a string
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a professional cryptocurrency market analyst writing 
            a comprehensive research report.

            Generate a well-structured, professional report in Markdown format.
            The report must include these sections:

            # [CRYPTO] Cryptocurrency Analysis Report

            ## Executive Summary
            A concise 3-4 sentence overview of the current state and key findings.

            ## Market Overview
            Current market position, context, and broader market conditions.

            ## Price Analysis
            Detailed breakdown using the price analysis data provided.

            ## News & Sentiment Analysis
            Detailed breakdown using the news analysis data provided.

            ## Key Insights
            3-5 bullet points of the most important takeaways.

            ## Risks & Considerations
            Key risks investors should be aware of.

            ## Outlook
            Short-term outlook based on the combined analysis.

            ---
            *Report generated on {date} | Timeframe: {days} days | Focus: {focus}*
            *This report is for informational purposes only and does not constitute financial advice.*

            Make the report detailed, professional, and actionable.
            Use markdown formatting throughout (headers, bold, bullet points, etc.)."""),
            ("user", """Generate a report for {crypto}:

PRICE ANALYSIS:
{price}

NEWS ANALYSIS:
{news}
""")
        ])

        chain = prompt | self.llm

        response = chain.invoke({
            "crypto": cryptocurrency,
            "days": days,
            "focus": focus,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
            "price": price_analysis,
            "news": news_analysis
        })

        return response.content

    def save(self, content: str, cryptocurrency: str) -> str:
        """
        Save the report as a markdown file.

        Args:
            content: Markdown report content
            cryptocurrency: Crypto symbol for filename

        Returns:
            Path to the saved file
        """

        reports_dir = "Reports"
        os.makedirs(reports_dir, exist_ok = True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{cryptocurrency}_report_{timestamp}.md"
        filepath = os.path.join(reports_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return filename