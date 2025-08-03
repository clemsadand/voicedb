from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import tempfile
import json
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
import whisper

model = whisper.load_model("base")

# Import your existing modules
from utils.tools import get_intent, execute_command
from utils.utils import transcribe_audio, convert_to_audio
from db.db import read, create, update, delete, filters, sort, replicate, close_connections

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for frontend

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = 'temp_audio'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed audio file extensions
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac', 'ogg', 'webm', 'm4a'}

# Cleanup database connections on app teardown
@app.teardown_appcontext
def cleanup_db(error):
    """Clean up database connections"""
    try:
        close_connections()
    except:
        pass

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup_old_files():
    """Remove temporary audio files older than 1 hour"""
    try:
        current_time = datetime.now().timestamp()
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(filepath):
                file_time = os.path.getctime(filepath)
                if current_time - file_time > 3600:  # 1 hour
                    os.remove(filepath)
    except Exception as e:
        print(f"Cleanup error: {e}")

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "healthy", "message": "Flask backend is running"})
    

@app.route("/api/transcribe", methods=["POST"])
def transcribe():
    print("=== TRANSCRIBE ENDPOINT CALLED ===")
    cleanup_old_files()  # clean older files
    
    if "audio" not in request.files:
        return jsonify({"success": False, "error": "No audio file provided"}), 400
    
    files = request.files["audio"]
    lang = request.form.get("lang", "en")
    
    print(f"Received file: {files.filename}, Language: {lang}")
    
    # validate file
    if files.filename == "":
        return jsonify({"success": False, "error": "No file selected"}), 400
        
    print("\nFile is valide ...\n")
    
    if files and allowed_file(files.filename):
        file_extension = files.filename.rsplit(".", 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
        
        files.save(filepath)
        print(f"File saved at {filepath}")
        
        #transcription = transcribe_audio(filepath)
        result = model.transcribe(filepath, language="en", task="transcribe")
        transcription = result["text"]
        
        print("\n", result["text"])
		
        print(f"Transcription result: '{transcription}'")
        
        # Clean up file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            "success": True, 
            "transcription": transcription, 
            #"language": lang
        })
    else:
        return jsonify({
            "success": False,
            "error": f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 400
        

@app.route("/api/chat", methods=["POST"])
def chat():
	"""Process text-based commands"""
	try:
		data = request.get_json()
		if not data or "message" not in data:
			return jsonify({"success": False, "error": "No message"}), 400
			user_message = data["message"]
			
		db_command = get_intent(user_message)
		result = execute_command(db_command)
		response_data = format_response(result, user_message)
		
		return jsonify(response_data)
	except Exception as e:
		print(f"❌ Error in process_text_command: {str(e)}")
		return jsonify({
            "status": "error", 
            "message": f"Chat processing failed: {str(e)}"
        })

##****************************************************************************************
@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get specific product by ID"""
    try:
        product = read(product_id)  # Your existing function
        if product:
            return jsonify({
                "status": "success",
                "data": format_product(product)
            })
        else:
            return jsonify({"status": "error", "message": "Product not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/products', methods=['POST'])
def create_product():
    """Create new product"""
    try:
        data = request.get_json()
        required_fields = ['name', 'category', 'color', 'quantity', 'price']
        
        if not all(field in data for field in required_fields):
            return jsonify({
                "status": "error", 
                "message": f"Missing required fields: {required_fields}"
            }), 400
        
        create(data['name'], data['category'], data['color'], 
               data['quantity'], data['price'])
        
        return jsonify({
            "status": "success",
            "message": "Product created successfully"
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update existing product"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
        
        # Update each field provided
        for field, value in data.items():
            if field in ['name', 'category', 'color', 'quantity', 'price']:
                update(product_id, field, value)
        
        return jsonify({
            "status": "success",
            "message": f"Product {product_id} updated successfully"
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete product"""
    try:
        delete(product_id)  # Your existing function
        return jsonify({
            "status": "success",
            "message": f"Product {product_id} deleted successfully"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def format_product(product_row):
    """Convert database row to dictionary"""
    if not product_row:
        return None
    
    # Handle both sqlite3.Row objects and tuples for backward compatibility
    if hasattr(product_row, 'keys'):
        # sqlite3.Row object (new format)
        return {
            "id": product_row['id'],
            "name": product_row['name'],
            "category": product_row['category'],
            "color": product_row['color'],
            "quantity": product_row['quantity'],
            "price": product_row['price']
        }
    else:
        # Tuple format (old format)
        return {
            "id": product_row[0],
            "name": product_row[1],
            "category": product_row[2],
            "color": product_row[3],
            "quantity": product_row[4],
            "price": product_row[5]
        }

def format_response(result, original_command):
    """Format database result for frontend consumption"""
    try:
        if result['status'] == 'success':
            if 'result' in result and result['result'] is not None:
                # Handle read operations
                if isinstance(result['result'], list):
                    data = []
                    for item in result['result']:
                        formatted = format_product(item)
                        if formatted:
                            data.append(formatted)
                    
                    return {
                        "status": "success",
                        "response": f"Found {len(data)} products",
                        "data": data,
                        "original_command": original_command
                    }
                else:
                    # Single product result
                    formatted = format_product(result['result'])
                    return {
                        "status": "success",
                        "response": "Found product" if formatted else "Product not found",
                        "data": [formatted] if formatted else [],
                        "original_command": original_command
                    }
            else:
                # Handle other operations (create, update, delete)
                return {
                    "status": "success",
                    "response": result.get('message', 'Operation completed successfully'),
                    "data": [],
                    "original_command": original_command
                }
        else:
            return {
                "status": result['status'],
                "response": result.get('message', 'Operation failed'),
                "data": [],
                "original_command": original_command
            }
    
    except Exception as e:
        print(f"❌ Error in format_response: {e}")
        return {
            "status": "error",
            "response": f"Response formatting error: {str(e)}",
            "data": [],
            "original_command": original_command
        }

def format_response_text(result, original_command):
    """Format response as natural language for audio output"""
    try:
        if result['status'] == 'success':
            if 'result' in result and result['result'] is not None:
                if isinstance(result['result'], list):
                    count = len(result['result'])
                    if count == 0:
                        return f"I found no products matching your request for {original_command}"
                    elif count == 1:
                        product = format_product(result['result'][0])
                        if product:
                            return f"I found one product: {product['name']} in {product['category']}, priced at ${product['price']}"
                        else:
                            return "I found one product but couldn't retrieve its details"
                    else:
                        return f"I found {count} products matching your request for {original_command}"
                else:
                    # Single product result
                    product = format_product(result['result'])
                    if product:
                        return f"I found the product: {product['name']} in {product['category']}, priced at ${product['price']}"
                    else:
                        return "Product not found"
            else:
                return result.get('message', 'Operation completed successfully')
        else:
            return f"Sorry, there was an error: {result.get('message', 'Operation failed')}"
    
    except Exception as e:
        return f"Sorry, I had trouble processing your request: {str(e)}"

if __name__ == '__main__':
    print("🚀 Starting Flask Backend Server...")
    print("📡 Available endpoints:")
    print("   - POST /api/chat (text commands)")
    print("   - GET /api/products (all products)")
    print("   - GET /api/products/<id> (specific product)")
    print("   - POST /api/products (create product)")
    print("   - PUT /api/products/<id> (update product)")
    print("   - DELETE /api/products/<id> (delete product)")
    print("   - GET /api/health (health check)")
    
    # Run in debug mode for development
    app.run(debug=True, host='0.0.0.0', port=5000)
