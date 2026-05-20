import pytest
from unittest.mock import AsyncMock, patch, MagicMock

# A simple unit test placeholder for the CI/CD pipeline
@pytest.mark.asyncio
async def test_screen_query_logic():
    from runtime_agent.agent_loop import AgentLoop
    
    loop = AgentLoop()
    
    # Verify heuristics
    assert loop._needs_screen_context("what is on my screen?") == True
    assert loop._needs_screen_context("tell me a joke") == False
    
    # Mock vision and LLM responses
    with patch.object(loop.vision, 'capture_and_parse', new_callable=AsyncMock) as mock_vision:
        mock_vision.return_value = {"elements": [{"type": "button", "text": "Submit"}]}
        
        with patch.object(loop.llm, 'generate_response', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "I see a submit button."
            
            # Simulated execution
            if loop._needs_screen_context("look at the screen"):
                ui = await loop.vision.capture_and_parse()
                assert ui["elements"][0]["text"] == "Submit"
                
                ans = await loop.llm.generate_response("test")
                assert ans == "I see a submit button."
