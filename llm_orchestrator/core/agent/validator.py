from pydantic import ValidationError
from llm_orchestrator.schemas.agent import AgentSchema
from llm_orchestrator.exceptions.agent_validator_exception import AgentValidatorException


class AgentValidator:
    @classmethod
    def run(cls, data: dict) -> AgentSchema:
        """
        Validate and parse the given data according to the AgentSchema.

        Args:
            data (dict): The data to be validated and parsed.

        Returns:
            AgentSchema: The parsed data.

        Raises:
            AgentValidatorException: If the data is invalid according to the schema.
        """
        try:
            # Ini otomatis validasi dan parsing sesuai schema
            return AgentSchema(**data)
        except ValidationError as e:
            # Bisa log atau raise ulang sebagai exception custom
            raise AgentValidatorException(f"Invalid Agent Schema: {e}")