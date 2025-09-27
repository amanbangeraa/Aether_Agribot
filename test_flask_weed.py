#!/usr/bin/env python3
"""
Standalone Flask test for weed detection
"""
import sys
import os
sys.path.append('.')

from flask import Flask, request, jsonify, render_template
from PIL import Image
import io
import base64
from scripts import weed_detection

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>Weed Detection Test Server</h1>
    <p><a href="/test-weed">Go to Weed Detection Test</a></p>
    '''

@app.route('/test-weed')
def test_weed():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Weed Detection Test</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .upload-area { border: 2px dashed #ccc; padding: 20px; text-align: center; margin: 20px 0; }
            .result { background: #f0f0f0; padding: 15px; margin: 20px 0; border-radius: 5px; }
            button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <h1>🌿 Weed Detection Test</h1>
        
        <div class="upload-area">
            <h3>Upload Image for Analysis</h3>
            <form id="uploadForm" enctype="multipart/form-data">
                <input type="file" id="fileInput" accept="image/*" required>
                <br><br>
                <button type="submit">🔍 Analyze Image</button>
            </form>
        </div>
        
        <div id="result" class="result" style="display: none;">
            <h3>Analysis Result:</h3>
            <div id="resultContent"></div>
        </div>
        
        <div id="loading" style="display: none; text-align: center;">
            <p>🔄 Analyzing image...</p>
        </div>
        
        <script>
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            
            if (!file) {
                alert('Please select a file');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').style.display = 'none';
            
            try {
                const response = await fetch('/api/test-weed-detection', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                // Hide loading
                document.getElementById('loading').style.display = 'none';
                
                // Show result
                const resultDiv = document.getElementById('result');
                const resultContent = document.getElementById('resultContent');
                
                if (data.success) {
                    const confidence = (data.confidence * 100).toFixed(1);
                    const isWeed = data.label === 'weed';
                    const emoji = isWeed ? '🌿' : '🌾';
                    const color = isWeed ? '#ff9800' : '#4caf50';
                    
                    resultContent.innerHTML = `
                        <div style="color: ${color}; font-size: 1.2em; font-weight: bold;">
                            ${emoji} ${data.label.toUpperCase()}
                        </div>
                        <div>Confidence: ${confidence}%</div>
                        ${isWeed ? 
                            '<div style="color: #ff9800; margin-top: 10px;">⚠️ Weed detected - consider treatment</div>' : 
                            '<div style="color: #4caf50; margin-top: 10px;">✅ Healthy crop detected</div>'
                        }
                    `;
                } else {
                    resultContent.innerHTML = `<div style="color: red;">❌ Error: ${data.error}</div>`;
                }
                
                resultDiv.style.display = 'block';
                
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                alert('Error: ' + error.message);
            }
        });
        </script>
    </body>
    </html>
    '''

@app.route('/api/test-weed-detection', methods=['POST'])
def api_test_weed_detection():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Convert file to PIL Image
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # Run weed detection
        result = weed_detection.predict_pil(image)
        
        return jsonify({
            'success': True,
            'label': result['label'],
            'confidence': result['prob']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Weed Detection Test Server...")
    print("📱 Open your browser to: http://localhost:5001/test-weed")
    print("🔍 Upload an image to test weed detection")
    app.run(debug=True, host='0.0.0.0', port=5001)
