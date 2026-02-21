# Digital Twin Project

## Phase 1

### Personal Data
- Store my personal information in .md files
- One .md for each project I did
- Use ChromaDB to store into VectorDB
    - using vector DB rather than relational bc relational are designed for exact or structured lookups
    - VectorDB is very aligned with OpenAI embedding and can run kNN very fast
- For chunking, use metadata filtering + contextual chunks
    - two-fold process
    1. Attach metadata like this to every chunk:
    ```
    {
        "text": "achieved SOTA diagnosis accuracy of 79%...",
        "source": "projects.md",
        "project": "OmniRAG",
        "type": "result"
    }
    ```
    2. Make each chunk self-contained by including a header prefix
    ```
    Project: OmniRAG
    ```


### DB Construction
- Offline DB construction
    - Runs script to construct DB based on my profile
- Online: Use Vector DB querying ChromaDB to get most similar chunk of information from DB, inject to the input prompt
    - persistence, no need to rebuild index every run

### Online Prompting
1. User Input
    - includes conversation history
2. Based on user input, run DB querying and grab relevant information and personality 
    - Top k = 5 chunks retrieved to start with
3. Concatenate input: [system prompt] + [user input] + [retrieved information] + [personality information]
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

## Phase 2
