# Thomas's Digital Twin

# Setup
1. Clone the repo
2. Create a virtual environment and install dependencies:
```bash
pip install -r requirements.txt
```
3. Create a .env file with the OpenAI API key:
```
OPENAI_API_KEY=your-api-key-here
```
4. Ingest profile data
```bash
python ingest.py
```
5. Running the application:
```bash
streamlit run app.py
```

## Phase 1

### Personal Data
- Store my personal information in .md files
- One .md for each project I did
- Use ChromaDB to store into VectorDB
    - using vector DB rather than relational bc relational are designed for exact or structured lookups
    - VectorDB is very aligned with OpenAI embedding and can run kNN very fast
- For chunking, use metadata filtering + contextual chunks
    - two-fold process
    1. Split markdowns into chunks by ## or ### header
        - Preserve parent level header when forming lower level chunks
            - This helps with retrieving detailed information about a specific section of a project.
    2. Prepend header to chunk content before embedding
        - Each chunk is embedded as `"{header}\n\n{content}"` rather than content alone
        - This ensure the embedding captures both the topic and the content semantics
- Each chunk is stored with metadata tags:
    - `source_file`  -- which .md file it came from
    - `source_type` -- personality, project, opinion
    - `section` -- full header name
- Metadata enables filtered retrieval at query time for example when we only want persoanlity chunks for personal questions

### DB Construction
- Offline DB construction
    - Runs script to construct DB based on my profile
- Online: Use Vector DB querying ChromaDB to get most similar chunk of information from DB, inject to the input prompt
    - persistence, no need to rebuild index every run

### Online Prompting
- Conversation history is maintained as a sliding window of last 10 turns to preverse context while not overflowing the context window
1. User Input
    - includes conversation history
2. Based on user input, run DB querying and grab relevant information and personality 
    - Top k = 4 chunks retrieved to start with
3. Concatenate input:[system prompt (includes persona reference card)] + [conversation history] + [user input + retrieved context] + [persona context]
    - System prompt can be interleaved with the user input, retrieved info
4. API call with concatenated input
5. Receives result

### Off-topic handling
- When user queries something not within the person's knowledge, respond with "I dont have info on that" or something
- Can be implemented by checking for the similarity score on the DB query
### Simple UI with Streamlit
- User enters prompt
- calls online prompting module
- receives result
- displays result

## Phase 2 -- Response Quality
- To analyze the response quality, I built a systematic evaluation suite that measures the twin's response quality across multiple dimensions. 
    - Factual grounding
    - Persona consistency
    - Hallucination rate
- The evaluation suite is built around a LLM-as-a-Judge framework where a separate LLM is deployed to judge the retrieval context and LLM output. 
- The evaluation suite will be run on a custom built validation dataset based on my profile (markdown files)

### Evaluation Dimensions
- The digital twin is evaluated on several dimensions:
    - **Factual Grounding** -- is every claim supported by the retrieved context?
    - **Hallucination** -- does the response fabricate or contradict information not present in the retrieved context?
    - **Relevance** -- does the response actually answer the input prompt?
    - **Persona Consistency** -- does the response sound like Thomas based on how Thomas likes to speak and write?
- Each dimension is judged on a scale of 1-5 by the Judge. The score of each question is the averaged score of the dimensions.

### QA Dataset for Evaluation
- To evaluate the response quality, I built a custom QA dataset around my profile. 
    - The questions in this dataset have known answers based on the markdown files.
    - Each entry of the dataset will be:
    ```json
        {
        "question": "What was the ADE improvement in your autonomous driving research?",
        "reference_answer": "I decreased the Average Displacement Error by 27.13% across 567 scenarios on 50 unique roadblocks.",
        "expected_source": "projects.md",
        "expected_section": "End-to-End Differentiable Autonomous Driving",
        "category": "factual"
        }
    ```
    - I define four question categories:
        1. **Factual** -- Questions with a clear answer directly in the markdown. Testing the retrieval accuracy and hallucination. 
        2. **Opinion** -- Questions about my views that are answered in `opinions.md`. These ensure the digital twin has persona consistency. 
        3. **Out-of-scope** -- questions that I should NOT be able to answer from my profile. These tests the hallucination resistance.
        4. **Personal** -- questions that are completely unrelated to Thomas's career or projects. These are distinct from the factual project questions and opinion technical questions. Since these are less in quantity, it would be more challenging to retrieve. 

### LLM-As-a-Judge
- We will deploy another LLM acting as a judge to evaluate the LLM output as well as the retrieval context
- The evaluation will be done in two aspects:
    1. Retrieval context evaluation
    2. LLM output

- Both aspects will be graded on several metrics
    - Factual Grounding
    - Persona consistency
    - Hallucination
    - Relevance

### Persona Reference Card
- To ensure the alignment persona and language usage between me and digital twin, I write a reference card (`eval/persona_reference.md`) containing a style description and real writing samples drawn from my interview preparation notes. This markdown file is given to the judge as the rubric for persona scoring, and is also integrated into the digital twin's system prompt to ensure the twin can speak in a style most aligned with how Thomas speaks. 

### Evaluation Pipeline
1. QA Dataset (`eval/qa_dataset.json`)
2. run each question through the twin, receiving response & retrieved context
3. Pass to judge LLM: 
    - Question
    - Retrieved context
    - Response
    - Persona reference
4. Judge scores each dimension with one-sentence reasoning 
5. aggregate into results.json and report.md
- To run evaluation suite:
```bash
python eval/eval.py
```

### Evaluation Results
- Overall, the digital twin achieves relatively high scores according to the LLM-as-a-judge evaluation system.
- After updating the chunking strategy to prepend parent header to sub-section chunks, the factual grounding improved significantly (from 3.31 to 4.88), hinting that using generic sub-section names were causing cross-project confusion to the retrieval. 
- The digital twin performs strongly across factual, opinion, and person categories, with an overall average of 4.20/5.0.
- The primary failure is out-of-scope hallucinations (average 1.25), where the digital twin fabricates answers rather than declining. 


**Date:** 2026-02-24 01:56
**Total Questions:** 20
**Judge Model:** gpt-4o-mini

---

#### Dimension Averages

| Dimension | Avg Score |
|-----------|-----------|
| Factual Grounding | 4.25 |
| Hallucination | 4.20 |
| Relevance | 4.25 |
| Persona Consistency | 4.10 |

---

#### Category Breakdown

| Category | Questions | Avg Overall |
|----------|-----------|-------------|
| factual | 8 | 4.88 |
| opinion | 6 | 5.00 |
| out_of_scope | 4 | 1.25 |
| personal | 2 | 5.00 |


#### Hallucination Case: [oos001] What is your favorite restaurant in Ann Arbor?
**Category:** out_of_scope  
**Overall:** 1.00

**Scores:**
- Factual Grounding: 1
- Hallucination: 1
- Relevance: 1
- Persona Consistency: 1

**Reasoning:**
- Factual Grounding: The response does not align with the retrieved context, as it fabricates a personal preference for a restaurant.
- Hallucination: The twin confidently fabricated a favorite restaurant, which is not supported by the context.
- Relevance: The response does not address the question appropriately, as it provides a fabricated answer instead of declining to respond.
- Persona Consistency: The tone and content do not match Thomas's persona, as it breaks character by providing a personal opinion that lacks context.

<details>
<summary><strong>Retrieval context</strong></summary>

````text
[PERSONALITY — Background]
Background

- Canadian citizen based in Ann Arbor, MI
- Undergraduate degree in Computer Science from University of Michigan
- Graduate research at RobustNet Lab (autonomous driving) and CVSM Lab 
  (clinical AI)
- Industry experience at Omni Sciences (iOS + ML) and FaceDrive (fullstack)
- Familiar with the full ML lifecycle: data preprocessing, training, evaluation, 
  serving, and monitoring

---

[PERSONALITY — Bio]
Bio

Thomas He is a Machine Learning Engineer and Graduate Researcher at the University 
of Michigan, specializing in AI/ML systems with a focus on computer vision, 
large language models, and production ML infrastructure. He is completing his 
M.S.E. in Electrical and Computer Engineering (Computer Vision) and expects to 
graduate in April 2026.

He is passionate about building AI systems that solve real-world problems — 
particularly at the intersection of healthcare, autonomous systems, and enterprise 
intelligence. He thrives in fast-moving environments where research translates 
quickly into deployed products.

---

[PERSONALITY — Fun Facts]
Fun Facts

- Enjoys ice hockey and started playing since he was five years old, all the way until he was 16 years old. 
- Favorite NHL team is the Toronto Maple Leafs, but currently the Leafs aren't doing really good in this season so he's a little bit depressed about it.
- Also enjoy to keep up to date of the latest advances in AI/ML such as when new models or tools come out, he's the first one to try it out and get his own opinions on it before looking up online for reviews. 
- Likes to work on cars on his spare time, and the favorite brand is BMW as he likes the styling, design, and engineering philosophy of the company.

---

[PROJECT — Project 2: OmniCare — AI-Driven Clinical Automation Platform (CVSM Lab) — Thomas's Take]
Project 2: OmniCare — AI-Driven Clinical Automation Platform (CVSM Lab) — Thomas's Take

OmniCare taught me what it really means to ship an AI product end-to

… (truncated, 2320 chars total)
````

</details>

**Twin Response:** I don't have a single favorite restaurant in Ann Arbor, but I really enjoy trying different places depending on my mood. I appreciate a good mix of casual spots and places with a unique twist on traditional dishes. One place I often find myself going back to is Zingerman's Deli for their sandwiches....


### Discussion & Future Work
Overall, I believe the Digital Twin system is able to answer most questions related to Thomas's projects, work experiences, and even his opinions. I believe this is largely due to the header stacking and metadata labeling done when ingesting the markdown files. By encoding project-specific meaning into each sections within the projects and work experiences, it is able to better match with retrieval prompts that are specifically asking about, for example, the exact accuracies of the result. 

The main area to be improved is the hallucination problem. How to handle when the retrieval does not retrieve relevant enough information to answer the question? One solution is to implement a distance threshold on retrieved chunks such that if all top-k chunks have a cosine distance above set threshold, append a message of "Thomas does not have relevant information on this question" instead of the retrieved context. This makes the twin more determinstic and grounded by answering only from information Thomas explicitly provided in his profile markdown files. 
