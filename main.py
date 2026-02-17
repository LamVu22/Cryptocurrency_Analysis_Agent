import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from utils import config
from crypto_agents import CustomerCommunicator, NewsAnalyst, PriceAnalyst, ReportWriter

load_dotenv()


def main():
    print("=" * 60)
    print("       🤖 Cryptocurrency Analysis Agent")
    print("=" * 60)

    # Initialize shared LLM
    llm = ChatOpenAI(
        model= config.MODEL_NAME,
        temperature=config.TEMPERATURE,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # Initialize all agents with the shared LLM
    communicator = CustomerCommunicator(llm)
    news_analyst = NewsAnalyst(llm)
    price_analyst = PriceAnalyst(llm)
    report_writer = ReportWriter(llm)

    # Step 1: Get user input
    user_input = input("\n💬 What would you like to analyze?\n> ")

    # Step 2: Extract structured requirements
    print("\n📋 Processing your request...")
    requirements = communicator.gather_requirements(user_input)
    crypto = requirements.get("cryptocurrency", "BTC")
    days = requirements.get("days", 30)
    focus = requirements.get("focus", "general overview")

    print(f"\n🔍 Analyzing {crypto} over the last {days} days (Focus: {focus})")

    # Step 3: Run news analysis
    print("\n📰 Fetching and analyzing news...")
    news_analysis = news_analyst.analyze(crypto)

    # Step 4: Run price analysis
    print("📊 Fetching and analyzing price data...")
    price_analysis = price_analyst.analyze(crypto, days)

    # Step 5: Generate report
    print("✍️  Generating report...")
    report = report_writer.generate(
        cryptocurrency=crypto,
        days=days,
        focus=focus,
        news_analysis=news_analysis,
        price_analysis=price_analysis
    )

    # Step 6: Save and display
    filepath = report_writer.save(report, crypto)

    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)
    print(f"\n✅ Report saved to: {filepath}")


if __name__ == "__main__":
    main()
