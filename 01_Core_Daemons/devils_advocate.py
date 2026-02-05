# poe: name=Devils-Advocate

class DevilsAdvocate:
    def __init__(self, pro_model=None, con_model=None, judge_model=None):
        """
        Initialize the debate with configurable AI models.
        
        Args:
            pro_model: Model to argue FOR the topic (default: first available)
            con_model: Model to argue AGAINST the topic (default: second available)  
            judge_model: Model to provide neutral analysis (default: third available)
        """
        # Default to generic model identifiers if not specified
        self.pro_model = pro_model or "model-1"
        self.con_model = con_model or "model-2"
        self.judge_model = judge_model or "model-3"
    
    def run(self):
        topic = poe.query.text.strip()
        
        if not topic:
            raise poe.BotError("Please provide a topic to debate! For example: 'Pineapple belongs on pizza'")
        
        with poe.start_message() as msg:
            msg.write("⚔️ **Devil's Advocate Debate**\n\n")
            msg.write(f"**Topic:** {topic}\n\n")
            msg.write("---\n\n")
            
            # Round 1: Opening arguments (parallel since they're independent)
            msg.write("## 🎯 Round 1: Opening Arguments\n\n")
            
            pro_response, con_response = poe.parallel(
                lambda: poe.call(
                    self.pro_model,
                    f"You are a skilled debater. Argue strongly IN FAVOR of this position. Be persuasive, use compelling logic and examples.\n\nTopic: {topic}\n\nGive your opening argument (2-3 paragraphs). Do not hedge or acknowledge the other side yet."
                ),
                lambda: poe.call(
                    self.con_model,
                    f"You are a skilled debater. Argue strongly AGAINST this position. Be persuasive, use compelling logic and examples.\n\nTopic: {topic}\n\nGive your opening argument (2-3 paragraphs). Do not hedge or acknowledge the other side yet."
                )
            )
            
            msg.write(f"**🟢 FOR**:\n{pro_response.text}\n\n")
            msg.write(f"**🔴 AGAINST**:\n{con_response.text}\n\n")
            msg.write("---\n\n")
            
            # Round 2: Rebuttals (parallel - each responds to the other's opening)
            msg.write("## ⚡ Round 2: Rebuttals\n\n")
            
            pro_rebuttal, con_rebuttal = poe.parallel(
                lambda t=topic, opp=con_response.text: poe.call(
                    self.pro_model,
                    f"You are debating IN FAVOR of: {t}\n\nYour opponent just argued AGAINST with:\n\n{opp}\n\nProvide a sharp rebuttal addressing their key points (1-2 paragraphs)."
                ),
                lambda t=topic, opp=pro_response.text: poe.call(
                    self.con_model,
                    f"You are debating AGAINST: {t}\n\nYour opponent just argued IN FAVOR with:\n\n{opp}\n\nProvide a sharp rebuttal addressing their key points (1-2 paragraphs)."
                )
            )
            
            msg.write(f"**🟢 FOR responds**:\n{pro_rebuttal.text}\n\n")
            msg.write(f"**🔴 AGAINST responds**:\n{con_rebuttal.text}\n\n")
            msg.write("---\n\n")
            
            msg.write("## 🤝 Neutral Analysis\n\n")
        
        # Final synthesis streamed to chat
        poe.call(
            self.judge_model,
            f"""You are a neutral debate moderator. Summarize this debate fairly.

**Topic:** {topic}

**FOR (Opening + Rebuttal):**
{pro_response.text}

{pro_rebuttal.text}

**AGAINST (Opening + Rebuttal):**
{con_response.text}

{con_rebuttal.text}

Provide:
1. The strongest point from each side
2. Any common ground or nuance both missed
3. Key questions the reader should consider when forming their own opinion

Be balanced and help the reader think critically.""",
            output=poe.default_chat
        )


if __name__ == "__main__":
    # Example usage with default models
    bot = DevilsAdvocate()
    bot.run()
    
    # Example usage with custom models:
    # bot = DevilsAdvocate(
    #     pro_model="gpt-4",
    #     con_model="claude-3", 
    #     judge_model="gemini-pro"
    # )
    # bot.run()
