# AI/ML Engine

This folder contains machine learning training pipelines, NLP embeddings, and RAG components for the **AI Digital Career Twin**.

### Components (To be implemented in subsequent phases)
- `train_placement_classifier.py`: Trains Random Forest / Gradient Boosting classifier on the 100,000-student base-paper dataset to output placement probabilities and feature attributions.
- `train_salary_regressor.py`: Predicts expected compensation package (LPA) for placed candidates.
- `skill_gap_matcher.py`: Sentence Transformers (`all-MiniLM-L6-v2`) and TF-IDF semantic matcher between student profiles/resumes and company job descriptions.
- `rag_advisor.py`: Retrieval-Augmented Generation module for personalized career suggestions and step-by-step career advice.
