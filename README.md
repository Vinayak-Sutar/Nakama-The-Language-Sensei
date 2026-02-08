# 🎌 Project Nakama: AI-Powered Language Learning Subtitles

> **Color-coded dual subtitles powered by Google Gemini for immersive Japanese learning**

Transform your anime watching into active language learning with grammar-aware, color-coded subtitles that highlight sentence structure in real-time.

---

## 🌟 Features

- **🎨 Grammar Color-Coding**: Visual highlighting of grammatical roles
  - **Cyan** (`&HFFFF00&`): Subjects/Topics (は, が particles)
  - **Yellow** (`&H00FFFF&`): Objects (を, に, へ particles)
  - **Green** (`&H00FF00&`): Verbs and actions
  
- **🌐 Dual-Language Display**: Synchronized Japanese (Romaji) + English subtitles

- **🤖 AI-Powered with Gemini**: 
  - Japanese → Romaji conversion
  - Contextual grammar analysis
  - Translation alignment between languages

- **⚡ Automated Pipeline**: Process any subtitle pair with one command

---

## 🧠 How We Use Gemini

**Project Nakama leverages Google's Gemini API via LangChain for advanced linguistic analysis:**

1. **Romaji Conversion**: Batch processing (20 lines) converts Japanese text to Romaji with high accuracy.

2. **Grammar Tagging**: Gemini analyzes sentence structure to identify:
   - Subject markers (particles は, が)
   - Object markers (particles を, に, へ)
   - Verb/action predicates
   - Applies same colors to English translations

3. **Batch Processing**: Efficient 20-line batching prevents hallucination and maintains context.

4. **LangChain Integration**: Structured prompts ensure consistent, reliable output.

**Result**: Production-ready pipeline that generates color-coded learning subtitles automatically.

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/Vinayak-Sutar/Nakama-The-Language-Sensei.git
cd Nakama-The-Language-Sensei

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up API key
cp .env.example .env
# Edit .env and add your Gemini API key
```

### Usage

**Process Subtitle Pair**:
```bash
python subtitle_pipeline.py <japanese_subtitle> <english_subtitle> [output_file]

# Example:
python subtitle_pipeline.py ope1jap.vtt ope1eng.ass one_piece_001_dual.ass
```

**Watch with VLC**:
```bash
vlc your_video.mp4 --sub-file one_piece_001_dual.ass
```

**Utility: Shift Timing**:
```bash
python shift_subs.py <subtitle_file> <seconds>
# Example: shift by +14 seconds
python shift_subs.py ope1eng.ass 14.0
```

---

## 📂 Project Structure

```
nakama-subtitles/
├── subtitle_pipeline.py      # Main processing pipeline (LangChain + Gemini)
├── shift_subs.py              # Timestamp adjuster utility
├── grammar_engine.py          # Offline NLP analyzer (prototype)
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
├── demo/
│   └── ope1dual.ass           # Pre-generated demo file
└── README.md
```

---

## 🎬 Demo

**Video**: [Watch Demo](YOUTUBE_LINK)  
**Live Example**: Load `demo/ope1dual.ass` with One Piece Episode 1

---

## 🛠️ Technologies

- **Google Gemini API** - AI grammar analysis via LangChain
- **LangChain** - Prompt engineering & orchestration
- **Python** - Core implementation
- **Janome** - Japanese tokenization (optional enhancement)
- **ASS Format** - Advanced subtitle styling

---

## 📊 Performance

- **Processing Speed**: ~50-100 lines/minute (depends on API quota)
- **Token Usage**: ~27K tokens per 20-minute episode
- **Accuracy**: High (low temperature + batch constraints reduce hallucination)

---

## 📝 License

MIT License - See [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- Google Gemini team
- LangChain community
- One Piece for demo content

---

**Made with ❤️ for language learners**  
[GitHub](https://github.com/Vinayak-Sutar/Nakama-The-Language-Sensei)
