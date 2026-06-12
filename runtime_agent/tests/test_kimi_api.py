import pytest
from runtime_agent.services.llm_service import ConversationalLLMService

@pytest.mark.asyncio
async def test_kimi_api_endpoint():
    llm = ConversationalLLMService()
    
    # Send a highly constrained prompt to guarantee a quick and specific response
    prompt = "Respond with exactly the word 'SUCCESS' and nothing else."
    
    response = await llm.generate_response(prompt)
    
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0
    
    # If the API key is valid and the network is up, it shouldn't return the fallback error string
    assert "Sorry, I couldn't connect" not in response
    assert "SUCCESS" in response.upper()
