from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import json
from PIL import Image
import scripts.weed_detection as weed
import scripts.disease_detection as disease
import scripts.gps_simulation as gps
import scripts.obstacle_avoidance as avoid
import scripts.soil_monitor as soil
# import scripts.camera_capture as camera  # Disabled for now

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weed-detection')
def weed_detection():
    return render_template('weed_detection.html')

@app.route('/disease-detection')
def disease_detection():
    return render_template('disease_detection.html')

@app.route('/gps-simulation')
def gps_simulation():
    return render_template('gps_simulation.html')

@app.route('/obstacle-avoidance')
def obstacle_avoidance():
    return render_template('obstacle_avoidance.html')

@app.route('/soil-monitoring')
def soil_monitoring():
    return render_template('soil_monitoring.html')

@app.route('/api/weed-detection', methods=['POST'])
def api_weed_detection():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload JPG, PNG, or GIF.'}), 400
        
        # Convert directly to PIL Image without saving to disk
        image = Image.open(file.stream).convert('RGB')
        
        # Run weed detection directly on PIL image
        result = weed.predict_pil(image)
        
        return jsonify({
            'success': True,
            'label': result['label'],
            'confidence': result['prob']
        })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weed-detection/camera', methods=['POST'])
def api_weed_detection_camera():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image data provided'}), 400
        
        image_file = request.files['image']
        
        # Simple image processing without camera module
        from PIL import Image
        import io
        import base64
        
        # Convert uploaded file to PIL Image
        image_data = image_file.read()
        pil_image = Image.open(io.BytesIO(image_data)).convert('RGB')
        
        # Run weed detection
        result = weed.predict_pil(pil_image)
        
        # Convert image to base64 for display
        buffer = io.BytesIO()
        pil_image.save(buffer, format='JPEG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'label': result['label'],
            'confidence': result['prob'],
            'image': img_base64
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/disease-detection', methods=['POST'])
def api_disease_detection():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload JPG, PNG, or GIF.'}), 400
        
        # Convert directly to PIL Image without saving to disk
        image = Image.open(file.stream).convert('RGB')
        
        # Run disease detection directly on PIL image
        result = disease.predict_pil(image)
        
        return jsonify({
            'success': True,
            'label': result['label'],
            'confidence': result['prob']
        })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/disease-detection/camera', methods=['POST'])
def api_disease_detection_camera():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image data provided'}), 400
        
        image_file = request.files['image']
        
        # Simple image processing without camera module
        from PIL import Image
        import io
        import base64
        
        # Convert uploaded file to PIL Image
        image_data = image_file.read()
        pil_image = Image.open(io.BytesIO(image_data)).convert('RGB')
        
        # Run disease detection
        result = disease.predict_pil(pil_image)
        
        # Convert image to base64 for display
        buffer = io.BytesIO()
        pil_image.save(buffer, format='JPEG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'label': result['label'],
            'confidence': result['prob'],
            'image': img_base64
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gps-simulation', methods=['POST'])
def api_gps_simulation():
    try:
        data = request.get_json()
        
        start_lat = float(data.get('start_lat', 12.9716))
        start_lon = float(data.get('start_lon', 77.5946))
        rows = int(data.get('rows', 8))
        cols = int(data.get('cols', 15))
        
        result = gps.run_demo(start_lat=start_lat, start_lon=start_lon, rows=rows, cols=cols)
        
        return jsonify({
            'success': True,
            'points_count': result['points_count'],
            'html_file': result['html']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/obstacle-avoidance', methods=['POST'])
def api_obstacle_avoidance():
    try:
        data = request.get_json()
        
        start_lat = float(data.get('start_lat', 12.9716))
        start_lon = float(data.get('start_lon', 77.5946))
        rows = int(data.get('rows', 8))
        cols = int(data.get('cols', 15))
        add_obstacle = data.get('add_obstacle', False)
        
        obstacles = None
        if add_obstacle:
            obstacles = [(start_lat + 0.00024, start_lon + 0.0007)]
        
        result = avoid.run_demo_with_obstacles(
            start_lat=start_lat,
            start_lon=start_lon,
            obstacles=obstacles,
            rows=rows,
            cols=cols
        )
        
        # Generate map
        map_path = avoid.make_map_with_obstacles(
            base_path=result['base_path'],
            new_path=result['new_path'],
            obstacles=result['obstacles'],
            start_loc=result['base_path'][0]
        )
        
        obstacles_count = len(result['obstacles']) if result['obstacles'] else 0
        
        return jsonify({
            'success': True,
            'base_len': result['base_len'],
            'new_len': result['new_len'],
            'obstacles_count': obstacles_count,
            'map_file': map_path,
            'obstacles': result['obstacles']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/soil-monitoring', methods=['GET'])
def api_soil_monitoring():
    try:
        result = soil.run_demo()
        df = result['dataframe']
        
        # Convert dataframe to JSON format for charts
        chart_data = {
            'time': df['time'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
            'soil_moisture': df['soil_moisture'].tolist(),
            'temperature': df['temperature'].tolist(),
            'battery': df['battery'].tolist()
        }
        
        # Generate recommendations
        recommendations = []
        if result['moisture_latest'] < 30:
            recommendations.append("💧 Consider irrigation - soil moisture is below optimal")
        if result['temp_latest'] > 35:
            recommendations.append("🌡️ High temperature detected - monitor crop stress")
        if result['battery_latest'] < 25:
            recommendations.append("🔋 Battery low - schedule maintenance soon")
        if not recommendations:
            recommendations.append("✅ All systems operating within normal parameters")
        
        return jsonify({
            'success': True,
            'moisture_latest': result['moisture_latest'],
            'temp_latest': result['temp_latest'],
            'battery_latest': result['battery_latest'],
            'chart_data': chart_data,
            'recommendations': recommendations
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/camera/release', methods=['POST'])
def api_camera_release():
    try:
        # Simplified camera release - just return success
        return jsonify({'success': True, 'message': 'Camera released successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
