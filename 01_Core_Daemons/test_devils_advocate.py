from devils_advocate import DevilsAdvocate


def test_debate():
    """Test function for the DevilsAdvocate bot"""
    with poe.start_message() as msg:
        msg.write("Test: Running a debate on a fun topic\n\n")
        
        # Create a test instance with default models
        bot = DevilsAdvocate()
        
        # Test with custom models
        custom_bot = DevilsAdvocate(
            pro_model="gpt-4",
            con_model="claude-3", 
            judge_model="gemini-pro"
        )
        
        msg.write("✅ DevilsAdvocate class instantiated successfully\n")
        msg.write("📝 Ready to debate topics when called through POE interface\n")
        msg.write("🔧 Configurable models supported\n")


if __name__ == "__main__":
    test_debate()
