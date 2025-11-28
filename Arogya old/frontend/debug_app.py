from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def home():
    try:
        return render_template('home.html')
    except Exception as e:
        return f"Template Error: {str(e)}"

@app.route('/test')
def test():
    return '<h1>AROGYA Healthcare Platform</h1><p>Working!</p><a href="/">Go Home</a>'

if __name__ == '__main__':
    print("🚀 Starting DEBUG AROGYA Frontend...")
    print("📱 Frontend: http://localhost:5001")
    print("🧪 Test page: http://localhost:5001/test")
    app.run(host='0.0.0.0', port=5001, debug=True)
