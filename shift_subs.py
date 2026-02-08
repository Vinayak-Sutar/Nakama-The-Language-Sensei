import re
import sys
import os

def shift_time(match, seconds_to_shift, precision=2):
    time_str = match.group(0)
    parts = time_str.split(':')
    
    # Handle optional hours (MM:SS.mmm) vs (H:MM:SS.mmm)
    if len(parts) == 2:
        h = 0
        m = int(parts[0])
        s = float(parts[1])
    else:
        h = int(parts[0])
        m = int(parts[1])
        s = float(parts[2])
    
    total_seconds = h * 3600 + m * 60 + s
    new_total = total_seconds + seconds_to_shift
    
    if new_total < 0:
        new_total = 0
        
    new_h = int(new_total // 3600)
    remainder = new_total % 3600
    new_m = int(remainder // 60)
    new_s = remainder % 60
    
    if precision == 3:
        return f"{new_h:02d}:{new_m:02d}:{new_s:06.3f}"
    else:
        # ASS standard is 1 digit hour if < 10? Actually typical is H:MM:SS.cc
        # But this script previously output new_h as decimal.
        # Let's keep ASS simple: H:MM:SS.cc
        return f"{new_h}:{new_m:02d}:{new_s:05.2f}"

def process_file(filepath, shift_amount):
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        return

    ext = os.path.splitext(filepath)[1].lower()
    is_vtt = ext == '.vtt'
    precision = 3 if is_vtt else 2

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex to find timestamps
    # ASS: H:MM:SS.cc (e.g., 0:00:02.73)
    # VTT: HH:MM:SS.mmm (e.g., 00:00:02.168) or MM:SS.mmm
    
    # Matches H:MM:SS.cc or HH:MM:SS.mmm
    pattern = r'\d{1,2}:\d{2}:\d{2}\.\d{2,3}'
    
    # Also handle MM:SS.mmm if it occurs (rare in this specific file but good to have)
    # But regex above requires 2 colons.
    
    new_content = re.sub(pattern, lambda m: shift_time(m, shift_amount, precision), content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Shifted timestamps in {filepath} by {shift_amount} seconds.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 shift_subs.py <subtitle_file> <seconds_to_shift>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    try:
        shift_amount = float(sys.argv[2])
    except ValueError:
        print("Error: Shift amount must be a number.")
        sys.exit(1)
        
    process_file(filepath, shift_amount)
