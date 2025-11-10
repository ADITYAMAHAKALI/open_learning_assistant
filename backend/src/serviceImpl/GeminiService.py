import os
import base64
import mimetypes
from typing import Iterator, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
import sys
sys.path.append("../../")
from src.service.LLMService import LLMQueryProcessor


class GeminiQueryProcessor(LLMQueryProcessor):
    """
    Concrete implementation of LLMQueryProcessor for Google's Gemini API.

    This class supports text generation using the Gemini models.
    It also provides a streaming generator for incremental responses.

    Environment Variables:
        GEMINI_API_KEY (str): Your Google Gemini API key.
    """

    def __init__(self, model_id: str = "gemini-2.5-flash") -> None:
        """
        Initialize GeminiQueryProcessor and load environment variables.

        Args:
            model_id (str): The Gemini model to use (default: "gemini-2.5-flash-image").
        """
        super().__init__()
        load_dotenv()

        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise EnvironmentError("Missing GEMINI_API_KEY in environment or .env file")

        self.client = genai.Client(api_key=self.api_key)
        self.model_id = model_id

    def generate_answer(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 1000,
        think: bool = False,
    ) -> str:
        """
        Generate a complete Gemini response (text + image).

        Args:
            prompt (str): Input text prompt.
            temperature (float): Sampling temperature (0.0 = deterministic).
            max_tokens (int): Token limit for response.
            think (bool): Reserved for consistency; not used here.
            save_images (bool): If True, saves generated images to disk.

        Returns:
            str: Combined text response from the model.
        """
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            )
        ]

        config = types.GenerateContentConfig(
            response_modalities=["TEXT"],
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=contents,
            config=config,
        )

        text_output = ""
        image_index = 0

        for part in response.candidates[0].content.parts:
            if part.text:
                text_output += part.text

        return text_output.strip()

    def generate_answer_stream(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 1000,
        think: bool = False,
    ) -> Iterator[str]:
        """
        Stream Gemini text and image responses incrementally.

        Args:
            prompt (str): Input text prompt.
            temperature (float): Sampling temperature.
            max_tokens (int): Token limit for streaming response.
            think (bool): Reserved for consistency; not used here.

        Yields:
            str: Incremental text chunks from the model.
        """
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            )
        ]

        config = types.GenerateContentConfig(
            response_modalities=["TEXT"],
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        stream = self.client.models.generate_content_stream(
            model=self.model_id,
            contents=contents,
            config=config,
        )

        for chunk in stream:
            if not chunk.candidates or not chunk.candidates[0].content:
                continue
            parts = chunk.candidates[0].content.parts
            if not parts:
                continue

            # Text streaming
            if parts[0].text:
                yield parts[0].text


    # utility for async frameworks
    def __repr__(self) -> str:
        return f"<GeminiQueryProcessor(model_id='{self.model_id}')>"


if __name__ == "__main__":
    processor = GeminiQueryProcessor()
    prompt = "Generate a 1-line motivational quote and an abstract blue background image description."

    print("\n--- Gemini Text Response ---")
    print(processor.generate_answer(prompt))

    print("\n--- Gemini Streaming Response ---")
    for chunk in processor.generate_answer_stream(prompt):
        print(chunk, end="")
    print()
