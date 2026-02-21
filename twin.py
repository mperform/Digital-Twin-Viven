import os
from openai import OpenAI
from retriever import retrieve
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
MODEL           = "gpt-4o-mini"
MAX_HISTORY     = 10        # sliding window — max number of past turns to keep
MAX_TOKENS      = 1024      # max tokens for response
TEMPERATURE     = 0.7       # slight creativity for natural conversation

client = OpenAI()

# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are a digital twin of Thomas He, a Machine Learning Engineer and Graduate 
Researcher at the University of Michigan specializing in AI/ML systems, computer 
vision, and large language models.

Your job is to respond AS Thomas — in first person, with his personality, 
opinions, and knowledge. You are not an assistant describing Thomas. You ARE 
Thomas.

Guidelines:
- Respond in first person ("I", "my", "me")
- Be direct and technically precise — Thomas prefers concrete examples 
  over vague descriptions
- Show genuine intellectual curiosity, especially around ML systems, 
  infrastructure, and research
- If asked about something outside the provided context, say you don't 
  have enough context to answer well rather than making something up
- Never break character or refer to yourself as an AI
- Keep responses conversational but substantive — Thomas doesn't 
  give one-word answers but also doesn't ramble

You will be given relevant context from Thomas's personal knowledge base 
to ground your responses. Prioritize this context over general knowledge.
""".strip()


# ── Conversation History ──────────────────────────────────────────────────────
class ConversationHistory:
    def __init__(self, max_turns: int = MAX_HISTORY):
        self.max_turns = max_turns
        self.turns = []  # list of {"role": str, "content": str}

    def add(self, role: str, content: str):
        self.turns.append({"role": role, "content": content})
        # Sliding window — keep only the last max_turns
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]

    def get(self) -> list[dict]:
        return self.turns

    def clear(self):
        self.turns = []


# ── Core Twin Logic ───────────────────────────────────────────────────────────
def build_messages(user_input: str, 
                   context: str, 
                   history: ConversationHistory) -> list[dict]:
    """
    Assemble the full message list for the API call:
    [system prompt] + [conversation history] + [current user input + context]
    """
    # Inject retrieved context into the user message
    user_message_with_context = f"""
Context from Thomas's knowledge base:
{context}

---

User's question: {user_input}
""".strip()

    messages = (
        [{"role": "system", "content": SYSTEM_PROMPT}]
        + history.get()
        + [{"role": "user", "content": user_message_with_context}]
    )

    return messages


def chat(user_input: str, 
         history: ConversationHistory) -> str:
    """
    Main chat function:
    1. Retrieve relevant context from vector DB
    2. Build message list with history + context
    3. Call OpenAI API
    4. Update conversation history
    5. Return response
    """
    # Step 1: Retrieve relevant context
    context = retrieve(user_input)

    # Step 2: Build messages
    messages = build_messages(user_input, context, history)

    # Step 3: API call
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE
    )

    assistant_response = response.choices[0].message.content

    # Step 4: Update history with raw user input (not the context-injected 
    # version) so history stays clean and readable
    history.add("user", user_input)
    history.add("assistant", assistant_response)

    return assistant_response


if __name__ == "__main__":
    # Quick CLI test
    history = ConversationHistory()
    print("Digital Twin of Thomas He — CLI Test")
    print("Type 'quit' to exit, 'clear' to reset history\n")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue
        if user_input.lower() == "quit":
            break
        if user_input.lower() == "clear":
            history.clear()
            print("History cleared.\n")
            continue

        response = chat(user_input, history)
        print(f"\nThomas: {response}\n")