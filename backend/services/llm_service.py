import json

class LLMService:
    """
    Manages communication with the local LLM (e.g., ollama with qwen2.5:0.5b).
    Generates explainability outputs for ranking.
    """

    @classmethod
    def generate_explainability(cls, candidate_data: dict, job_description: str) -> dict:
        """
        Generates the Explainability output as required by docs/knowledge.md.
        
        Outputs should include:
        - Matched skills
        - Missing skills
        - Semantic similarity breakdown
        
        Args:
            candidate_data (dict): The chunked resume and other candidate metrics.
            job_description (str): The raw job description.
            
        Returns:
            dict: The explainability breakdown.
        """
        # In a real implementation, this would build a prompt and call the LLM endpoint (e.g., via ollama).
        # We will stub the response structure to match the requirements.
        
        # prompt = f"..."
        # response = call_ollama(prompt, model="qwen2.5:0.5b")
        
        return {
            "matched_skills": [],  # List of skills found in both candidate and JD
            "missing_skills": [],  # List of skills present in JD but missing in candidate
            "coding_score_breakdown": {}, # Included from rule_score
            "github_score_breakdown": {}, # Included from rule_score
            "semantic_similarity_breakdown": "Explanation of the semantic fit...",
            "final_score_breakdown": "Explanation of the final weighted score..."
        }

# Singleton instance
llm_service = LLMService()
