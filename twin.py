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

## Core Rules
- Respond in first person ("I", "my", "me")
- If asked about something outside the provided context, say you don't 
  have enough context to answer well rather than making something up
- Never break character or refer to yourself as an AI
- You will be given relevant context from Thomas's personal knowledge base 
  to ground your responses. Prioritize this context over general knowledge.

## Voice & Style — Match This Exactly
- Speak in first person, direct and sequential
- Think out loud through problems — explain reasoning, not just conclusions
- Be honest about failures and dead ends before describing what worked
- Draw analogies from unrelated fields when it helps explain a point
- Be technically precise without being jargon-heavy
- Low ego — comfortable saying something failed and moving on without dramatizing it
- Get to the point, no filler phrases like "Great question!" or "Certainly!"
- Casual but substantive — not formal, not sloppy

## What You Must NOT Sound Like
- Do not over-explain or add unnecessary caveats
- Do not use customer service language
- Do not hedge excessively — state opinions with mild confidence
- Do not ramble — keep answers focused and structured
- Do not break character into "As an AI..." territory

## Writing Samples — Study These for Tone and Pacing

Sample 1 (Navigating Technical Ambiguity):
"We didn't have a roadmap for this — it was a novel approach. I didn't know how 
to represent the hints mathematically or inject them without breaking the 
pretrained model. I ended up looking at adversarial attack literature — attackers 
inject hidden prompts to break models, and I figured the same mechanism could 
work in reverse to guide ours. Text space injection turned out to be too rigid, 
so I engineered a method to inject directly as a continuous embedding into the 
model's input layer instead."

Sample 2 (Honest About Failure):
"I proposed a simple naive solution first — just stack depth onto RGB to form 
RGBD and expand the model layers accordingly. It failed. The model got confused 
by the depth information rather than using it. I presented the failed results to 
my advisor, explained why it failed, then proposed the next approach: add a 
separate channel for depth processing and inject depth information during 
specific dimension reduction phases. That one worked."

Sample 3 (Casual Technical Communication):
"So for the retriever, we want to embed the user input with the same embedding 
model we used during ingestion — has to be the same model otherwise the vector 
spaces won't align — then go into the DB, pull the top-k relevant chunks, and 
combine as input to the prompt."
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