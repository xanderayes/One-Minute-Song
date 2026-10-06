import random
import sys
from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo


def find_gcd(a: int, b: int) -> int:
    """Find greatest common divisor using Euclidean algorithm."""
    return a if b == 0 else find_gcd(b, a % b)


def format_to_fraction(num: float) -> str:
    """Convert a number to a simplified fraction (eighths)."""
    numerator = round(num * 2)
    denominator = 8
    
    gcd = find_gcd(numerator, denominator)
    simplified_num = numerator // gcd
    simplified_den = denominator // gcd
    
    return f"{simplified_num}/{simplified_den}"


def format_number(num: float) -> str:
    """Format number, showing multiples of 4 for values > 7."""
    if num > 7:
        fours = int(num // 4)
        remainder = num - (fours * 4)
        if remainder == 0:
            return f"({fours} * 4)"
        else:
            return f"({fours} * 4 + {remainder})"
    return str(num)


def format_bar(num: float) -> str:
    """Format number as fraction bar notation."""
    if num > 7:
        fours = int(num // 4)
        remainder = num - (fours * 4)
        remainder_fraction = format_to_fraction(remainder)
        if remainder == 0:
            return f"({fours} * 4/4)"
        else:
            return f"({fours} * 4/4 + {remainder_fraction})"
    return format_to_fraction(num)


def try_generate_sequence(target: float):
    """Attempt to generate a valid sequence with 3 unique numbers."""
    unique_numbers = set()
    max_val = max(0.5, target / 2)
    
    while len(unique_numbers) < 3:
        raw_num = random.random() * (max_val - 0.5) + 0.5
        rounded_num = round(raw_num * 2) / 2
        unique_numbers.add(rounded_num)
    
    numbers = list(unique_numbers)
    min_number = min(numbers)
    
    sequence = []
    remaining = target
    max_numbers = 10
    
    while remaining > 0:
        if len(sequence) >= max_numbers:
            return None
        
        valid_numbers = [n for n in numbers if n <= remaining]
        
        if len(valid_numbers) == 0:
            return None
        
        chosen = random.choice(valid_numbers)
        sequence.append(chosen)
        remaining -= chosen
        
        if remaining < min_number and remaining > 0:
            if len(sequence) > 0:
                last = sequence.pop()
                remaining += last
                if remaining in numbers or remaining == 0:
                    if remaining > 0:
                        sequence.append(remaining)
                    remaining = 0
                else:
                    return None
            else:
                return None
    
    if len(sequence) == 1 and target >= min_number * 2:
        return None
    
    return sequence if len(sequence) >= 2 else None


def generate_random_sequence(target: float):
    """Generate a random sequence that sums to target."""
    if target < 1.5:
        return None
    
    max_attempts = 100
    for _ in range(max_attempts):
        result = try_generate_sequence(target)
        if result:
            return result
    
    return [target]


def parse_bar_to_beats(bar_str: str) -> list:
    """Parse bar notation string and return list of beat durations."""
    beats = []
    
    # Handle simple fraction (e.g., "5/4")
    if '/' in bar_str and '(' not in bar_str:
        parts = bar_str.split('/')
        numerator = float(parts[0])
        denominator = float(parts[1])
        beats.append(numerator / denominator)
        return beats
    
    # Handle complex notation (e.g., "(4 * 4/4 + 3/8)")
    if '(' in bar_str and ')' in bar_str:
        content = bar_str[1:-1]  # Remove parentheses
        components = content.split(' + ')
        
        for comp in components:
            comp = comp.strip()
            if '*' in comp:
                # Handle multiplication (e.g., "4 * 4/4")
                mult_parts = comp.split(' * ')
                count = int(mult_parts[0].strip())
                frac_parts = mult_parts[1].strip().split('/')
                numerator = float(frac_parts[0])
                denominator = float(frac_parts[1])
                beat_duration = numerator / denominator
                beats.extend([beat_duration] * count)
            else:
                # Handle simple fraction (e.g., "3/8")
                frac_parts = comp.split('/')
                numerator = float(frac_parts[0])
                denominator = float(frac_parts[1])
                beats.append(numerator / denominator)
    
    return beats


def generate_midi(sequence: list, bpm: int):
    """Generate MIDI file from sequence with given BPM."""
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    
    # Set tempo
    track.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm)))
    
    # MIDI parameters
    note = 60  # Middle C
    velocity = 64
    
    current_time = 0
    
    for num in sequence:
        bar_str = format_bar(num)
        beats = parse_bar_to_beats(bar_str)
        
        for beat_duration in beats:
            # Convert beats to ticks (assuming 480 ticks per quarter note)
            ticks = int(beat_duration * 480)
            
            # Note on
            track.append(Message('note_on', note=note, velocity=velocity, time=current_time))
            # Note off
            track.append(Message('note_off', note=note, velocity=velocity, time=ticks))
            
            current_time = 0  # Reset time after first note
    
    mid.save('output.midi')
    print(f"MIDI file saved as output.midi (BPM: {bpm})")


def generate_sequence(target: int, bpm: int = 120):
    """Main function to generate and display sequence."""
    if target < 2:
        print("Error: Please enter a valid integer (minimum 2)")
        return
    
    sequence = generate_random_sequence(target)
    
    if not sequence:
        print("Error: Target too small for the constraints")
        return
    
    # Display sequence
    print(f"Random sequence: {' + '.join(format_number(num) for num in sequence)}")
    print(f"= {sum(sequence)}")
    
    # Display parts with letters (assigned by order of first appearance)
    letter_map = {}
    letter_index = 0
    for num in sequence:
        if num not in letter_map:
            letter_map[num] = chr(65 + letter_index)
            letter_index += 1
    parts = ' '.join(letter_map[num] for num in sequence)
    print(f"Parts: {parts}")
    
    # Display bars
    bars = ' + '.join(format_bar(num) for num in sequence)
    print(f"Bars: {bars}")
    
    # Generate MIDI file
    generate_midi(sequence, bpm)


def main():
    """Command-line interface."""
    if len(sys.argv) > 1:
        try:
            target = int(sys.argv[1])
        except ValueError:
            print("Error: Please provide a valid integer")
            sys.exit(1)
        
        bpm = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    else:
        try:
            target = int(input("Enter a target number: "))
        except ValueError:
            print("Error: Please enter a valid integer")
            sys.exit(1)
        
        try:
            bpm = int(input("Enter BPM (default 120): ") or "120")
        except ValueError:
            bpm = 120
    
    generate_sequence(target, bpm)


if __name__ == "__main__":
    main()
