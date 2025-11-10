from abc import ABC, abstractmethod
from typing import Iterator

class LLMQueryProcessor(ABC):
    """Interface (abstract base class) for LLM Query processing."""

    @abstractmethod
    def generate_answer(self, prompt:str, temperature:float, max_tokens:int, think:bool) -> str:
        """generate answer for a prompt"""
        pass
    
    @abstractmethod
    def generate_answer_stream(self, prompt:str, temperature:float, max_tokens:int, think:bool) -> Iterator[str]:
        """generate answer stream for a prompt"""
        pass
    
    