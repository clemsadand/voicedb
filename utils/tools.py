import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from utils.utils import transcribe_audio
from utils.models import Action, DBCommand, Product, Status
from typing import Union
from db.db import create, update, read, delete, filters, sort, replicate, get_overall_stats, get_category_stats
from dotenv import load_dotenv

# *******************************
# Gemini API key
if "GOOGLE_API_KEY" not in os.environ:
	os.environ["GOOGLE_API_KEY"] = "YOUR_GOOGLE_API_KEY"
elif:
	os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
else:
	os.environ["GOOGLE_API_KEY"] = input("Enter your Google API KEY (get it from https://aistudio.google.com/)\n: ")


#instantiate gemini
llm = ChatGoogleGenerativeAI(model="gemma-3n-e4b-it", temperature=0.0)

def get_intent(command: str) -> Union[Status, DBCommand, dict]:
    parser = PydanticOutputParser(pydantic_object=DBCommand)
    prompt = PromptTemplate(
        input_variables=["command"],
        template="""
        You are a helpful assistant that extracts structured database commands from natural language.
        
        The database consists of a products table with fields: id (int), name (text), category (Furniture, Electronics, Clothing, Books, Toys, Kitchen), color (red, blue, etc.), quantity (int), and price (float). All user queries should map to valid operations on this structure.

        Extract the correct JSON structure for the database operation below. Only output the JSON, and make sure to follow these rules:
        - The `row` field must be either a single integer (e.g. 4) or a list of integers (e.g. [1, 3, 5]).
        - Never use strings like colors, names, or labels as the `row` value.
        - If no row is specified, `row` should be None.
        - The `message` should a simple sentence to say what you have done, don't include any external link.
        - The `action` must be one of: create, read, update, delete, filter, sort, replicate, stats.
        - If `action` is stats, then `row`, `field`, `operator`, and `value` should all be None.
        - If `action` is create, then `row`, `field` and `operator` should be None, and then value should be a dictionary with these entries: name, category, color, quantity and price. 
        - The `operator` must be one of: =, <, <=, >, >=, !=, LIKE, None.
        - For filter action, `field` can be: id, name, category, color, quantity, price. While rendering a category, make it matches the existing categories.

        Examples:
        - "show all products" → action="read"
		- "create product iPhone 13, Electronics, Blue, 5, 999" → action="create"
		- "update product 1 name to iPhone 14" → action="update", row=1, field="name", value="iPhone 14"
		- "delete product 2" → action="delete", row=2
		- "find products with price > 100" → action="filter", field="price", operator=">", value=100
		- "show all product in furniture" → action="filter", field="category", operator="=", value="Furniture"
		- "show all furniture products" → action="filter", field="category", operator="=", value="Furniture"
		- "sort by price descending" → action="sort", field="price", value="desc"
		- "copy product 3" → action="replicate", row=3
        - "show database statistics" → action="stats"
        - "give me an overview" → action="stats"  
        - "what are the stats?" → action="stats"
        - "database summary" → action="stats"

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
            if cmd.value and isinstance(cmd.value, dict):
                required_fields = ['name', 'category', 'color', 'quantity', 'price']
                if all(field in cmd.value for field in required_fields):
                    product_id = create(
                        cmd.value['name'],
                        cmd.value['category'], 
                        cmd.value['color'],
                        cmd.value['quantity'],
                        cmd.value['price']
                    )
                    return {
                        "status": "success", 
                        "message": f"Product created with ID {product_id}",
                        "result": product_id
                    }
                else:
                    return {"status": "error", "message": f"Missing required fields: {required_fields}"}
            else:
                return {"status": "error", "message": "Create requires value as dictionary with product details"}

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
                # Handle operator - check if it's an enum or string
                operator_str = cmd.operator.value if hasattr(cmd.operator, 'value') else cmd.operator
                result = filters(cmd.field, operator_str, cmd.value)
                return {"status": "success", "result": result}
            else:
                return {"status": "error", "message": "Filtering requires field, operator, and value"}

        # SORT
        elif cmd.action == Action.sort:
            if cmd.field:
                # Check if descending sort is requested
                descending = False
                if cmd.value and str(cmd.value).lower() in ['desc', 'descending', 'reverse']:
                    descending = True
                result = sort(cmd.field, descending)
                return {"status": "success", "result": result}
            else:
                return {"status": "error", "message": "Field required for sorting"}

        # REPLICATE
        elif cmd.action == Action.replicate:
            if cmd.row is not None:
                new_id = replicate(cmd.row)
                return {"status": "success", "message": f"Row {cmd.row} replicated with new ID {new_id}"}
            else:
                return {"status": "error", "message": "Row ID required for replicate"}
        
        # STATISTICS
        elif cmd.action == Action.stats:
            overall = get_overall_stats()
            by_category = get_category_stats()
            return {
                "status": "success", 
                "overview": overall, 
                "by_category": by_category, 
                "message": "Database statistics retrieved successfully"
            }
        
        else:
            return {"status": "error", "message": f"Unsupported action: {cmd.action}"}
            
    except Exception as e:
        return {"status": "error", "message": f"Exception occurred: {str(e)}"}
	
	
