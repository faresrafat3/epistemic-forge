"""Cognitive Economy Tracker (Token & Cost Budgeting).

Ensures the pipeline respects the user's budget and gracefully degrades
or halts if the API costs exceed the specified limits.
"""
from loguru import logger
import litellm

class TokenBudgetManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TokenBudgetManager, cls).__new__(cls)
            cls._instance.reset()
        return cls._instance
        
    def reset(self):
        self.total_tokens = 0
        self.total_cost = 0.0
        self.budget_limit = 8000
        
    def set_budget(self, max_tokens: int):
        self.budget_limit = max_tokens
        
    def add_usage(self, response_object, model: str):
        """Extracts token usage and cost from the LLM response."""
        try:
            usage = response_object.usage
            if usage:
                self.total_tokens += getattr(usage, 'total_tokens', 0)
                # LiteLLM cost calculation helper
                try:
                    cost = litellm.cost_calculator.completion_cost(completion_response=response_object)
                    self.total_cost += cost
                except:
                    pass
        except Exception as e:
            logger.debug(f"Could not track token usage: {e}")

    def is_budget_exceeded(self) -> bool:
        if self.total_tokens >= self.budget_limit:
            logger.warning(f"🚨 COGNITIVE BUDGET EXCEEDED: {self.total_tokens}/{self.budget_limit} tokens used.")
            return True
        return False
        
    def get_report(self) -> str:
        return f"Economy Report -> Tokens: {self.total_tokens} | Est. Cost: ${self.total_cost:.4f}"

budget_manager = TokenBudgetManager()
