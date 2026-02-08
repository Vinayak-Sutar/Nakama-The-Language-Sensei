import sys
from janome.tokenizer import Tokenizer
import cutlet

# Color Constants (ASS format)
COLOR_SUBJECT = r"{\c&HFFFF00&}"  # Cyan
COLOR_OBJECT = r"{\c&H32CD32&}"   # Green
COLOR_VERB = r"{\c&H008CFF&}"     # Orange
COLOR_OTHER = r"{\c&HFFFFFF&}"    # White (Default)
COLOR_PARTICLE = r"{\c&HBEBEBE&}" # Greyish

def tag_sentence(text):
    """
    Analyze Japanese text and apply grammar-based color tagging.
    """
    t = Tokenizer()
    tokens = list(t.tokenize(text))
    
    tagged_text = ""
    current_color = COLOR_OTHER
    
    # Simple heuristic-based tagging
    # Iterate through tokens and color based on particles/pos
    
    buffer_text = ""
    chunk_color = COLOR_OTHER
    
    for i, token in enumerate(tokens):
        word = token.surface
        pos = token.part_of_speech.split(',')
        
        # print(f"{word}: {pos}") # Debug info
        
        # Check for particles that mark grammar roles
        if pos[0] == '助詞': # Particle
            if word == 'は' or word == 'が':
                # Previous chunk was Likely Subject
                tagged_text += f"{COLOR_SUBJECT}{buffer_text}{word}{COLOR_OTHER}"
                buffer_text = ""
                continue
            elif word == 'を' or word == 'に':
                # Previous chunk was Likely Object
                tagged_text += f"{COLOR_OBJECT}{buffer_text}{word}{COLOR_OTHER}"
                buffer_text = ""
                continue
            else:
                # Other particles
                tagged_text += f"{chunk_color}{buffer_text}{word}{COLOR_OTHER}"
                buffer_text = ""
                continue
        
        elif pos[0] == '動詞': # Verb
             # If strictly a verb
             tagged_text += f"{chunk_color}{buffer_text}{COLOR_VERB}{word}{COLOR_OTHER}"
             buffer_text = ""
             continue
             
        # Accumulate words until we hit a marker
        buffer_text += word
        
    # Append remaining
    if buffer_text:
        tagged_text += f"{chunk_color}{buffer_text}"
        
    return tagged_text

def to_romaji(text):
    katsu = cutlet.Cutlet()
    return katsu.romaji(text)

if __name__ == "__main__":
    sample_text = "私は海賊王になる男だ！"
    if len(sys.argv) > 1:
        sample_text = sys.argv[1]
        
    print(f"Original: {sample_text}")
    
    romaji = to_romaji(sample_text)
    print(f"Romaji: {romaji}")
    
    tagged = tag_sentence(sample_text)
    print(f"Tagged: {tagged}")
