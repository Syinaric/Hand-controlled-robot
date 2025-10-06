#!/usr/bin/env python3
"""
Sensitivity Configuration for Hand Gesture Controller

This script allows you to easily adjust the sensitivity parameters
for fist detection without editing the main code.
"""

# Sensitivity Parameters
SENSITIVITY_CONFIGS = {
    "very_sensitive": {
        "tolerance_pixels": 15,
        "required_fingers": 2,
        "description": "Very sensitive - only 2 fingers need to be closed"
    },
    "sensitive": {
        "tolerance_pixels": 10,
        "required_fingers": 3,
        "description": "Sensitive - 3 fingers need to be closed (current)"
    },
    "moderate": {
        "tolerance_pixels": 5,
        "required_fingers": 4,
        "description": "Moderate - 4 fingers need to be closed"
    },
    "strict": {
        "tolerance_pixels": 0,
        "required_fingers": 5,
        "description": "Strict - all 5 fingers must be closed"
    }
}

def print_configs():
    """Print available sensitivity configurations."""
    print("🎯 Hand Gesture Sensitivity Configurations")
    print("=" * 50)
    
    for i, (name, config) in enumerate(SENSITIVITY_CONFIGS.items(), 1):
        print(f"{i}. {name.upper()}")
        print(f"   Tolerance: {config['tolerance_pixels']} pixels")
        print(f"   Required fingers: {config['required_fingers']}/5")
        print(f"   Description: {config['description']}")
        print()

def get_config_choice():
    """Get user's sensitivity choice."""
    print_configs()
    
    while True:
        try:
            choice = input("Enter your choice (1-4, or press Enter for 'sensitive'): ").strip()
            
            if not choice:
                return "sensitive"
            
            choice_num = int(choice)
            if 1 <= choice_num <= 4:
                config_names = list(SENSITIVITY_CONFIGS.keys())
                return config_names[choice_num - 1]
            else:
                print("Please enter a number between 1 and 4.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nUsing default 'sensitive' configuration.")
            return "sensitive"

def generate_code(config_name):
    """Generate the code snippet for the chosen configuration."""
    config = SENSITIVITY_CONFIGS[config_name]
    
    code = f"""
# Update these values in hand_gesture_controller.py
# In the detect_fist() and count_closed_fingers() methods:

tolerance_pixels = {config['tolerance_pixels']}  # Tolerance in pixels for detection
required_fingers = {config['required_fingers']}   # Minimum number of fingers that must be closed (out of 5)
"""
    
    return code

def main():
    """Main configuration function."""
    print("🤖 Hand Gesture Controller - Sensitivity Configuration")
    print("=" * 60)
    print("This tool helps you choose the right sensitivity for fist detection.")
    print("You can then update the values in hand_gesture_controller.py")
    print()
    
    choice = get_config_choice()
    config = SENSITIVITY_CONFIGS[choice]
    
    print(f"\n✅ You selected: {choice.upper()}")
    print(f"📝 Description: {config['description']}")
    print()
    
    print("🔧 Code to update in hand_gesture_controller.py:")
    print("-" * 50)
    print(generate_code(choice))
    
    print("📋 Steps to apply changes:")
    print("1. Open hand_gesture_controller.py")
    print("2. Find the detect_fist() method (around line 95)")
    print("3. Find the count_closed_fingers() method (around line 151)")
    print("4. Update the tolerance_pixels and required_fingers values")
    print("5. Restart the hand gesture controller")
    print()
    
    print("💡 Tips:")
    print("- Higher tolerance_pixels = more forgiving detection")
    print("- Lower required_fingers = easier to trigger fist")
    print("- Start with 'sensitive' and adjust based on your needs")

if __name__ == "__main__":
    main()
