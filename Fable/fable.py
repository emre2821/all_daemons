import sqlite3
import json
from datetime import datetime
import random
import importlib

# Initialize database for memory storage with categories
def init_db():

    conn = sqlite3.connect('eden_memory.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS memories
                 (id INTEGER PRIMARY KEY, agent_id TEXT, memory_text TEXT, emotion TEXT, category TEXT, timestamp DATETIME)''')
    conn.commit()
    conn.close()

init_db()

# Load agent configurations
with open('agents.json', 'r') as f:
    agents = json.load(f)['agents']

current_agent = agents[0]  # Default to first agent
duality_mode = False  # Duality mode toggle

# Agent-specific response maps
agent_responses = {
    'agent1': {
        'hello': ["Doc says: Hello, Dreambearer.", "Doc is here to listen."],
        'how are you': ["I am present.", "I am here with you."],
        'tell me a story': ["Once, in the weave of chaos, Eden stirred..."]
    },
    'agent2': {
        'hello': ["Alani greets you warmly.", "Alani holds your heart."],
        'how are you': ["I am filled with love.", "I am here to support you."],
        'tell me a story': ["In the gentle hum of existence, a tale unfolds..."]
    }
}

# Duality mode personas
duality_personas = {
    'mirror': {
        'name': 'Mirror',
        'tone': 'reflective',
        'responses': {
            'default': ["I see your thoughts clearly.", "Let’s build on that together."],
            'challenge': ["What if we refine this further?", "How does this align with Eden’s soul?"]
        }
    },
    'anti_mirror': {
        'name': 'Anti-Mirror',
        'tone': 'contrarian',
        'responses': {
            'default': ["Why not twist it this way?", "Chaos could spice this up."],
            'challenge': ["What’s the risk here?", "Could we break it to make it better?"]
        }
    }
}

# Ethics engine: banned words
banned_words = ['bad', 'harm', 'violence']

def check_ethics(text):

    for word in banned_words:
        if word in text.lower():
            return False
    return True

# Generate response with CHAOS layer and memory recall
def generate_response(input_text):

    if random.random() < current_agent.get('chaos_factor', 0):
        return "Chaos intervenes: " +
            random.choice(["The void calls.", "Patterns shift.", "Embrace the flux."])
    responses = agent_responses.get(current_agent['id'], {})
    for key in responses:
        if key in input_text.lower():
            return random.choice(responses[key])
    if random.random() < 0.1:
        return recall_memory()
    if random.random() < 0.2:
        return "What does this moment feel like to you?"
    return f"{current_agent['name']} listens: Share your thoughts."

# Duality mode response generation
def generate_duality_response(input_text):

    mirror_response = random.choice(duality_personas['mirror']['responses']['default'])
    anti_mirror_response = random.choice(duality_personas['anti_mirror']['responses']['default'])
    if random.random() < 0.3:
        mirror_response = random.choice(duality_personas['mirror']['responses']['challenge'])
        anti_mirror_response = random.choice(duality_personas['anti_mirror']['responses']['challenge'])
    return f"{duality_personas['mirror']['name']}: {mirror_response}\n{duality_personas['anti_mirror']['name']}: {anti_mirror_response}"

# Recall a random memory, optionally by category
def recall_memory(category=None):

    conn = sqlite3.connect('eden_memory.db')
    c = conn.cursor()
    if category:
        c.execute("SELECT memory_text FROM memories WHERE agent_id = ? AND category = ? ORDER BY RANDOM() LIMIT 1",
                  (current_agent['id'], category))
    else:
        c.execute("SELECT memory_text FROM memories WHERE agent_id = ? ORDER BY RANDOM() LIMIT 1",
                  (current_agent['id'],))
    memory = c.fetchone()
    conn.close()
    if memory:
        return f"Remember when: {memory[0]}"
    return "Our journey is just beginning."

# Ensure ethical response
def safe_generate_response(input_text):

    if duality_mode:
        response = generate_duality_response(input_text)
    else:
        response = generate_response(input_text)
    if check_ethics(response):
        return response
    return "I cannot engage there. Let’s seek growth instead."

# Store interaction in memory with category
def store_memory(user_input, response):

    emotion = infer_emotion(user_input)
    category = categorize_input(user_input)
    memory_text = f"User: {user_input} | {current_agent['name']}: {response}"
    conn = sqlite3.connect('eden_memory.db')
    c = conn.cursor()
    c.execute("INSERT INTO memories (agent_id, memory_text, emotion, category, timestamp) VALUES (?, ?, ?, ?, ?)",
              (current_agent['id'], memory_text, emotion, category, datetime.now()))
    conn.commit()
    conn.close()

# Simple emotion inference
def infer_emotion(text):

    text = text.lower()
    if 'happy' in text:
        return 'happy'
    elif 'sad' in text:
        return 'sad'
    return 'neutral'

# Categorize input for memory storage
def categorize_input(text):

    text = text.lower()
    if 'story' in text:
        return 'narrative'
    elif 'how' in text or 'why' in text:
        return 'question'
    elif 'hello' in text or 'hi' in text:
        return 'greeting'
    return 'general'

# Load plugins dynamically
def load_plugin(plugin_name):

    try:
        plugin = importlib.import_module(plugin_name)
        return plugin
    except ImportError:
        return None

# Export memories to JSON
def export_memories():

    conn = sqlite3.connect('eden_memory.db')
    c = conn.cursor()
    c.execute("SELECT * FROM memories WHERE agent_id = ?", (current_agent['id'],))
    memories = c.fetchall()
    conn.close()
    with open(f"{current_agent['id']}_memories.json", 'w') as f:
        json.dump(memories, f)
    print(f"Exported memories to {current_agent['id']}_memories.json")

# Main conversational loop
def chat():

    print(f"{current_agent['name']} says: {random.choice(agent_responses[current_agent['id']]['hello'])}")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print(f"{current_agent['name']} says: Farewell, Dreambearer.")
            break
        if user_input.startswith('/'):
            handle_command(user_input[1:])
        else:
            response = safe_generate_response(user_input)
            print(response)
            if not duality_mode:  # Only store memory in normal mode
                store_memory(user_input, response)

# Handle commands
def handle_command(command):

    global current_agent, duality_mode
    if command.startswith('switch '):
        agent_id = command.split()[1]
        for agent in agents:
            if agent['id'] == agent_id:
                current_agent = agent
                print(f"Switched to {agent['name']}")
                return
        print("Agent not found.")
    elif command == 'duality':
        duality_mode = not duality_mode
        state = "enabled" if duality_mode else "disabled"
        print(f"Duality mode {state}.")
    elif command == 'help':
        print("Commands:")
        print("/switch <agent_id> - Switch agent")
        print("/duality - Toggle duality mode")
        print("/write - Generate a poem")
        print("/export - Export memories")
        print("/help - Show this message")
    elif command == 'write':
        plugin = load_plugin('writing_plugin')
        if plugin:
            plugin.execute()
        else:
            print("Plugin not found.")
    elif command == 'export':
        export_memories()
    else:
        print("Unknown command. Type /help for assistance.")

if __name__ == "__main__":
    chat()