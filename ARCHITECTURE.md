# Project Nakama - System Architecture

## Pipeline Architecture

```mermaid
flowchart TB
    subgraph Input["📥 Input Files"]
        JP[Japanese Subtitle<br/>VTT/ASS/SRT]
        EN[English Subtitle<br/>VTT/ASS/SRT]
    end
    
    subgraph Parser["📖 Subtitle Parser"]
        P1[VTT Parser]
        P2[ASS Parser]
        P3[SRT Parser]
        P1 --> NORM[Normalize to<br/>Start/End/Text]
        P2 --> NORM
        P3 --> NORM
    end
    
    subgraph Batch["⚙️ Batch Processor<br/>20 lines per batch"]
        BATCH[Batch Manager]
    end
    
    subgraph AI["🤖 AI Processing"]
        choice{AI Backend?}
        GEMINI["Google Gemini API<br/>gemini-3-flash-preview"]
        OLLAMA["Ollama Local<br/>llama3.2"]
        choice -->|API Available| GEMINI
        choice -->|Offline/Fallback| OLLAMA
    end
    
    subgraph Step1["Step 1: Romaji Conversion"]
        R1[Japanese Text]
        R2[Convert to Romaji]
        R3[Romaji Output]
        R1 --> R2
        R2 --> R3
    end
    
    subgraph Step2["Step 2: Grammar Tagging"]
        G1[Romaji + English]
        G2["Identify Grammar:<br/>Subject/Object/Verb"]
        G3["Apply Color Codes:<br/>Cyan/Yellow/Green"]
        G4[Tagged Lines]
        G1 --> G2
        G2 --> G3
        G3 --> G4
    end
    
    subgraph Output["💾 Output Generation"]
        ASS["ASS File Generator<br/>Dual-Layer Subtitles"]
        FINAL["✨ Final Output<br/>episode_dual.ass"]
    end
    
    JP --> Parser
    EN --> Parser
    NORM --> BATCH
    BATCH --> AI
    AI --> Step1
    Step1 --> Step2
    Step2 --> Output
    ASS --> FINAL
    
    style GEMINI fill:#4285f4,color:#fff
    style OLLAMA fill:#00d084,color:#fff
    style FINAL fill:#0f9d58,color:#fff
```

## Color Coding System

```mermaid
graph LR
    subgraph "ASS Color Codes (BGR Format)"
        S["Subject/Topic<br/>は, が<br/>{\\c&HFFFF00&}"]
        O["Object<br/>を, に, へ<br/>{\\c&H00FFFF&}"]
        V["Verb/Action<br/>{\\c&H00FF00&}"]
        D["Default/Particles<br/>{\\c&HFFFFFF&}"]
    end
    
    style S fill:#00ffff,color:#000
    style O fill:#ffff00,color:#000
    style V fill:#00ff00,color:#000
    style D fill:#ffffff,color:#000
```

## Technology Stack

```mermaid
graph TB
    subgraph Core["Core Technologies"]
        PY[Python 3.10+]
        LC[LangChain]
    end
    
    subgraph AI["AI Models"]
        G[Google Gemini API]
        O[Ollama llama3.2]
    end
    
    subgraph NLP["NLP Libraries"]
        J[Janome]
        C[Cutlet]
        F[Fugashi]
    end
    
    subgraph Utils["Utilities"]
        SR[pysrt]
        DE[python-dotenv]
    end
    
    PY --> LC
    LC --> G
    LC --> O
    PY --> NLP
    PY --> Utils
    
    style G fill:#4285f4,color:#fff
    style O fill:#00d084,color:#fff
```

## Data Flow Example

**Input:**
```
Japanese: 俺は海賊王になる
English: I will become the Pirate King
```

**Processing:**
1. **Romaji Conversion**: `Ore wa kaizoku-ō ni naru`
2. **Grammar Analysis**:
   - `Ore` (I) → Subject → Cyan
   - `kaizoku-ō` (Pirate King) → Object → Yellow
   - `naru` (become) → Verb → Green

**Output:**
```ass
Dialogue: {...,Romaji_Main,...,{\c&HFFFF00&}Ore{\c&HFFFFFF&} wa {\c&H00FFFF&}kaizoku-ō{\c&HFFFFFF&} ni {\c&H00FF00&}naru{\c&HFFFFFF&}
Dialogue: {...,English_Main,...,{\c&HFFFF00&}I{\c&HFFFFFF&} will {\c&H00FF00&}become{\c&HFFFFFF&} the {\c&H00FFFF&}Pirate King{\c&HFFFFFF&}
```

## Performance Metrics

- **Batch Size**: 20 lines
- **Processing Speed**: ~50-100 lines/minute (depends on AI backend)
- **Memory Usage**: Minimal (streaming batch processing)
- **Token Usage**: ~27K tokens per 20-min episode
- **Output Size**: ~36-70 KB per episode
