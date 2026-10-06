import random
import sys


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


def generate_sequence(target: int):
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


def main():
    """Command-line interface."""
    if len(sys.argv) > 1:
        try:
            target = int(sys.argv[1])
        except ValueError:
            print("Error: Please provide a valid integer")
            sys.exit(1)
    else:
        try:
            target = int(input("Enter a target number: "))
        except ValueError:
            print("Error: Please enter a valid integer")
            sys.exit(1)
    
    generate_sequence(target)


if __name__ == "__main__":
    main()
