from connectors.llm import DeepSeekClient


class Summarizer:
    def __init__(self):
        self.llm_client = DeepSeekClient()
        self.agent_description = (
            "A marketing agent focused on learning marketing concepts."
        )

    def summarize(self, text: str) -> str:

        task_description = f"""
TASK: Summarize the text below.
TEXT TO SUMMARIZE: {text}
        
Extract each individual sentence from the following summary as a standalone string, removing bullet points, numbering, and formatting. 
Output only a list of sentences, one per line, ready for embedding generation via a sentence-transformer."""
        summary = self.llm_client.summarize(
            self.agent_description, task_description
        )
        return summary
