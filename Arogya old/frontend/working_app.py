from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'arogya-healthcare-secret-key'

# Sample data
doctors_data = [
    {"id": 1, "name": "Dr. Rajesh Kumar", "specialty": "General Medicine", "hospital": "Rural Health Center", "experience": 10, "rating": 4.5},
    {"id": 2, "name": "Dr. Priya Singh", "specialty": "Pediatrics", "hospital": "Community Hospital", "experience": 8, "rating": 4.7}
]

hospitals_data = [
    {"id": 1, "name": "Rural Health Center", "address": "Village Road, District 1", "phone": "123-456-7890", "services": ["General Medicine", "Maternity"], "rating": 4.2}
]

# Routes
@app.route('/')
def home():
    try:
        return render_template('home.html')
    except Exception as e:
        return f'<h1>AROGYA Healthcare</h1><p>Template Error: {str(e)}</p><p><a href="/dashboard">Dashboard</a></p>'

@app.route('/dashboard')
def dashboard():
    try:
        return render_template('dashboard.html')
    except Exception as e:
        return f'<h1>Dashboard</h1><p>Template Error: {str(e)}</p><p><a href="/">Home</a></p>'

@app.route('/symptom-checker')
def symptom_checker():
    try:
        return render_template('symptom_checker.html')
    except Exception as e:
        return f'<h1>Symptom Checker</h1><p>Template Error: {str(e)}</p><p><a href="/">Home</a></p>'

@app.route('/find-hospitals')
def find_hospitals():
    try:
        return render_template('find_hospitals.html')
    except Exception as e:
        return f'<h1>Find Hospitals</h1><p>Template Error: {str(e)}</p><p><a href="/">Home</a></p>'

@app.route('/hospital-finder')
def hospital_finder():
    try:
        return render_template('hospital_finder.html')
    except Exception as e:
        return f'<h1>Hospital Finder</h1><p>Template Error: {str(e)}</p><p><a href="/">Home</a></p>'

@app.route('/medication-reminders')
def medication_reminders():
    try:
        return render_template('test_reminders.html')
    except Exception as e:
        return f'<h1>Medication Reminders</h1><p>Template Error: {str(e)}</p><p><a href="/">Home</a></p>'

@app.route('/health-articles')
def health_articles():
    try:
        return render_template('health_articles.html')
    except Exception as e:
        return f'<h1>Health Articles</h1><p>Template Error: {str(e)}</p><p><a href="/">Home</a></p>'

@app.route('/schemes')
def schemes():
    try:
        return render_template('schemes.html')
    except Exception as e:
        return f'<h1>Government Schemes</h1><p>Template Error: {str(e)}</p><p><a href="/">Home</a></p>'

@app.route('/diet-plans')
def diet_plans():
    try:
        return render_template('diet_plans.html')
    except Exception as e:
        return f'<h1>Diet Plans</h1><p>Template Error: {str(e)}</p><p><a href="/">Home</a></p>'

# API Routes
@app.route('/api/health')
def api_health():
    return jsonify({"status": "Backend server is running"})

@app.route('/api/doctors')
def api_doctors():
    return jsonify(doctors_data)

@app.route('/api/hospitals')
def api_hospitals():
    return jsonify(hospitals_data)

@app.route('/api/symptom-check', methods=['POST'])
def symptom_check():
    data = request.get_json()
    symptoms = data.get('symptoms', [])
    severity = "mild"
    recommendations = ["Rest and hydrate", "Monitor symptoms"]
    
    if len(symptoms) > 5:
        severity = "severe"
        recommendations = ["Consult doctor immediately", "Go to nearest hospital"]
    elif len(symptoms) > 2:
        severity = "moderate"
        recommendations = ["Consult doctor if symptoms persist", "Take over-the-counter medication"]
    
    return jsonify({
        "severity": severity,
        "recommendations": recommendations,
        "possible_conditions": ["Common Cold", "Flu", "Allergies"] if severity == "mild" else ["Infection", "Inflammation"]
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    print(f"AROGYA Frontend server running on http://localhost:{port}")
    print("Available routes:")
    print("   / - Home page")
    print("   /dashboard - Dashboard")
    print("   /symptom-checker - Symptom checker")
    print("   /find-hospitals - Hospital finder")
    print("   /medication-reminders - Medication reminders")
    print("   /health-articles - Health articles")
    print("   /schemes - Government schemes")
    print("   /diet-plans - Diet plans")
    app.run(host='0.0.0.0', port=port, debug=True)
