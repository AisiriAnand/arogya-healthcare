from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>AROGYA Healthcare</h1><p><a href="/dashboard">Dashboard</a></p><p><a href="/symptom-checker">Symptom Checker</a></p>'

@app.route('/dashboard')
def dashboard():
    return '<h1>Dashboard</h1><p>Dashboard working!</p><p><a href="/">Home</a></p>'

@app.route('/symptom-checker')
def symptom_checker():
    return '<h1>Symptom Checker</h1><p>Symptom checker working!</p><p><a href="/">Home</a></p>'

if __name__ == '__main__':
    print("🚀 Simple AROGYA Test Server...")
    app.run(host='0.0.0.0', port=5001, debug=True)
