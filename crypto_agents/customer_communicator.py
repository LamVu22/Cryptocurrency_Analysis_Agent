from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field


class CryptoRequest(BaseModel):
    cryptocurrency: str = Field(description="The cryptocurrency symbol e.g. BTC, ETH, SOL")
    days: int = Field(description="Number of days for historical analysis, default 30")
    focus: str = Field(description="What the user wants to focus on e.g. price trends, news, general overview")


class CustomerCommunicator:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.parser = JsonOutputParser(pydantic_object=CryptoRequest)

    def gather_requirements(self, user_input: str) -> dict:
        """
        Parse user input and extract structured analysis requirements.

        Args:
            user_input: Raw user query

        Returns:
            Dictionary with cryptocurrency, days, and focus
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant that extracts cryptocurrency 
            analysis requirements from user input.

            Extract the following:
            - cryptocurrency: the symbol (BTC, ETH, SOL, etc.). If the user provides 
              a full name like 'Bitcoin', convert it to its symbol 'BTC'
            - days: the number of days for historical analysis. Default to 30 if not specified
            - focus: what the user wants to focus on (price trends, news sentiment, 
              general overview, etc.)

            {format_instructions}
            """),
            ("user", "{input}")
        ])

        chain = prompt | self.llm | self.parser

        try:
            result = chain.invoke({
                "input": user_input,
                "format_instructions": self.parser.get_format_instructions()
            })
            return result
        except Exception as e:
            print(f"Error parsing requirements: {e}")
            # Sensible fallback defaults
            return {
                "cryptocurrency": "BTC",
                "days": 30,
                "focus": "general overview"
            }