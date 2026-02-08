#!/usr/bin/env python3
"""
Project Nakama - Subtitle Pipeline
Converts Japanese + English subtitles → Color-coded dual ASS file using Gemini API
"""

import os
import re
from typing import List, Tuple
from dataclasses import dataclass
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
import pysrt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class SubtitleLine:
    """Represents a single subtitle entry"""
    index: int
    start_time: str  # Format: H:MM:SS.cc
    end_time: str
    japanese: str = ""
    romaji: str = ""
    english: str = ""
    tagged_romaji: str = ""
    tagged_english: str = ""

class SubtitlePipeline:
    """Main pipeline for processing subtitles with Gemini"""
    
    def __init__(self, api_key: str = None, batch_size: int = 20, use_ollama: bool = False, ollama_url: str = "http://localhost:11434"):
        """Initialize pipeline with Gemini API key or Ollama"""
        self.batch_size = batch_size
        self.use_ollama = use_ollama
        
        if use_ollama:
            print(f"🦙 Using Ollama at {ollama_url}")
            self.llm = ChatOllama(
                model="llama3.2",  # or any model you have installed
                base_url=ollama_url,
                temperature=0.1
            )
        else:
            self.api_key = api_key or os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY not found in environment")
            print(f"🤖 Using Gemini API")
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-3-flash-preview",  # Gemini 3 preview model
                google_api_key=self.api_key,
                temperature=0.1  # Low temperature to reduce hallucination
            )
        
    def parse_subtitle_file(self, filepath: str) -> List[Tuple[str, str, str]]:
        """Parse subtitle file and extract (start, end, text) tuples"""
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == '.srt':
            return self._parse_srt(filepath)
        elif ext == '.ass':
            return self._parse_ass(filepath)
        elif ext == '.vtt':
            return self._parse_vtt(filepath)
        else:
            raise ValueError(f"Unsupported format: {ext}")
    
    def _parse_srt(self, filepath: str) -> List[Tuple[str, str, str]]:
        """Parse SRT file"""
        subs = pysrt.open(filepath, encoding='utf-8')
        return [(self._srt_to_ass_time(sub.start), 
                 self._srt_to_ass_time(sub.end), 
                 sub.text.replace('\n', ' ')) 
                for sub in subs]
    
    def _parse_ass(self, filepath: str) -> List[Tuple[str, str, str]]:
        """Parse ASS file"""
        dialogues = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('Dialogue:'):
                    parts = line.split(',', 9)
                    if len(parts) >= 10:
                        start = parts[1].strip()
                        end = parts[2].strip()
                        text = parts[9].strip()
                        # Remove existing color tags
                        text = re.sub(r'\{[^}]+\}', '', text)
                        dialogues.append((start, end, text))
        return dialogues
    
    def _parse_vtt(self, filepath: str) -> List[Tuple[str, str, str]]:
        """Parse VTT file"""
        dialogues = []
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if '-->' in line:
                    times = line.split('-->')
                    start = self._vtt_to_ass_time(times[0].strip())
                    end = self._vtt_to_ass_time(times[1].strip().split()[0])
                    i += 1
                    text = []
                    while i < len(lines) and lines[i].strip():
                        # Remove VTT tags
                        clean = re.sub(r'<[^>]+>', '', lines[i].strip())
                        text.append(clean)
                        i += 1
                    dialogues.append((start, end, ' '.join(text)))
                i += 1
        return dialogues
    
    def _srt_to_ass_time(self, srt_time) -> str:
        """Convert SRT time (00:00:02,730) to ASS (0:00:02.73)"""
        time_str = str(srt_time)
        return time_str.replace(',', '.')[:-1]  # Remove last digit
    
    def _vtt_to_ass_time(self, vtt_time: str) -> str:
        """Convert VTT time (00:00:02.730) to ASS (0:00:02.73)"""
        parts = vtt_time.split(':')
        h = int(parts[0])
        m = parts[1]
        s = parts[2][:5]  # Take only 2 decimal places
        return f"{h}:{m}:{s}"
    
    def convert_to_romaji(self, japanese_lines: List[str]) -> List[str]:
        """Convert Japanese to Romaji using Gemini (batch processing)"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a precise Japanese to Romaji converter.
Convert ONLY the Japanese text to Romaji. Do not translate, do not add explanations.
Maintain the exact same line structure. Return each line on a new line."""),
            ("human", "{japanese_text}")
        ])
        
        chain = prompt | self.llm
        
        batch_text = "\n".join(japanese_lines)
        response = chain.invoke({"japanese_text": batch_text})
        
        romaji_lines = response.content.strip().split('\n')
        return romaji_lines[:len(japanese_lines)]  # Ensure same count
    
    def apply_grammar_tagging(self, romaji_lines: List[str], english_lines: List[str]) -> List[Tuple[str, str]]:
        """Apply grammar color tagging using Gemini"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Japanese grammar expert. Tag grammatical elements with ASS color codes:

COLOR CODES (BGR format):
- Subject/Topic (は, が): {{\\c&HFFFF00&}}
- Object (を, に, へ): {{\\c&H00FFFF&}}
- Verb/Action: {{\\c&H00FF00&}}
- Default/Particles: {{\\c&HFFFFFF&}}

INSTRUCTIONS:
1. For each Japanese Romaji line, identify grammatical elements
2. Wrap each element with appropriate color code
3. Apply SAME grammar colors to corresponding English translation
4. Return format: ROMAJI_LINE|||ENGLISH_LINE
5. Do NOT hallucinate. Use ONLY the lines provided.
6. Maintain exact line count and order.

EXAMPLE:
Input Romaji: Ore wa kaizoku-ou ni naru
Input English: I will become the Pirate King
Output: {{\\c&HFFFF00&}}Ore{{\\c&HFFFFFF&}} wa {{\\c&H00FFFF&}}kaizoku-ou{{\\c&HFFFFFF&}} ni {{\\c&H00FF00&}}naru{{\\c&HFFFFFF&}}|||{{\\c&HFFFF00&}}I{{\\c&HFFFFFF&}} will {{\\c&H00FF00&}}become{{\\c&HFFFFFF&}} the {{\\c&H00FFFF&}}Pirate King{{\\c&HFFFFFF&}}"""),
            ("human", """Tag these lines:

ROMAJI:
{romaji_lines}

ENGLISH:
{english_lines}""")
        ])
        
        chain = prompt | self.llm
        
        romaji_text = "\n".join(romaji_lines)
        english_text = "\n".join(english_lines)
        
        response = chain.invoke({
            "romaji_lines": romaji_text,
            "english_lines": english_text
        })
        
        # Parse response
        tagged_pairs = []
        for line in response.content.strip().split('\n'):
            if '|||' in line:
                romaji, english = line.split('|||', 1)
                tagged_pairs.append((romaji.strip(), english.strip()))
        
        return tagged_pairs
    
    def generate_ass_file(self, subtitles: List[SubtitleLine], output_path: str):
        """Generate final ASS file"""
        
        ass_template = """[Script Info]
Title: Project Nakama - Color-Coded Dual Subtitles
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 640
PlayResY: 360
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Romaji_Main,Arial,18,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1,1,2,10,10,35,1
Style: English_Main,Arial,16,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,1,2,10,10,15,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text

"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ass_template)
            
            for sub in subtitles:
                # Romaji line
                f.write(f"Dialogue: 0,{sub.start_time},{sub.end_time},Romaji_Main,,0,0,0,,{sub.tagged_romaji}\n")
                # English line
                f.write(f"Dialogue: 0,{sub.start_time},{sub.end_time},English_Main,,0,0,0,,{sub.tagged_english}\n")
                f.write("\n")
    
    def process(self, japanese_file: str, english_file: str, output_file: str):
        """Main processing pipeline"""
        print(f"🎌 Project Nakama - Subtitle Pipeline")
        print(f"📥 Input: {japanese_file} + {english_file}")
        
        # Parse files
        print("📖 Parsing subtitle files...")
        jp_subs = self.parse_subtitle_file(japanese_file)
        en_subs = self.parse_subtitle_file(english_file)
        
        if len(jp_subs) != len(en_subs):
            print(f"⚠️  Warning: Line count mismatch (JP: {len(jp_subs)}, EN: {len(en_subs)})")
        
        subtitles = []
        total_batches = (len(jp_subs) + self.batch_size - 1) // self.batch_size
        
        # Process in batches
        for batch_idx in range(0, len(jp_subs), self.batch_size):
            batch_num = batch_idx // self.batch_size + 1
            print(f"\n🔄 Processing batch {batch_num}/{total_batches}...")
            
            batch_jp = jp_subs[batch_idx:batch_idx + self.batch_size]
            batch_en = en_subs[batch_idx:batch_idx + self.batch_size]
            
            # Step 1: Convert to Romaji
            print(f"  ✓ Converting {len(batch_jp)} lines to Romaji...")
            jp_texts = [text for _, _, text in batch_jp]
            romaji_texts = self.convert_to_romaji(jp_texts)
            
            # Step 2: Apply grammar tagging
            print(f"  ✓ Applying grammar color tags...")
            en_texts = [text for _, _, text in batch_en]
            tagged_pairs = self.apply_grammar_tagging(romaji_texts, en_texts)
            
            # Build subtitle objects
            for i, ((start, end, _), (tagged_romaji, tagged_english)) in enumerate(zip(batch_jp, tagged_pairs)):
                sub = SubtitleLine(
                    index=batch_idx + i,
                    start_time=start,
                    end_time=end,
                    japanese=jp_texts[i] if i < len(jp_texts) else "",
                    romaji=romaji_texts[i] if i < len(romaji_texts) else "",
                    english=en_texts[i] if i < len(en_texts) else "",
                    tagged_romaji=tagged_romaji,
                    tagged_english=tagged_english
                )
                subtitles.append(sub)
        
        # Generate output
        print(f"\n💾 Generating ASS file: {output_file}")
        self.generate_ass_file(subtitles, output_file)
        print(f"✅ Done! Created {len(subtitles)} subtitle pairs")


if __name__ == "__main__":
    import sys
    
    # Check for --ollama flag
    use_ollama = "--ollama" in sys.argv
    if use_ollama:
        sys.argv.remove("--ollama")
    
    if len(sys.argv) < 3:
        print("Usage: python subtitle_pipeline.py [--ollama] <japanese_file> <english_file> [output_file]")
        print("Example: python subtitle_pipeline.py ope1jap.vtt ope1eng.ass one_piece_001_dual.ass")
        print("         python subtitle_pipeline.py --ollama ope1jap.vtt ope1eng.ass one_piece_001_dual.ass")
        sys.exit(1)
    
    japanese_file = sys.argv[1]
    english_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else "output_dual.ass"
    
    pipeline = SubtitlePipeline(batch_size=20, use_ollama=use_ollama, ollama_url="http://localhost:11434")
    pipeline.process(japanese_file, english_file, output_file)
