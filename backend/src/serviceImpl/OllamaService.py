import sys
from typing import Iterator
from ollama import chat
# Add project root to path
sys.path.append("../../")

from src.service.LLMService import LLMQueryProcessor


class OllamaQueryProcessor(LLMQueryProcessor):
    """
    Concrete implementation of LLMQueryProcessor for interacting with Ollama models.

    This class provides both synchronous and streaming interfaces to query a
    local or remote Ollama model endpoint using the `ollama.chat()` API.

    Attributes:
        model_id (str): The model identifier to use with Ollama (default: "qwen3-vl:2b").
    """

    def __init__(self, model_id: str = "qwen3-vl:2b") -> None:
        """
        Initialize the OllamaQueryProcessor with a specific model.

        Args:
            model_id (str): The Ollama model to use. Default is 'qwen3-vl:2b'.
        """
        super().__init__()
        self.model_id = model_id

    def generate_answer(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 1000,
        think: bool = False,
    ) -> str:
        """
        Generate a complete response from the model for a given prompt.

        Args:
            prompt (str): The user query or input text.
            temperature (float): Controls randomness in generation (0.0 = deterministic).
            max_tokens (int): Maximum number of tokens to generate.
            think (bool): If True, includes the model's reasoning trace (if supported).

        Returns:
            str: JSON-formatted string containing the full response payload.
        """
        options = {
            "temperature":temperature,
            "num_predict": max_tokens
        }
        response = chat(
            model=self.model_id,
            messages=[{"role": "user", "content": prompt}],
            stream=False,
            think=think,
            options=options
        )
        return response.model_dump_json()

    def generate_answer_stream(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 1000,
        think: bool = False,
    ) -> Iterator[str]:
        """
        Stream model output incrementally as it generates text.

        Args:
            prompt (str): The input query for the model.
            temperature (float): Sampling temperature for response variability.
            max_tokens (int): Maximum number of tokens to stream.
            think (bool): If True, stream both the reasoning (thinking) and content phases.

        Yields:
            str: Incremental chunks of generated text (either reasoning or final output).

        Example:
            >>> ollama = OllamaQueryProcessor()
            >>> for chunk in ollama.generate_answer_stream("Explain gravity in simple terms"):
            ...     print(chunk, end='')
        """
        options = {
            "temperature":temperature,
            "num_predict": max_tokens
        }
        stream = chat(
            model=self.model_id,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            think=think,
            options=options
        )

        in_thinking = False

        for chunk in stream:
            if chunk.message.thinking:
                if not in_thinking:
                    in_thinking = True
                    yield chunk.message.thinking
            elif chunk.message.content:
                if in_thinking:
                    in_thinking = False
                yield chunk.message.content


if __name__ == "__main__":
    ollama = OllamaQueryProcessor()
    prompt = "The capital city of India is"
    print("\n--- Synchronous Response ---")
    print(ollama.generate_answer(prompt=prompt))

    print("\n--- Streaming Response ---")
    for token in ollama.generate_answer_stream(prompt=prompt):
        print(token, end="")
