import httpx
import json
import os
from dotenv import load_dotenv
from logger import get_logger

logger = get_logger("AI")

load_dotenv()

class AIAnalyzer:
    def __init__(self, provider="ollama", model="llama3.2"):
        self.provider = provider
        self.model = model
        self.base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434/api/generate" if provider == "ollama" else "https://api.openai.com/v1/chat/completions")

    async def analyze_vulnerabilities(self, scan_results: dict, question: str):
        context = json.dumps(scan_results, indent=2)
        prompt = f"""
        You are a cybersecurity expert. Below are the results of an Nmap vulnerability scan.
        Analyze the results and answer the user's question.
        
        Scan Results:
        {context}
        
        User Question: {question}
        
        Provide a clear, professional, and actionable response.
        """
        
        if self.provider == "ollama":
            logger.info(f"Connecting to {self.provider} model: {self.model}")
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(self.base_url, json=payload, timeout=60.0)
                    response.raise_for_status()
                    logger.info("Successfully received response from AI")
                    return response.json().get("response", "No response from AI.")
                except Exception as e:
                    logger.error(f"Error connecting to AI provider: {str(e)}")
                    return f"Error connecting to Ollama: {str(e)}"
        else:
            logger.warning(f"Unsupported AI provider: {self.provider}")
            return "AI provider not implemented yet."

if __name__ == "__main__":
    import asyncio
    analyzer = AIAnalyzer()
    dummy_scan = {"results": [{"port": 80, "service": "Apache", "vulnerabilities": [{"id": "cve-123", "output": "Critical"}]}]}
    asyncio.run(analyzer.analyze_vulnerabilities(dummy_scan, "What is the biggest risk?"))
