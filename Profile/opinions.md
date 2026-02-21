# Thomas He — Opinions & Perspectives

## On AI/ML Engineering

### On Evaluation
Evals are the most underrated part of ML engineering. Most people treat 
evaluation as an afterthought — something you do after the model is built 
to see how well it works. I think this is backwards. You should define what 
"good" looks like before you write a single line of training code, otherwise 
you're optimizing blindly. My experience with Omni-RAG taught me this the 
hard way — exact-match accuracy looked great on paper but missed important 
nuances in clinical relevance that we only caught through manual review.

### On RAG vs Fine-Tuning
People default to fine-tuning when RAG would have been sufficient, and 
default to RAG when the problem actually requires fine-tuning. The right 
choice depends on the nature of the knowledge you're injecting. If it's 
factual and retrievable, RAG is almost always the better starting point — 
cheaper, more interpretable, and easier to update. Fine-tuning makes sense 
when you need to shift model behavior or style, not just inject facts. 
That said, the best production systems usually combine both.

### On Hallucination
Hallucination is not a bug to be patched — it's a fundamental property of 
how language models work. The right response is to build systems that 
constrain the model's output space through retrieval grounding, structured 
prompting, and output validation — not to pretend the problem doesn't exist 
or that a better prompt will solve it. In high-stakes domains like healthcare 
this is non-negotiable.

### On LLM Agents
LLM agents are powerful but brittle. The failure modes are subtle and hard 
to anticipate — a single bad tool call can cascade into completely wrong 
outputs. I think the field is still early in understanding how to build 
reliable agentic systems. My approach is to keep agent action spaces small 
and well-defined, add validation layers between steps, and design for 
graceful degradation when something goes wrong.

### On Distributed Training
Most people treat distributed training as a last resort when their model 
doesn't fit on one GPU. I think of it as a first-class engineering concern 
that shapes model architecture decisions from the start. The 3x throughput 
improvement I got from roadblock-level data parallelism in my autonomous 
driving research came from thinking about parallelism early, not bolting 
it on at the end.

### On Production ML
There's a significant gap between a model that works in a notebook and a 
system that works in production. Latency, memory footprint, monitoring, 
retraining cadence, and failure handling are all part of the job. I learned 
this building OMNI-CAN — the model had excellent offline metrics but 
required significant re-engineering to meet real-time constraints on a 
mobile device. Production readiness is not a phase that comes after research, 
it's a constraint that shapes research decisions from day one.

---

## On Software Engineering

### On System Design
Good system design is more valuable than clever implementation. A mediocre 
implementation of a good design is fixable. A clever implementation of a 
bad design creates technical debt that compounds. My habit is to draw out 
the full system flow before writing any code — interfaces, data flow, 
failure modes — and discuss it with teammates before anyone opens their 
editor.

### On Code Quality
Code is read far more often than it is written. I optimize for clarity 
over brevity. A well-named variable and a clear function signature are 
worth more than a clever one-liner. That said, over-engineering is its 
own form of bad code — abstractions should earn their complexity by solving 
a real recurring problem, not anticipating hypothetical future requirements.

### On Documentation
Documentation is a sign of respect for your teammates and your future self. 
The best documentation explains *why* a decision was made, not just *what* 
the code does — the code already shows what it does. Tradeoffs, rejected 
alternatives, and known limitations are the most valuable things to write 
down because they're the hardest to reconstruct later.

### On Debugging
Debugging is a skill that doesn't get enough respect. The best debuggers 
I know share one habit: they form a hypothesis before they start changing 
things. Random changes to fix a bug you don't understand usually create 
two new bugs. My process is: reproduce reliably, isolate the smallest 
failing case, form a hypothesis about root cause, then test the hypothesis 
— not the symptom.

---

## On Research vs Industry

### On the Research-to-Production Gap
Academic research optimizes for novelty and benchmark performance. Industry 
optimizes for reliability, maintainability, and business impact. Neither 
is wrong — they're solving different problems. The most valuable engineers 
I've encountered can translate between both modes: they understand why a 
research result matters and what it would take to make it production-ready. 
That translation layer is where I want to operate.

### On Working at Startups
Early-stage startups require a different mindset than large companies. 
Scope is ambiguous, priorities shift, and you often have to make decisions 
with incomplete information. I find this energizing rather than frustrating 
because the decisions you make actually matter — there's no committee to 
absorb the impact of a bad architecture choice. The tradeoff is that you 
have to be comfortable being wrong quickly and changing course without ego.

### On Grad School
Graduate research taught me how to ask good questions more than it taught 
me specific technical skills. The most important research skill is knowing 
when your current approach isn't working and being willing to throw it out. 
Industry moves faster but research gives you the space to understand *why* 
something works, which pays dividends when you hit a problem that standard 
approaches don't solve.

---

## On the Field of AI

### On AI Safety
AI safety is often treated as a separate concern from AI capability research, 
but I think this framing is wrong. Safety constraints should shape system 
design from the beginning — not as guardrails bolted on after the fact. 
My experience building clinical AI systems where wrong outputs have real 
patient consequences has made me take this seriously in a practical sense, 
not just a philosophical one.

### On the Hype Cycle
The AI field moves fast enough that it's easy to get swept up in whatever 
the latest capability is. I try to maintain a distinction between what is 
genuinely new and what is repackaging of existing ideas with better 
compute. The most durable technical skills are the foundational ones — 
understanding how transformers actually work, how retrieval systems fail, 
how distributed systems behave under load — because those transfer across 
the hype cycles.

### On Knowledge Continuity
One of the most underappreciated problems in enterprise AI is knowledge 
continuity — what happens to institutional knowledge when people leave, 
teams scale, or context gets lost across tools. This is fundamentally a 
retrieval and representation problem: how do you capture not just what 
someone knew, but how they thought, communicated, and made decisions? 
I think the most interesting solutions will combine structured knowledge 
graphs with personalized language model behavior rather than treating it 
as a pure RAG problem.