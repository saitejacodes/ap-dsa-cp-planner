# AI CP/DSA Planner 

A high-performance, agent-driven platform designed to close the gap between generalized training sheets and personalized competitive programming growth.

## The Problem I was faced and try some solution 

Many high-quality mentors and DSA sheets exist in the market today, but most are generalized for the average student. I built this project to solve a specific problem: the lack of personalization. Every programmer has unique weaknesses (e.g., Dynamic Programming or Segment Trees) that generic schedules don't address effectively. 

This platform uses live data from Codeforces and LeetCode combined with a custom-engineered Dependency Graph (DAG) to generate a unique 30-day training path tailored specifically to your submission history and current rating.

## Key Features

- **Multi-Platform Integration**: Fetches real-time statistics and solved problems from Codeforces and LeetCode.
- **Agent-Powered Planning**: Uses Llama-3.3 (Groq) models to orchestrate a 30-day curriculum based on your detected weaknesses.
- **Semantic Recommendation Engine**: Powered by ChromaDB (built locally for efficiency) to recommend the most relevant practice problems for your specific level.
- **Interactive Mastery System**: A dedicated foundations page where you must pass AI-generated quizzes before proceeding to advanced practice.
- **Dependency Graph (DAG)**: An intelligent mapping of 22 DSA topics ensuring you always master prerequisites like sorting or arrays before tackling complex topics.

## Technical Architecture

The core of the system is built on three pillars:
1. **Dynamic Intelligence**: A custom TOPIC_GRAPH implementation that ensures a logical learning flow through topological sorting.
2. **Local Vector Search**: ChromaDB provides a fast, local retrieval system (RAG) that searches thousands of problems without needing expensive cloud overhead.
3. **State Management**: A hybrid MongoDB-Streamlit architecture that tracks your progress and remembers your study history across sessions.

## Challenges & Optimizations

Building this system required overcoming two significant engineering hurdles:
- **Problem Curation**: Designing a RAG system that could reliably feed high-quality, filtered problems to the LLM agent while ensuring variety and correctness.
- **Dependency Graph Logic**: Implementing a complex DAG for 22 topics was a significant optimization task, ensuring the pathing was both flexible and robust.

## Setup & Use

### Prerequisites
- Python 3.9+
- MongoDB (Local or Atlas)
- Groq API Key

### Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure your `.env` file (see `.env.example`)
4. Run the data ingestion script: `python scripts/load_rag.py`
5. Launch the application: `streamlit run main.py`

## Project Structure

- **agents/**: LLM orchestration and planning logic.
- **docs/**: Detailed system design and architecture notes.
- **models/**: Database connections and data schemas.
- **pages/**: Streamlit multi-page interface.
- **rag/**: Vector store initialization and query logic.
- **services/**: API fetchers for Codeforces and LeetCode.
