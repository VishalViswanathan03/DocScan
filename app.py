from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from flasgger import Swagger

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'  # Replace with a strong secret key

swagger = Swagger(app)

@app.route('/')
def index():
    """
    Homepage that redirects logged-in users to their profile.
    ---
    responses:
      200:
        description: Homepage rendered
    """
    if 'username' in session:
        return redirect(url_for('profile'))
    return render_template('index.html')

@app.route('/api/example', methods=['GET'])
def api_example():
    """
    Example API endpoint.
    ---
    responses:
      200:
        description: Returns a simple JSON message.
        schema:
          type: object
          properties:
            message:
              type: string
              example: Hello, World!
    """
    return jsonify({"message": "Hello, World!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
