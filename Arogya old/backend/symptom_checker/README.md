# Symptom Checker AI Module

Machine learning powered disease prediction system for the AROGYA Healthcare platform.

## Overview

This module provides AI-powered symptom analysis using a trained machine learning model that achieves 100% accuracy on 41 disease categories.

### Key Features

- **100% Accuracy**: Perfect accuracy on trained disease categories
- **41 Disease Categories**: Comprehensive disease coverage
- **TF-IDF + Logistic Regression**: Robust ML pipeline
- **Real-time Predictions**: Instant AI analysis
- **RESTful API**: Clean integration with frontend

## Model Performance

- **Training Data**: 4,920 medical symptom cases
- **Test Accuracy**: 100% (1.0000)
- **Model**: Logistic Regression with TF-IDF features
- **Random Seed**: 42 (reproducible results)
- **Feature Extraction**: TF-IDF Vectorizer (max_features=1000)

## Supported Diseases

The model can predict 41 different diseases including:
- Fungal infection
- Allergy
- GERD
- Diabetes
- Migraine
- Pneumonia
- Chicken pox
- Dengue
- Typhoid
- Hepatitis (A, B, C, D, E)
- And 31 more...

## Installation & Setup

### Prerequisites

```bash
pip install -r requirements.txt
```

### Training the Model

```bash
cd backend
python symptom_checker/train.py --data ../../DiseaseAndSymptoms.csv --out symptom_checker/model/pipeline.joblib
```

### Running the Backend Server

```bash
cd backend
uvicorn main:app --reload --port 5000
```

## API Endpoints

### GET /api/symptom-checker/symptom-list

Returns list of available symptoms from training data.

**Response:**
```json
{
  "symptoms": ["itching", "skin_rash", "nodal_skin_eruptions", ...]
}
```

### POST /api/symptom-checker/predict

Predicts diseases based on symptoms.

**Request:**
```json
{
  "symptoms": ["itching", "skin_rash"],
  "description": "I have itching and skin rash"
}
```

**Response:**
```json
{
  "predictions": [
    {
      "condition": "Fungal infection",
      "score": 0.95
    },
    {
      "condition": "Allergy", 
      "score": 0.05
    }
  ],
  "model_version": "v1",
  "explain": ["itching", "skin_rash"]
}
```

## Testing

Run the test suite:

```bash
pytest backend/symptom_checker/tests/
```

## Model Architecture

### Data Preprocessing

1. **Load CSV data** with disease-symptom mappings
2. **Clean missing values** (fill with empty strings)
3. **Combine symptoms** into text format per sample
4. **Remove empty samples**

### Feature Engineering

- **TF-IDF Vectorization** (max_features=1000, ngram_range=(1,2))
- **Text preprocessing**: lowercase, remove special characters
- **Stop words removal** for English

### Model Training

1. **Stratified split**: 80% train, 20% test
2. **Model selection**: Logistic Regression (best performer)
3. **Evaluation**: Accuracy, Precision, Recall, F1-score
4. **Pipeline creation**: TF-IDF + Classifier

### Performance Metrics

- **Accuracy**: 1.0000 (100%)
- **Macro F1**: 1.0000
- **Weighted F1**: 1.0000
- **Training samples**: 3,936
- **Test samples**: 984

## Files Structure

```
symptom_checker/
├── train.py              # Training script
├── model/
│   ├── pipeline.joblib   # Trained ML pipeline
│   ├── metrics.json      # Performance metrics
│   └── model_info.json   # Model metadata
├── tests/
│   └── test_predict.py   # API tests
├── report.md             # Detailed training report
└── README.md             # This file
```

## Frontend Integration

The frontend (`/symptom-checker`) integrates with this API:

1. **Load symptoms** from `/api/symptom-checker/symptom-list`
2. **Send predictions** to `/api/symptom-checker/predict`
3. **Display results** with confidence scores
4. **Show model info** and disclaimers

## Limitations & Considerations

### Medical Disclaimer
- This tool is for informational purposes only
- Not a substitute for professional medical advice
- Always consult healthcare professionals

### Technical Limitations
- Only trained on 41 disease categories
- Based on pattern matching in training data
- May not reflect individual medical circumstances
- Requires symptom text in English

### Ethical Considerations
- Transparent about model capabilities
- Clear medical disclaimers
- Privacy-focused (no personal data stored)
- Reproducible results (fixed random seed)

## Future Improvements

1. **More Data**: Expand training dataset
2. **More Diseases**: Add additional disease categories
3. **Better Features**: Include patient demographics
4. **Ensemble Models**: Combine multiple ML approaches
5. **Real-world Validation**: Clinical testing

## Troubleshooting

### Model Not Loading
- Ensure `pipeline.joblib` exists in `symptom_checker/model/`
- Check backend logs for loading errors
- Verify all dependencies are installed

### API Errors
- Check backend server is running on port 5000
- Verify CORS configuration
- Check request format matches API specification

### Poor Predictions
- Ensure symptoms are described clearly
- Use English language symptoms
- Check if symptoms match training data patterns

## Development

### Adding New Diseases
1. Update the CSV training data
2. Retrain the model using `train.py`
3. Update the pipeline file
4. Test with new predictions

### Model Retraining
```bash
# Retrain with new data
python symptom_checker/train.py --data new_data.csv --out symptom_checker/model/pipeline.joblib

# Restart backend server
uvicorn main:app --reload --port 5000
```

## License & Credits

- Trained on medical symptom data
- ML pipeline using scikit-learn
- FastAPI backend integration
- Part of AROGYA Healthcare platform
