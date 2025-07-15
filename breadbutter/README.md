Problem Statement 01: Talent Matchmaking Engine

I created this talent recommendation system that combines rule-based matching with semantic similarity to connect clients with the most suitable creative professionals.

System Architecture
Hybrid Matching Approach
The system uses two different methods to find the best match:

Rule-Based Matching: Evaluates talent based on concrete criteria

Semantic Matching: Uses embeddings to find conceptual similarity between queries and talent profiles

Final Recommendation Logic:

Rule-based matching generates top 3 candidates
Semantic matching generates top 3 candidates
Final output: Top 2 from rule-based + Top 1 from semantic matching
LLM filtering selects the best semantic match with detailed justification

Technical Stack

Backend Framework:

Flask: Web application framework
PostgreSQL: Database with vector embeddings support
psycopg2: PostgreSQL adapter with RealDictCursor

Machine Learning & NLP:

LangChain: LLM integration and prompt management
Groq: LLM provider (llama3-70b-8192 model)
SentenceTransformers: Semantic similarity (all-mpnet-base-v2)
scikit-learn: Cosine similarity calculations

Geolocation Services:

geopy: Location services and distance calculations
Nominatim: OpenStreetMap geocoding service

Scoring Algorithm:

Rule-Based Scoring (Max: 60 points):

Location Score (Max: 25 points):

    Exact match: +25 points
    Can travel within range: +20 points
    Cannot travel: -10 points

Budget Score (Max: 25 points):

    Within budget range: +25 points
    Partial budget fit: +20 points
    Above budget: -10 points

Portfolio Score (Max: 10 points):

    Has portfolio: +10 points
    No portfolio: +5 points

Semantic Scoring:

Uses cosine similarity between query and talent embeddings
Considers style preferences, specializations, and experience
Normalized to comparable scale with rule-based scoring

LLM Scoring (Max: 42 points):

    Style & Specialization: Up to 10 points
    Budget Alignment: Up to 10 points
    Experience: Up to 12 points
    Portfolio Presence: Up to 10 points

Key Components:

1. recommendation.py

    Parses natural language using LLM
    Extracts structured gig information
    Stores in PostgreSQL database
    Vector similarity using sentence transformers
    Handles conceptual matching beyond keywords
    Considers talent summaries and specializations
    Gives the final recommendation

2. calculate_rule_based_scores.py:

    Location-based scoring with travel calculations
    Budget alignment with flexible ranges
    Portfolio presence evaluation


4. get_distance.py:

    Geolocation services integration
    Accurate distance measurement
    Handles geocoding errors gracefully

5. prompts.py:

    Structured prompt engineering
    Consistent output formatting
    Detailed justification generation