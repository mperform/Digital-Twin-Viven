# Thomas He — Projects

## Project 1: End-to-End Differentiable Autonomous Driving (RobustNet Lab)
**Type:** Graduate Research  
**Tech:** Python, PyTorch, CUDA, Nvidia A40, WandB  
**Timeline:** April 2025 – Present

### Overview
Architected a fully differentiable optimization algorithm to improve the safety 
of End-to-End Autonomous Driving frameworks, with a focus on construction zone 
scenarios where existing models fail most frequently.

### What I Did
- Designed a large-scale training framework to facilitate optimization across 
  100,000 scenes spanning ~1500 unique roadblocks
- Implemented data parallelism at the roadblock level across 4 Nvidia A40 GPUs, 
  improving training efficiency by ~3x
- Extended the pipeline to support Low-rank Subspace Suffix Fine-tuning (LSSF) 
  for Vision-Language Models to improve trajectory prediction

### Results
- Decreased Average Displacement Error (ADE) by 27.13% across 567 scenarios 
  on 50 unique roadblocks
- Training throughput improved ~3x through roadblock-level data parallelism

### Challenges & Learnings
- Resolving memory bottlenecks and PCIe communication issues in distributed 
  training environments
- Making discrete language model outputs end-to-end differentiable required 
  significant architectural innovation
- Balancing training efficiency with model safety across diverse road scenarios

### Thomas's Take
This project taught me that safety in autonomous systems is fundamentally an 
optimization problem — you need to define what safety means mathematically before 
you can improve it. The distributed training work also gave me deep appreciation 
for how infrastructure decisions directly constrain research velocity.

---

## Project 2: OmniCare — AI-Driven Clinical Automation Platform (CVSM Lab)
**Type:** Graduate Research + Product  
**Tech:** Python, PyTorch, DeepSeek-R1, Whisper, Django, ARCore, RunPod, 
Samsung XR  
**Timeline:** January 2025 – Present

### Overview
Built an end-to-end clinical automation platform combining contactless vital 
sign monitoring, automated clinical documentation, and LLM-based triage 
decision support — deployed on Samsung XR headsets worn by medical professionals.

### What I Did
- Led backend architecture and full-stack integration across a multi-person team
- Served a distilled DeepSeek-R1 across 2 L40S GPUs on RunPod for real-time 
  clinical reasoning and next-step action recommendations
- Engineered REST API endpoints and WebSocket video streaming serving real-time 
  vitals inference to Samsung XR clients
- Integrated Whisper speech-to-text with speaker diarization to transcribe 
  nurse-patient dialogs into structured SOAP clinical notes
- Developed the Android XR frontend on Samsung XR headset using ARCore for 
  vitals display and clinical workflow navigation

### Results
- Successfully deployed end-to-end on RunPod with live Samsung XR frontend
- Platform handles real-time vitals inference, LLM clinical reasoning, and 
  automated documentation in a single unified workflow

### Challenges & Learnings
- Coordinating multiple ML model serving pipelines (rPPG, triage agent, 
  summarization, stress prediction) with strict real-time latency requirements
- Designing a safe clinical AI system that recommends next steps without 
  overstepping into diagnosis territory
- Managing team coordination across frontend and backend tracks simultaneously

### Thomas's Take
OmniCare taught me what it really means to ship an AI product end-to-end. 
Research-quality models are necessary but not sufficient — latency, reliability, 
and safety guardrails are equally important in a clinical context. Leading the 
backend while overseeing full-stack integration also pushed me to think more 
carefully about system design upfront rather than iterating blindly.

---

## Project 3: Omni-RAG — Medical Knowledge Graph-Assisted RAG Framework (CVSM Lab)
**Type:** Graduate Research  
**Tech:** Python, PyTorch, LLM prompting, Knowledge Graphs, RAG, MIMIC-IV-ED  
**Timeline:** January 2024 – Present

### Overview
Built a Domain-Agnostic Medical Knowledge Graph-assisted RAG framework for 
patient diagnosis workflows, achieving SOTA in-domain diagnosis accuracy through 
hybrid knowledge graph construction and semantic retrieval.

### What I Did
- Designed a hybrid knowledge graph construction pipeline leveraging LLM expert 
  prompting and empirical EHR data mining from MIMIC-IV-ED
- Built a semantic KG retrieval and aggregation module with symptom deduplication 
  to reduce model hallucinations
- Implemented a LLM post-training pipeline with TRL, LoRA, and quantization on 
  DeepSpeed ZeRO-3 for a 70B model
- Preprocessed clinical triage data (MIMIC-IV-ED) using pandas and JSONL 
  data cleansing pipelines

### Results
- Achieved SOTA In-Domain diagnosis exact-match accuracy of 79%
- 5x improvement over LLM-only configurations
- Symptom deduplication module measurably reduced hallucination rate on 
  out-of-distribution queries

### Challenges & Learnings
- Medical knowledge graphs are expensive to construct accurately — hybrid 
  LLM + empirical mining was key to balancing quality and scalability
- Hallucination in medical contexts is particularly dangerous, requiring 
  systematic deduplication and retrieval validation
- DeepSpeed ZeRO-3 required careful memory profiling to avoid OOM errors 
  on the 70B model

### Thomas's Take
Omni-RAG convinced me that naive RAG is rarely enough for high-stakes domains. 
The knowledge graph layer adds structured reasoning that flat vector retrieval 
misses — especially for multi-hop medical queries where symptoms relate to 
conditions in non-obvious ways. Evaluation design was also critical here; 
exact-match accuracy alone doesn't capture clinical relevance.

---

## Project 4: OMNI-CAN — Contactless Vital Sign Monitoring (Omni Sciences)
**Type:** Industry — Software Engineering Internship  
**Tech:** Python, PyTorch, SwiftUI, UIKit, Django, AWS, PostgreSQL, A100 GPU  
**Timeline:** May 2024 – August 2024

### Overview
Developed a contactless vital sign monitoring system combining a temporal-shift 
dual-branch attention CNN for pulsewave prediction with a production iOS mobile 
application and Django REST backend on AWS.

### What I Did
- Architected and served a temporal-shift dual-branch attention CNN for 
  pulsewave prediction using RGB and Depth camera inputs
- Developed the iOS mobile application using SwiftUI and UIKit for real-time 
  HR and RR signal display
- Integrated a Django REST backend on AWS with PostgreSQL, serving real-time 
  heart rate and respiration rate signal processing
- Trained the model on an A100 GPU with train-valid-test split on 500+ samples

### Results
- Achieved Pearson correlation of 0.989 and R² of 97.8% on held-out test set
- End-to-end system deployed on iOS devices serving real-time vital sign 
  monitoring

### Challenges & Learnings
- RGB + Depth fusion required careful temporal alignment between input streams
- Real-time signal processing on mobile introduced latency constraints that 
  shaped model architecture decisions
- Bridging ML research and iOS production deployment required learning SwiftUI 
  and UIKit alongside model optimization

### Thomas's Take
OMNI-CAN was my first experience taking an ML model from training all the way 
to a production mobile application. It fundamentally changed how I think about 
model design — inference speed and memory footprint matter just as much as 
accuracy when you're running on a phone. It also sparked my broader interest 
in contactless health monitoring as a research area.

---

## Project 5: MTSPipe — Multi-Teacher Knowledge Distillation Pipeline
**Type:** Graduate Research  
**Tech:** Python, PyTorch, TensorFlow, CUDA, WandB, Distributed Systems  
**Timeline:** 2024 – 2025

### Overview
Engineered a parallelized multi-GPU training pipeline extending MTSPipe for 
multi-teacher knowledge distillation, improving training throughput and 
reducing energy consumption through architectural optimizations.

### What I Did
- Engineered a multi-GPU training pipeline increasing training throughput 
  by 6% while reducing energy consumption by 7%
- Implemented a dynamic routing module pruning 20% of redundant forward 
  passes to optimize system latency and efficiency
- Developed an asynchronous micro-batch scheduler in PyTorch, eliminating 
  pipeline bubbles to maximize hardware utilization
- Optimized CUDA memory management to resolve bottlenecks in distributed 
  training across multiple GPU nodes

### Results
- 6% throughput improvement and 7% energy reduction over baseline pipeline
- 20% reduction in redundant forward passes through dynamic routing
- Pipeline bubble elimination through asynchronous micro-batch scheduling

### Challenges & Learnings
- Multi-teacher distillation introduces complex gradient flow that requires 
  careful loss weighting and scheduling
- Asynchronous scheduling across GPUs introduced subtle race conditions that 
  required systematic debugging
- Energy efficiency is an underappreciated metric in ML systems — small 
  architectural changes compound significantly at scale

### Thomas's Take
MTSPipe pushed me to think seriously about ML systems efficiency, not just 
model accuracy. The dynamic routing module was particularly interesting because 
it sits at the intersection of model architecture and systems optimization — 
a space I find increasingly compelling as models scale.