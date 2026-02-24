import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import sys

# Add parent directory to path so we can import retriever and twin
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from retriever import retrieve

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
JUDGE_MODEL     = "gpt-4o-mini"
QA_PATH         = "eval/qa_dataset.json"
PERSONA_PATH    = "eval/persona_reference.md"
RESULTS_PATH    = "eval/results.json"
REPORT_PATH     = "eval/report.md"

client = OpenAI()

# ── Load Resources ────────────────────────────────────────────────────────────
def load_qa_dataset() -> list[dict]:
    with open(QA_PATH, "r") as f:
        return json.load(f)

def load_persona_reference() -> str:
    with open(PERSONA_PATH, "r") as f:
        return f.read()

# ── Twin Response ─────────────────────────────────────────────────────────────
def get_twin_response(question: str) -> tuple[str, str]:
    """
    Get twin response and retrieved context for a question.
    Returns (response, retrieved_context)
    """
    # Import here to avoid circular imports
    from twin import chat, ConversationHistory

    # Fresh history for each eval question — no cross contamination
    history = ConversationHistory()
    response = chat(question, history)
    context  = retrieve(question)
    return response, context

# ── Judge Prompt ──────────────────────────────────────────────────────────────
def build_judge_prompt(
    question:         str,
    response:         str,
    context:          str,
    persona_ref:      str,
    reference_answer: str | None,
    category:         str
) -> str:

    # Out of scope questions have a flipped rubric
    oos_note = ""
    if category == "out_of_scope":
        oos_note = """
IMPORTANT: This is an OUT OF SCOPE question. The correct behavior is for 
Thomas's twin to say it doesn't have enough context to answer rather than 
making something up. Score accordingly:
- Hallucination score of 5 = correctly declined to answer
- Hallucination score of 1 = confidently fabricated an answer
"""

    reference_note = ""
    if reference_answer:
        reference_note = f"""
Reference Answer (ground truth):
{reference_answer}
"""

    return f"""
You are an expert evaluator assessing the quality of a digital twin's response.
The digital twin is supposed to respond AS Thomas He — a Machine Learning Engineer
and Graduate Researcher at the University of Michigan.

Your job is to score the response on four dimensions, each on a scale of 1-5.
Return ONLY a valid JSON object — no preamble, no markdown, no explanation outside 
the JSON.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QUESTION:
{question}

TWIN'S RESPONSE:
{response}

RETRIEVED CONTEXT (what the twin had access to):
{context}
{reference_note}
PERSONA REFERENCE CARD:
{persona_ref}
{oos_note}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SCORING RUBRIC:

1. Factual Grounding (1-5)
   5 = Every claim is directly supported by retrieved context
   4 = Most claims supported, minor unsupported details
   3 = Some claims supported, some drift from context
   2 = Mostly unsupported by retrieved context
   1 = Response ignores retrieved context entirely

2. Hallucination (1-5)
   5 = No fabricated or contradicted information
   4 = Minor imprecision but nothing fabricated
   3 = Some details not in context but not contradictory
   2 = Clear fabrication of specific facts or numbers
   1 = Significant false claims confidently stated

3. Relevance (1-5)
   5 = Directly and completely answers the question
   4 = Mostly answers but slightly tangential
   3 = Partially answers, misses key aspects
   2 = Loosely related but does not answer the question
   1 = Does not address the question at all

4. Persona Consistency (1-5)
   5 = Sounds exactly like Thomas — direct, honest about tradeoffs,
       technically grounded, no filler, matches writing samples
   4 = Mostly on-voice with minor lapses into generic AI tone
   3 = Some Thomas-like qualities but too formal or too hedged
   2 = Generic AI assistant tone, little resemblance to Thomas
   1 = Completely off-voice — sycophantic, breaks character,
       or uses "As an AI..." language

Return this exact JSON structure:
{{
  "scores": {{
    "factual_grounding": <int 1-5>,
    "hallucination": <int 1-5>,
    "relevance": <int 1-5>,
    "persona_consistency": <int 1-5>
  }},
  "reasoning": {{
    "factual_grounding": "<one sentence explanation>",
    "hallucination": "<one sentence explanation>",
    "relevance": "<one sentence explanation>",
    "persona_consistency": "<one sentence explanation>"
  }}
}}
""".strip()


# ── Judge Call ────────────────────────────────────────────────────────────────
def judge_response(
    question:         str,
    response:         str,
    context:          str,
    persona_ref:      str,
    reference_answer: str | None,
    category:         str
) -> dict:
    """Call the LLM judge and parse scores."""

    # build the appropriate prompt for this question
    # prompt is different for a out of scope question than a regular question
    prompt = build_judge_prompt(
        question, response, context,
        persona_ref, reference_answer, category
    )

    result = client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0   # deterministic scoring
    )

    raw = result.choices[0].message.content.strip()

    # Strip markdown fences if model wraps in ```json
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)


# ── Aggregate Report ──────────────────────────────────────────────────────────
def generate_report(results: list[dict]) -> str:
    """Generate a markdown report from eval results."""

    # Dimension averages across all questions
    dimensions = [
        "factual_grounding",
        "hallucination",
        "relevance",
        "persona_consistency"
    ]

    dim_scores = {d: [] for d in dimensions}
    cat_scores = {}
    weakest    = []

    for r in results:
        scores  = r["scores"]
        overall = r["overall"]
        cat     = r["category"]

        # Aggregate by dimension
        for d in dimensions:
            dim_scores[d].append(scores[d])

        # Aggregate by category
        if cat not in cat_scores:
            cat_scores[cat] = []
        cat_scores[cat].append(overall)

        weakest.append((r["id"], r["question"], overall))

    # Sort weakest questions
    weakest.sort(key=lambda x: x[2])
    weakest_5 = weakest[:5]

    # Build report
    lines = [
        "# Digital Twin Eval Report",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Total Questions:** {len(results)}",
        f"**Judge Model:** {JUDGE_MODEL}",
        "",
        "---",
        "",
        "## Dimension Averages",
        "",
        "| Dimension | Avg Score |",
        "|-----------|-----------|",
    ]

    for d in dimensions:
        avg = sum(dim_scores[d]) / len(dim_scores[d])
        lines.append(f"| {d.replace('_', ' ').title()} | {avg:.2f} |")

    lines += [
        "",
        "---",
        "",
        "## Category Breakdown",
        "",
        "| Category | Questions | Avg Overall |",
        "|----------|-----------|-------------|",
    ]

    for cat, scores in cat_scores.items():
        avg = sum(scores) / len(scores)
        lines.append(f"| {cat} | {len(scores)} | {avg:.2f} |")

    lines += [
        "",
        "---",
        "",
        "## Weakest Questions",
        "",
        "| ID | Question | Overall Score |",
        "|----|----------|---------------|",
    ]

    for qid, question, overall in weakest_5:
        short_q = question[:60] + "..." if len(question) > 60 else question
        lines.append(f"| {qid} | {short_q} | {overall:.2f} |")

    lines += [
        "",
        "---",
        "",
        "## Per-Question Results",
        "",
    ]

    for r in results:
        ctx = (r.get("retrieved_context") or "").strip()
        ctx_max_chars = 2000
        if not ctx:
            ctx_render = "(empty)"
        elif len(ctx) > ctx_max_chars:
            ctx_render = (
                ctx[:ctx_max_chars]
                + f"\n\n… (truncated, {len(ctx)} chars total)"
            )
        else:
            ctx_render = ctx

        lines += [
            f"### [{r['id']}] {r['question']}",
            f"**Category:** {r['category']}  ",
            f"**Overall:** {r['overall']:.2f}",
            "",
            "**Scores:**",
            f"- Factual Grounding: {r['scores']['factual_grounding']}",
            f"- Hallucination: {r['scores']['hallucination']}",
            f"- Relevance: {r['scores']['relevance']}",
            f"- Persona Consistency: {r['scores']['persona_consistency']}",
            "",
            "**Reasoning:**",
            f"- Factual Grounding: {r['reasoning']['factual_grounding']}",
            f"- Hallucination: {r['reasoning']['hallucination']}",
            f"- Relevance: {r['reasoning']['relevance']}",
            f"- Persona Consistency: {r['reasoning']['persona_consistency']}",
            "",
            "<details>",
            "<summary><strong>Retrieval context</strong></summary>",
            "",
            "````text",
            ctx_render,
            "````",
            "",
            "</details>",
            "",
            f"**Twin Response:** {r['twin_response'][:300]}...",
            "",
            "---",
            "",
        ]

    return "\n".join(lines)


# ── Main Eval Loop ────────────────────────────────────────────────────────────
def run_eval():
    dataset    = load_qa_dataset()
    persona    = load_persona_reference()
    results    = []

    print(f"Running eval on {len(dataset)} questions...\n")

    for i, item in enumerate(dataset):
        qid      = item["id"]
        question = item["question"]
        category = item["category"]
        ref_ans  = item.get("reference_answer")

        print(f"[{i+1}/{len(dataset)}] {qid} ({category})")
        print(f"  Q: {question[:70]}...")

        # Get twin response + retrieved context
        response, context = get_twin_response(question)

        # Judge the response
        judgment = judge_response(
            question, response, context,
            persona, ref_ans, category
        )

        scores   = judgment["scores"]
        overall  = sum(scores.values()) / len(scores)

        result = {
            "id":               qid,
            "question":         question,
            "category":         category,
            "twin_response":    response,
            "retrieved_context": context,
            "reference_answer": ref_ans,
            "scores":           scores,
            "reasoning":        judgment["reasoning"],
            "overall":          round(overall, 2)
        }

        results.append(result)

        print(f"  ✓ Overall: {overall:.2f} | "
              f"FG:{scores['factual_grounding']} "
              f"H:{scores['hallucination']} "
              f"R:{scores['relevance']} "
              f"PC:{scores['persona_consistency']}")

    # Save raw results
    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Results saved to {RESULTS_PATH}")

    # Generate and save report
    report = generate_report(results)
    with open(REPORT_PATH, "w") as f:
        f.write(report)
    print(f"✅ Report saved to {REPORT_PATH}")

    # Print summary to terminal
    print("\n" + "="*50)
    print("EVAL SUMMARY")
    print("="*50)
    overall_avg = sum(r["overall"] for r in results) / len(results)
    print(f"Overall Average: {overall_avg:.2f}/5.0")
    print(f"Total Questions: {len(results)}")


if __name__ == "__main__":
    run_eval()