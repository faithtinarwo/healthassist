import os
import random
import pandas as pd
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from models import db, User, HealthRecord
from transformers import pipeline

# Load environment variables from .env file (Ensure that .env is not pushed to GitHub)
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Ensure secret keys are securely loaded from environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_default_secret_key')  # Replace with secure secret key

# Load database configuration from environment variables
db_user = os.getenv('DB_USER', 'root')
db_password = os.getenv('DB_PASSWORD', '')
db_host = os.getenv('DB_HOST', 'localhost')
db_name = os.getenv('DB_NAME', 'telemedicine')

# Avoid hardcoding sensitive information. Ensure it is fetched from environment variables.
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{db_user}:{db_password}@{db_host}/{db_name}"

# Initialize the database
db.init_app(app)

# Load the dataset (Ensure dataset.csv is securely stored and not pushed to GitHub)
csv_file_path = "dataset.csv"  # Update this path to your dataset location
try:
    data = pd.read_csv(csv_file_path)
    data.fillna('', inplace=True)  # Handle missing values
    print("Dataset loaded successfully")
except Exception as e:
    print(f"Error loading dataset: {e}")
    data = None

# Set up the Hugging Face model pipeline (Ensure model is public or locally saved to avoid sensitive data leakage)
try:
    chatbot = pipeline("text-generation", model="gpt2")  # Update to a custom model if needed
except Exception as e:
    print(f"Error initializing Hu
    gging Face pipeline: {e}")
    chatbot = None

@app.route('/')
def index():
    """Render the homepage."""
    return render_template('index.html')

# Route for Disease Prediction
@app.route('/predict', methods=['POST'])
def predict_disease():
    """Predict a disease based on symptoms provided."""
    try:
        symptoms = request.json.get('symptoms', [])
        if not symptoms:
            return jsonify({'error': 'No symptoms provided'}), 400

        if data is not None:
            prediction = get_disease_by_symptoms(symptoms)
        else:
            return jsonify({'error': 'Dataset not loaded. Unable to predict diseases.'}), 500

        return jsonify({'prediction': prediction})
    except Exception as e:
        print(f"Error in /predict route: {e}")  # Log the detailed error
        return jsonify({'error': str(e)}), 500

# Route for Personalized Treatment
@app.route('/personalized_medicine', methods=['POST'])
def personalized_medicine():
    """Provide a personalized treatment plan based on patient data."""
    try:
        patient_data = request.json.get('patient_data', {})
        if not patient_data:
            return jsonify({'error': 'No patient data provided'}), 400

        treatment_plan = recommend_treatment(patient_data)
        return jsonify({'treatment_plan': treatment_plan})
    except Exception as e:
        print(f"Error in /personalized_medicine route: {e}")  # Log the detailed error
        return jsonify({'error': str(e)}), 500

# Route for Mental Health Chatbot
@app.route('/chat', methods=['POST'])
def chat():
    """Provide chatbot responses to user messages."""
    try:
        user_message = request.json.get('message', '')
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        bot_reply = get_chatbot_response(user_message)
        return jsonify({'reply': bot_reply})
    except Exception as e:
        print(f"Error in /chat route: {e}")  # Log the detailed error
        return jsonify({'error': str(e)}), 500

# AI Model Functions
def get_disease_by_symptoms(symptoms):
    """Predict diseases based on symptoms using the loaded dataset."""
    try:
        matched_diseases = []
        for symptom in symptoms:
            results = data[data['Symptoms'].str.contains(symptom, case=False, na=False)]
            matched_diseases.extend(results['Disease'].unique())
        if matched_diseases:
            return list(set(matched_diseases))  # Return unique diseases
        else:
            return ["No matching diseases found."]
    except Exception as e:
        print(f"Error in get_disease_by_symptoms: {e}")
        return ["Error processing symptoms."]

def recommend_treatment(patient_data):
    """Simulate treatment recommendation based on patient data."""
    condition = patient_data.get('condition', 'unknown condition')
    return f"Personalized treatment plan for {condition}"

def get_chatbot_response(message):
    """Generate a chatbot response using Hugging Face GPT-2."""
    if chatbot:
        try:
            response = chatbot(f"User says: {message} \nHealthAssist Bot:")
            return response[0]['generated_text'].strip()
        except Exception as e:
            print(f"Error generating chatbot response: {e}")
            return "Sorry, there was an error processing your request."
    else:
        return "Chatbot is currently unavailable. Please try again later."

# Run the application
if __name__ == "__main__":
    app.run(debug=True)
