import os
import streamlit as st
import google.generativeai as genai
from typing import Optional, List
from src.config.settings import config


class KinyarwandaSummarizer:
    """A class to summarize long Kinyarwanda transcripts using a chunked approach."""

    def __init__(self, gemini_processor):
        """Initializes the summarizer with a Gemini processor instance."""
        self.gemini_processor = gemini_processor

    def chunk_transcript(self, text: str, max_size: int = 1800) -> List[str]:
        """Splits a long transcript into smaller chunks based on size.
        Args:
            text: The full transcript text.
            max_size: The approximate maximum size of each chunk.
        Returns:
            A list of text chunks.
        """
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        for p in paragraphs:
            if len(current_chunk) + len(p) + 2 > max_size:
                chunks.append(current_chunk)
                current_chunk = p
            else:
                if current_chunk:
                    current_chunk += "\n\n" + p
                else:
                    current_chunk = p
        if current_chunk:
            chunks.append(current_chunk)
        return chunks

    def summarize_chunk(self, chunk: str) -> str:
        """Summarizes a single chunk of text.
        Args:
            chunk: A small chunk of the transcript.
        Returns:
            A summary of the chunk.
        """
        prompt = f"""You are an expert focus group analyst fluent in Kinyarwanda.

Analyze this partial Kinyarwanda transcript and provide a detailed summary of this specific section.

Focus on:
- Key topics discussed in this chunk
- Main opinions or arguments presented
- Any specific examples or data points mentioned

This is one part of a larger transcript. Your summary should be self-contained but also ready to be combined with other summaries.

Partial Transcript:
{chunk}

Summary of this chunk (in Kinyarwanda):"""
        return self.gemini_processor._generate_content(prompt)

    def summarize_global(self, partial_summaries: List[str]) -> str:
        """Creates a final, global summary from partial summaries.
        Args:
            partial_summaries: A list of summaries from each chunk.
        Returns:
            A single, cohesive summary.
        """
        combined_summaries = "\n\n---\n\n".join(partial_summaries)
        prompt = f"""You are an expert focus group analyst fluent in Kinyarwanda.

You have been given a series of partial summaries from a long focus group transcript. Your task is to synthesize them into a single, cohesive, and comprehensive final summary.

Ensure the final summary:
- Flows logically and reads as a single document.
- Eliminates redundancy and connects related ideas from different chunks.
- Preserves all key insights, opinions, and conclusions.
- Follows the required structure: Ingingo z'ingenzi, Ibitekerezo, Ibibazo, Ibyifuzo.

Partial Summaries:
{combined_summaries}

Comprehensive Final Summary in Kinyarwanda:"""
        return self.gemini_processor._generate_content(prompt)

    def summarize(self, text: str) -> str:
        """Executes the full chunked summarization pipeline.
        Args:
            text: The full Kinyarwanda transcript.
        Returns:
            The final, comprehensive summary.
        """
        chunks = self.chunk_transcript(text)
        if not chunks:
            return ""

        if len(chunks) == 1:
            return self.summarize_chunk(chunks[0])

        partial_summaries = [self.summarize_chunk(chunk) for chunk in chunks]
        final_summary = self.summarize_global(partial_summaries)
        return final_summary


class GeminiProcessor:
    """A class to process transcripts using the Google Gemini API.

    Attributes:
        model: An instance of the Google Gemini Pro model.
    """

    def __init__(self):
        """Initializes the GeminiProcessor with an API key.

        Raises:
            ValueError: If the GEMINI_API_KEY is not found.
        """
        api_key = config.gemini_api_key

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in secrets or environment variables"
            )

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-pro")
        self.summarizer = KinyarwandaSummarizer(self)
        print("Gemini processor initialized")

    def _generate_content(self, prompt: str, max_retries: int = 3) -> str:
        """Generates content from a prompt with a retry mechanism.

        Args:
            prompt: The prompt to send to the Gemini model.
            max_retries: The maximum number of times to retry the request.

        Returns:
            The generated text content.

        Raises:
            Exception: If the API call fails after all retries.
        """
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(
                        f"Gemini API error after {max_retries} attempts: {str(e)}"
                    )
                print(f"Retry {attempt + 1}/{max_retries} after error: {str(e)}")
                continue

    def fix_orthography(self, raw_text: str) -> str:
        """Fixes the orthography, grammar, and punctuation of a Kinyarwanda transcript.

        Args:
            raw_text: The raw Kinyarwanda transcript.

        Returns:
            The corrected transcript.
        """
        prompt = f"""You are an expert in Kinyarwanda language. 

Fix the orthography, grammar, and punctuation in this Kinyarwanda transcript. Keep the timestamps intact.

Rules:
- Correct spelling errors while preserving Kinyarwanda linguistic rules
- Add proper punctuation (periods, commas, question marks)
- Fix capitalization
- Maintain all timestamps in [HH:MM:SS - HH:MM:SS] format
- Do not translate or change the meaning
- Keep paragraph structure

Transcript:
{raw_text}

Return only the corrected text with timestamps."""

        return self._generate_content(prompt)

    def summarize_kinyarwanda(self, cleaned_text: str) -> str:
        """Summarizes the key insights from a cleaned Kinyarwanda transcript.
        This method now uses the advanced chunked summarization pipeline.
        Args:
            cleaned_text: The cleaned Kinyarwanda transcript.
        Returns:
            A summary of the transcript in Kinyarwanda.
        """
        return self.summarizer.summarize(cleaned_text)

    def translate_to_english(self, kinyarwanda_summary: str) -> str:
        """Translates a Kinyarwanda summary to English.

        Args:
            kinyarwanda_summary: The Kinyarwanda summary.

        Returns:
            The English translation of the summary.
        """
        prompt = f"""Translate this Kinyarwanda focus group summary to English.

Maintain the structure and key sections:
- Key points discussed
- Main opinions/perspectives  
- Concerns raised
- Recommendations/conclusions

Provide a professional, accurate translation suitable for stakeholder review.

Kinyarwanda text:
{kinyarwanda_summary}

English translation:"""

        return self._generate_content(prompt)

    def process_full_pipeline(self, raw_transcript: str) -> dict:
        """Runs the complete transcript processing pipeline.

        Args:
            raw_transcript: The raw Kinyarwanda transcript.

        Returns:
            A dictionary containing the cleaned transcript, Kinyarwanda summary,
            English summary, and a status indicator.
        """
        try:
            cleaned = self.fix_orthography(raw_transcript)
            summary_rw = self.summarize_kinyarwanda(cleaned)
            summary_en = self.translate_to_english(summary_rw)

            return {
                "cleaned": cleaned,
                "summary_rw": summary_rw,
                "summary_en": summary_en,
                "status": "success",
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

# Summarization pipeline optimized and tested for chunked long-text summarization.
