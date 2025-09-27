#!/usr/bin/env python3
"""
Minimal Flask app to test weed detection upload
"""
import sys
import os
sys.path.append('.')

from flask import Flask, request, jsonify, render_template_string
from werkzeug.utils import secure_filename
from PIL import Image
import io

# Import weed detection
from scripts import weed_detection

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Simple HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Weed Detection Upload Test</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        .upload-area { border: 2px dashed #007bff; padding: 30px; text-align: center; margin: 20px 0; border-radius: 10px; }
        .result { background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 5px; border-left: 4px solid #007bff; }
        button { background: #007bff; color: white; border: none; padding: 15px 30px; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        .error { color: #dc3545; }
        .success { color: #28a745; }
        .loading { color: #6c757d; }
    </style>
</head>
<body>
    <h1>🌿 Weed Detection Upload Test</h1>
    
    <div class="upload-area">
        <h3>📁 Select Image for Weed Detection</h3>
        <form id="uploadForm" enctype="multipart/form-data">
            <input type="file" id="fileInput" accept="image/*" required style="margin: 10px;">
            <br><br>
            <button type="submit">🔍 Analyze for Weeds</button>
        </form>
    </div>
    
    <div id="result" style="display: none;"></div>
    
    <div class="upload-area" style="background: #f8f9fa;">
        <h4>📋 Instructions</h4>
        <p>1. Select any image file (JPG, PNG, GIF)</p>
        <p>2. Click "Analyze for Weeds"</p>
        <p>3. Wait for AI analysis results</p>
        <p>4. See if it detects rice crop or weed</p>
    </div>
    
    <script>
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            const resultDiv = document.getElementById('result');
            
            if (!file) {
                alert('Please select a file first!');
                return;
            }
            
            // Show loading
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '<div class="loading">🔄 Analyzing image with AI...</div>';
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const confidence = (data.confidence * 100).toFixed(1);
                    const isWeed = data.label === 'weed';
                    const emoji = isWeed ? '🌿' : '🌾';
                    const colorClass = isWeed ? 'error' : 'success';
                    
                    resultDiv.innerHTML = `
                        <div class="result">
                            <h3>🎯 Analysis Complete!</h3>
                            <div class="${colorClass}" style="font-size: 1.5em; font-weight: bold;">
                                ${emoji} ${data.label.toUpperCase()}
                            </div>
                            <div style="margin: 10px 0;">Confidence: <strong>${confidence}%</strong></div>
                            ${isWeed ? 
                                '<div style="color: #dc3545; margin-top: 15px;">⚠️ <strong>Weeds detected!</strong> Consider weed control measures.</div>' : 
                                '<div style="color: #28a745; margin-top: 15px;">✅ <strong>Healthy rice crop detected!</strong> Field looks good.</div>'
                            }
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `<div class="result error">❌ Error: ${data.error}</div>`;
                }
                
            } catch (error) {
                resultDiv.innerHTML = `<div class="result error">❌ Upload failed: ${error.message}</div>`;
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        print("Upload request received")
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type. Please upload JPG, PNG, or GIF.'}), 400
        
        print(f"Processing file: {file.filename}")
        
        # Convert to PIL Image
        image = Image.open(file.stream).convert('RGB')
        print(f"Image loaded: {image.size}")
        
        # Run weed detection
        result = weed_detection.predict_pil(image)
        print(f"Prediction result: {result}")
        
        return jsonify({
            'success': True,
            'label': result['label'],
            'confidence': result['prob']
        })
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/status')
def status():
    return jsonify({'status': 'Server is running', 'weed_detection': 'available'})

if __name__ == '__main__':
    print("🚀 Starting Minimal Weed Detection Server...")
    print("🌐 Open: http://localhost:5002")
    print("📁 Upload any image to test weed detection")
    app.run(debug=True, host='0.0.0.0', port=5002)
