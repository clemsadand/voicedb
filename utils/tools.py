import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from utils.utils import transcribe_audio
from utils.models import Action, DBCommand, Product, Status
from typing import Union
from db.db import create, update, read, delete, filters, sort, replicate, get_overall_stats, get_category_stats

# *******************************
# Gemini API key
if "GOOGLE_API_KEY" not in os.environ:
	os.environ["GOOGLE_API_KEY"] = "YOUR_GOOGLE_API_KEY"

#instantiate gemini
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.0)

def get_intent(command: str) -> Union[Status, DBCommand, dict]:
	
#	parser = PydanticOutputParser(pydantic_object=Status)
#	clarity_prompt = PromptTemplate.from_template(
#		"""
#		Determine whether this command is clear enough to extract these structured data: (action, row, field, value, operator).
#		Respond with "clear" or "unclear".
#		Command: "{command}"
#		
#		{format_instructions}
#		""",
#		partial_variables={"format_instructions": parser.get_format_instructions()}
#	)
#	
#	clarity_chain = clarity_prompt | llm | parser
#	clarity = clarity_chain.invoke({"command": command})
#	
#	if clarity != "clear":
#		return {"status": "needs_clarification", "message": "Please clarify your command."}
#		
	parser = PydanticOutputParser(pydantic_object=DBCommand)
	prompt = PromptTemplate(
        input_variables=["command"],
        template="""
        You are a helpful assistant that extracts structured database commands from natural language.

        Extract the correct JSON structure for the database operation below. Only output the JSON, and make sure to follow these rules:
		- The `row` field must be either a single integer (e.g. 4) or a list of integers (e.g. [1, 3, 5]).
		- Never use strings like colors, names, or labels as the `row` value.
		- If no row is specified, `row` should be None.
		- The `action` must be one of: create, read, update, delete, filter, sort, replicate, get_stats.
		- The `operator` must be one of: =, <, <=, >, >=, !=, LIKE, None.
		- The message should a simple sentence to say what you have done.
		
		- If `action` is create, then `row`, `field` and `operator` should be None, and then value should be a dictionary with these entries: name, category, color, quantity and price. 
		- Note that `stats` is the action that help to view the statistics.


        User command: {command}

        {format_instructions}
        """,
        partial_variables={"format_instructions": parser.get_format_instructions()},
	)
	
	parser_chain = prompt | llm | parser
	return parser_chain.invoke({"command": command})


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
        elif cmd.action == Action.stats:
        	overall = get_overall_stats()
        	by_category = get_category_stats()
        	return {"status": "success", "overview": overall, "by_category": by_category, "message": "Here is the stats."}
        else:
            return {"status": "error", "message": f"Unsupported action: {cmd.action}"}
            

    except Exception as e:
        return {"status": "error", "message": f"Exception occurred: {str(e)}"}



	
	
	
	
