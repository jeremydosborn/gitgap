"""Survey collection - CLI prompts for gathering responses."""

from .questions import QUESTION


def ask_question() -> int | None:
    """
    Present the survey question and collect response.
    
    Returns:
        int: Response value (0-5), or None if invalid/cancelled
    """
    print(QUESTION["text"])
    
    while True:
        try:
            response = input("\nYour response (0-5): ").strip()
            
            if response.lower() in ('q', 'quit', 'exit', ''):
                return None
            
            value = int(response)
            min_val, max_val = QUESTION["valid_range"]
            
            if min_val <= value <= max_val:
                if value == 0:
                    print("\nNo problem. Your response will not be recorded.")
                    return None
                return value
            else:
                print(f"Please enter a number between {min_val} and {max_val}")
                
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\n")
            return None