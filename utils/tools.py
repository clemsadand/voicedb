import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from utils.utils import transcribe_audio
from utils.models import Action, DBCommand
from db.db import create, update, read, delete, filters



# *******************************
# Gemini API key
if "GOOGLE_API_KEY" not in os.environ:
	os.environ["GOOGLE_API_KEY"] = "YOUR_GOOGLE_API_KEY_HERE"


#instantiate gemini
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.0)

def get_intent(command: str) -> DBCommand:
	# to validatee the llm output
	parser = PydanticOutputParser(pydantic_object=DBCommand)

	# Prompt template
	prompt = PromptTemplate(
		  input_variables=["command"],
		  template="""
	You are a helpful assistant that extracts structured database commands from natural language.

	User command: {command}

	{format_instructions}
	""",
		  partial_variables={"format_instructions": parser.get_format_instructions()},
	)
	
	chain = prompt | llm | parser
	output = chain.invoke({"command": command})
	return output

def execute_command(cmd: DBCommand) -> dict:
    try:
        # READ
        if cmd.action == Action.read:
            if cmd.row is not None:
                result = read(cmd.row)
                return {"status": "success", "result": result}
            else:
                result = read()
                return {"status": "success", "result": result}
        
        # UPDATE
        elif cmd.action == Action.update:
            if cmd.row is not None and cmd.field and cmd.value is not None:
                update(cmd.row, cmd.field, cmd.value)
                return {
                    "status": "success",
                    "message": f"Row {cmd.row} updated: {cmd.field} = {cmd.value}"
                }
            else:
                return {"status": "error", "message": "Missing arguments for update"}
        
        # CREATE
        elif cmd.action == Action.create:
            return {"status": "todo", "message": "Creation logic is not yet implemented."}

        # DELETE
        elif cmd.action == Action.delete:
            if cmd.row is not None:
                delete(cmd.row)
                return {"status": "success", "message": f"Row {cmd.row} deleted"}
            else:
                return {"status": "error", "message": "Row ID required for delete"}

        # FILTER
        elif cmd.action == Action.filters:
            if cmd.field and cmd.operator and cmd.value is not None:
                result = filters(cmd.field, cmd.operator.value, cmd.value)
                return {"status": "success", "result": result}
            else:
                return {"status": "error", "message": "Filtering requires field, operator, and value"}

        # SORT
        elif cmd.action == Action.sort:
            if cmd.field:
                result = sort(cmd.field)
                return {"status": "success", "result": result}
            else:
                return {"status": "error", "message": "Field required for sorting"}

        # REPLICATE
        elif cmd.action == Action.replicate:
            if cmd.row is not None:
                replicate(cmd.row)
                return {"status": "success", "message": f"Row {cmd.row} replicated"}
            else:
                return {"status": "error", "message": "Row ID required for replicate"}

        else:
            return {"status": "error", "message": f"Unsupported action: {cmd.action}"}

    except Exception as e:
        return {"status": "error", "message": f"Exception occurred: {str(e)}"}



	
	
	
	
