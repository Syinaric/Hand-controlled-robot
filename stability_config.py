#!/usr/bin/env python3
"""
Stability Configuration for Hand Gesture Controller

This script helps you adjust the stability parameters to prevent
the servo from constantly switching back and forth.
"""

# Stability Configuration Options
STABILITY_CONFIGS = {
    "very_stable": {
        "stability_threshold": 15,
        "history_size": 20,
        "fist_threshold": 0.8,
        "description": "Very stable - requires 80% majority over 20 frames"
    },
    "stable": {
        "stability_threshold": 10,
        "history_size": 15,
        "fist_threshold": 0.7,
        "description": "Stable - requires 70% majority over 15 frames (current)"
    },
    "moderate": {
        "stability_threshold": 8,
        "history_size": 12,
        "fist_threshold": 0.6,
        "description": "Moderate - requires 60% majority over 12 frames"
    },
    "responsive": {
        "stability_threshold": 5,
        "history_size": 8,
        "fist_threshold": 0.5,
        "description": "Responsive - requires 50% majority over 8 frames"
    }
}

def print_configs():
    """Print available stability configurations."""
    print("🎯 Hand Gesture Stability Configurations")
    print("=" * 60)
    print("These settings help prevent the servo from constantly switching")
    print("back and forth when your hand gesture is detected inconsistently.")
    print()
    
    for i, (name, config) in enumerate(STABILITY_CONFIGS.items(), 1):
        print(f"{i}. {name.upper()}")
        print(f"   Stability threshold: {config['stability_threshold']} frames")
        print(f"   History size: {config['history_size']} frames")
        print(f"   Fist threshold: {config['fist_threshold']*100:.0f}% majority")
        print(f"   Description: {config['description']}")
        print()

def get_config_choice():
    """Get user's stability choice."""
    print_configs()
    
    while True:
        try:
            choice = input("Enter your choice (1-4, or press Enter for 'stable'): ").strip()
            
            if not choice:
                return "stable"
            
            choice_num = int(choice)
            if 1 <= choice_num <= 4:
                config_names = list(STABILITY_CONFIGS.keys())
                return config_names[choice_num - 1]
            else:
                print("Please enter a number between 1 and 4.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nUsing default 'stable' configuration.")
            return "stable"

def generate_code(config_name):
    """Generate the code snippet for the chosen configuration."""
    config = STABILITY_CONFIGS[config_name]
    
    code = f"""
# Update these values in hand_gesture_controller.py
# In the __init__ method around line 70:

self.stability_threshold = {config['stability_threshold']}    # Frames needed for stable detection
self.history_size = {config['history_size']}           # Number of recent gestures to consider
self.fist_threshold = {config['fist_threshold']}        # Percentage of recent frames that must be FIST
"""
    
    return code

def main():
    """Main configuration function."""
    print("🤖 Hand Gesture Controller - Stability Configuration")
    print("=" * 60)
    print("This tool helps you choose the right stability settings")
    print("to prevent constant servo switching.")
    print()
    
    choice = get_config_choice()
    config = STABILITY_CONFIGS[choice]
    
    print(f"\n✅ You selected: {choice.upper()}")
    print(f"📝 Description: {config['description']}")
    print()
    
    print("🔧 Code to update in hand_gesture_controller.py:")
    print("-" * 50)
    print(generate_code(choice))
    
    print("📋 Steps to apply changes:")
    print("1. Open hand_gesture_controller.py")
    print("2. Find the __init__ method (around line 70)")
    print("3. Update the stability_threshold, history_size, and fist_threshold values")
    print("4. Restart the hand gesture controller")
    print()
    
    print("💡 Tips:")
    print("- Higher stability_threshold = more frames needed before switching")
    print("- Larger history_size = more frames considered for majority")
    print("- Higher fist_threshold = more consistent detection required")
    print("- Start with 'stable' and adjust based on your needs")
    print()
    
    print("🔍 Current Issues:")
    print("- If servo switches too much: Use 'very_stable' or 'stable'")
    print("- If servo doesn't respond: Use 'moderate' or 'responsive'")
    print("- If detection is inconsistent: Increase fist_threshold")

if __name__ == "__main__":
    main()
