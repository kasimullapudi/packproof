from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
import os
import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Verified connection string with database name
app.config["MONGO_URI"] = "mongodb+srv://kasimullapudi42:YxDsHlSMsI7S7jwq@cluster0.rkyag.mongodb.net/uploads?retryWrites=true&w=majority"
mongo = PyMongo(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/healthcheck')
def healthcheck():
    try:
        mongo.db.command('ping')
        return jsonify({
            "status": "success",
            "database": str(mongo.db),
            "collection": str(mongo.db.files)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        print(f"file extension {file}")
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Remove the database connection check - it's not needed
        # The healthcheck already verified the connection
        
        # Directly insert the document
        result = mongo.db.files.insert_one({
            "filename": filename,
            "filepath": file_path,
            "size": os.path.getsize(file_path),
            "upload_time": datetime.datetime.utcnow()
        })

        return jsonify({
            "message": "File uploaded successfully",
            "file_id": str(result.inserted_id)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True)