from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from utils.utils import transcribe_audio
from utils.models import Action, DBCommand
from utils.tools import create, update, read, delete, filters
import os
import argparse

#setup a parser to get file
parser = argparse.ArgumentParser(description="A simple program that greets a user.")
parser.add_argument("filename", default="dev_audio/row4.flac", help="The command audio file to use")
args = parser.parse_args()
filename = args.filename

# *******************************
# Gemini API key
os.environ["GOOGLE_API_KEY"] = "GOOGLE_API_KEY"


#instantiate gemini
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.0)

def process_command(command_text: str) -> DBCommand:
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


if __name__ == "__main__":
	# transcribe the audio
	command = transcribe_audio(filename)
	cmd_to_db = process_command(command)
	
	print()
	print(cmd_to_db)
	
	print(execute_command(cmd_to_db))

