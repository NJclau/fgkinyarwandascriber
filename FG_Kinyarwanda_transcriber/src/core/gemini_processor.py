import os
import streamlit as st
import google.generativeai as genai
from typing import Optional
from src.config.settings import config

class GeminiProcessor:
    """Process transcripts using Google Gemini API"""
    
    def __init__(self):
        """Initialize Gemini with API key from secrets"""
        api_key = config.gemini_api_key
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in secrets or environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        print("Gemini processor initialized")
    
    def _generate_content(self, prompt: str, max_retries: int = 3) -> str:
        """Generate content with retry logic"""
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Gemini API error after {max_retries} attempts: {str(e)}")
                print(f"Retry {attempt + 1}/{max_retries} after error: {str(e)}")
                continue
    
    def fix_orthography(self, raw_text: str) -> str:
        """Fix Kinyarwanda orthography, grammar, and punctuation"""
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
        """Summarize key insights in Kinyarwanda"""
        prompt = f"""You are an expert focus group analyst fluent in Kinyarwanda.

Analyze this Kinyarwanda transcript and provide a comprehensive summary in Kinyarwanda.

Your summary should include:
1. Ingingo z'ingenzi (Key points discussed)
2. Ibitekerezo by'abagize inama (Main opinions/perspectives)
3. Ibibazo byavuzwe (Concerns raised)
4. Ibyifuzo n'ibyiyumviro (Recommendations/conclusions)

Keep the summary in Kinyarwanda language. Be thorough but concise.

Transcript:
{cleaned_text}

Summary in Kinyarwanda:"""
        
        return self._generate_content(prompt)
    
    def translate_to_english(self, kinyarwanda_summary: str) -> str:
        """Translate Kinyarwanda summary to English"""
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
        """Run complete processing pipeline"""
        try:
            cleaned = self.fix_orthography(raw_transcript)
            summary_rw = self.summarize_kinyarwanda(cleaned)
            summary_en = self.translate_to_english(summary_rw)
            
            return {
                'cleaned': cleaned,
                'summary_rw': summary_rw,
                'summary_en': summary_en,
                'status': 'success'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
