from google import genai
from google.genai import types
from llm_orchestrator.types.base_llm import BaseLLM
class LLMGemini(BaseLLM):
    def __init__(self):
        """
        Initialize an instance of LLMGemini.

        This constructor sets up a connection to the Google GENAI client using the provided API key
        and initializes an empty context dictionary for storing context information for future queries.
        """
        self.client = genai.Client(
            api_key="AIzaSyCrGGmZd0GAZpaYwgRNua8KcUuqFjn9ups",
        )
        self.context = {}
        
    def set_context(self, context: dict):
        """
        Set the context to use for future queries.

        Args:
            context: dict
                The context to use for future queries. This context will be
                passed to the model when generating content.

        Returns:
            None
        """
        self.context = context
    
    async def ask(self, prompt, config = None)->types.GenerateContentResponse:
        """
        Generate content based on the provided prompt and configuration.

        This function sends a request to the Google GENAI client to generate content
        using the specified model. The prompt and optional configuration are used
        to customize the content generation, including system instructions derived
        from the current context.

        Args:
            prompt: The input text to generate content from.
            config: Optional configuration dictionary to customize the content
                    generation process. If not provided, an empty configuration
                    is used.

        Returns:
            types.GenerateContentResponse: The response from the content generation
            request, which includes the generated content and associated metadata.
        """
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                **(config if config else {}),
                "system_instruction": str(self.context)
            }
        )
        return response
    
    def embeddings(self, texts: list[str]):
        
        """
        Generate embeddings for a list of text inputs.

        This function utilizes the Google GENAI client's embedding model to
        generate vector representations for the given list of text inputs.
        The model used is configured for semantic similarity tasks with a
        specified output dimensionality.

        Args:
            texts: list[str]
                A list of strings for which embeddings need to be generated.

        Returns:
            list[list[float]]: A list of embeddings, where each embedding
            is a list of floats representing the vector for the corresponding
            input text.
        """
        result = self.client.models.embed_content(
            model="gemini-embedding-001",
            contents=texts,
            config=types.EmbedContentConfig(
                task_type="SEMANTIC_SIMILARITY",
                output_dimensionality=1536
            )
        )
        
        embeddings = []
        
        for embedding in result.embeddings:
            embeddings.append(embedding.values)
        
        return embeddings