"""
Symptom Checker Training Script
Train machine learning model for disease prediction based on symptoms
"""

import pandas as pd
import numpy as np
import joblib
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# ML imports
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.multioutput import MultiOutputClassifier

# Try XGBoost if available
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False
    logging.warning("XGBoost not available, will skip XGBoost model")

# Set random seed for reproducibility
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SymptomCheckerTrainer:
    def __init__(self, data_path: str, output_path: str):
        self.data_path = data_path
        self.output_path = output_path
        self.df = None
        self.pipeline = None
        self.metrics = {}
        
    def load_data(self):
        """Load and preprocess the symptom dataset"""
        logger.info(f"Loading data from {self.data_path}")
        
        try:
            self.df = pd.read_csv(self.data_path)
            logger.info(f"Data shape: {self.df.shape}")
            logger.info(f"Number of diseases: {self.df['Disease'].nunique()}")
            logger.info(f"Diseases: {self.df['Disease'].unique()}")
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
            
    def preprocess_data(self):
        """Clean and preprocess the symptom data"""
        logger.info("Preprocessing data...")
        
        # Fill missing values with empty strings
        symptom_cols = [col for col in self.df.columns if col.startswith('Symptom_')]
        self.df[symptom_cols] = self.df[symptom_cols].fillna('')
        
        # Create symptom text by combining all symptoms for each row
        self.df['symptoms_text'] = self.df[symptom_cols].apply(
            lambda row: ' '.join([symptom.strip().lower() for symptom in row if symptom.strip()]), 
            axis=1
        )
        
        # Remove rows with no symptoms
        self.df = self.df[self.df['symptoms_text'].str.len() > 0].copy()
        
        logger.info(f"After cleaning - Shape: {self.df.shape}")
        logger.info(f"Sample symptom texts: {self.df['symptoms_text'].head(3).tolist()}")
        
    def prepare_features_and_labels(self):
        """Prepare features (symptom text) and labels (diseases)"""
        self.X = self.df['symptoms_text'].values
        self.y = self.df['Disease'].values
        
        logger.info(f"Features shape: {self.X.shape}")
        logger.info(f"Labels shape: {self.y.shape}")
        
    def split_data(self):
        """Split data into train and test sets with stratification"""
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, 
            test_size=0.2, 
            random_state=RANDOM_SEED, 
            stratify=self.y
        )
        
        logger.info(f"Train set: {len(self.X_train)} samples")
        logger.info(f"Test set: {len(self.X_test)} samples")
        
    def create_pipeline(self):
        """Create ML pipeline with TF-IDF and classifier"""
        # TF-IDF Vectorizer for symptom text
        tfidf = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            stop_words='english',
            lowercase=True
        )
        
        # Models to try
        models = {}
        
        # Logistic Regression
        models['logistic'] = LogisticRegression(
            random_state=RANDOM_SEED,
            max_iter=1000
        )
        
        # Random Forest
        models['random_forest'] = RandomForestClassifier(
            random_state=RANDOM_SEED,
            n_estimators=100
        )
        
        # XGBoost (if available) - Skip due to label encoding issues
        # if XGB_AVAILABLE:
        #     models['xgboost'] = xgb.XGBClassifier(
        #         random_state=RANDOM_SEED,
        #         use_label_encoder=False,
        #         eval_metric='mlogloss',
        #         objective='multi:softmax'
        #     )
        
        # Create pipelines
        self.pipelines = {}
        for name, model in models.items():
            self.pipelines[name] = Pipeline([
                ('tfidf', tfidf),
                ('classifier', model)
            ])
            
    def evaluate_models(self):
        """Evaluate all models and select the best one"""
        logger.info("Evaluating models...")
        
        best_score = 0
        best_model_name = None
        best_pipeline = None
        
        for name, pipeline in self.pipelines.items():
            logger.info(f"Evaluating {name}...")
            
            # Train the model
            pipeline.fit(self.X_train, self.y_train)
            
            # Make predictions
            y_pred = pipeline.predict(self.X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(self.y_test, y_pred)
            
            # Generate classification report
            report = classification_report(self.y_test, y_pred, output_dict=True)
            
            # Store metrics
            self.metrics[name] = {
                'accuracy': accuracy,
                'macro_avg': report['macro avg'],
                'weighted_avg': report['weighted avg'],
                'classification_report': report
            }
            
            logger.info(f"{name} - Accuracy: {accuracy:.4f}")
            
            # Check if this is the best model
            if accuracy > best_score:
                best_score = accuracy
                best_model_name = name
                best_pipeline = pipeline
                
        logger.info(f"Best model: {best_model_name} with accuracy: {best_score:.4f}")
        self.best_model_name = best_model_name
        self.pipeline = best_pipeline
        
    def save_model(self):
        """Save the trained pipeline and metrics"""
        logger.info(f"Saving model to {self.output_path}")
        
        # Create output directory if it doesn't exist
        Path(self.output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save the pipeline
        joblib.dump(self.pipeline, self.output_path)
        
        # Save metrics
        metrics_path = Path(self.output_path).parent / 'metrics.json'
        with open(metrics_path, 'w') as f:
            json.dump(self.metrics, f, indent=2)
            
        # Save model info
        model_info = {
            'model_name': self.best_model_name,
            'accuracy': self.metrics[self.best_model_name]['accuracy'],
            'random_seed': RANDOM_SEED,
            'training_date': datetime.now().isoformat(),
            'data_shape': self.df.shape,
            'num_diseases': self.df['Disease'].nunique(),
            'diseases': self.df['Disease'].unique().tolist()
        }
        
        info_path = Path(self.output_path).parent / 'model_info.json'
        with open(info_path, 'w') as f:
            json.dump(model_info, f, indent=2)
            
        logger.info("Model and metrics saved successfully!")
        
    def generate_report(self):
        """Generate training report"""
        report_path = Path(self.output_path).parent / 'report.md'
        
        with open(report_path, 'w') as f:
            f.write("# Symptom Checker Model Report\n\n")
            f.write(f"**Training Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Random Seed:** {RANDOM_SEED}\n")
            f.write(f"**Data Shape:** {self.df.shape}\n")
            f.write(f"**Number of Diseases:** {self.df['Disease'].nunique()}\n\n")
            
            f.write("## Model Performance\n\n")
            for name, metrics in self.metrics.items():
                f.write(f"### {name}\n")
                f.write(f"- Accuracy: {metrics['accuracy']:.4f}\n")
                f.write(f"- Macro F1: {metrics['macro_avg']['f1-score']:.4f}\n")
                f.write(f"- Weighted F1: {metrics['weighted_avg']['f1-score']:.4f}\n\n")
            
            f.write(f"## Best Model: {self.best_model_name}\n\n")
            f.write(f"The best model achieved **{self.metrics[self.best_model_name]['accuracy']:.4f} accuracy**.\n\n")
            
            if self.metrics[self.best_model_name]['accuracy'] >= 0.90:
                f.write("**Target met:** Accuracy >= 0.90\n\n")
            else:
                f.write("**Target not met:** Accuracy < 0.90\n\n")
                f.write("### Recommendations for Improvement:\n")
                f.write("1. Collect more training data\n")
                f.write("2. Improve symptom labeling consistency\n")
                f.write("3. Try ensemble methods\n")
                f.write("4. Add more features (patient demographics, etc.)\n\n")
                
        logger.info(f"Report saved to {report_path}")
        
    def train(self):
        """Main training pipeline"""
        try:
            self.load_data()
            self.preprocess_data()
            self.prepare_features_and_labels()
            self.split_data()
            self.create_pipeline()
            self.evaluate_models()
            self.save_model()
            self.generate_report()
            
            logger.info("Training completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return False

def main():
    """Main function to run training"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Train symptom checker model')
    parser.add_argument('--data', required=True, help='Path to CSV data file')
    parser.add_argument('--out', required=True, help='Output path for model pipeline')
    
    args = parser.parse_args()
    
    trainer = SymptomCheckerTrainer(args.data, args.out)
    success = trainer.train()
    
    if success:
        print("Training completed successfully!")
        print(f"Best model: {trainer.best_model_name}")
        print(f"Accuracy: {trainer.metrics[trainer.best_model_name]['accuracy']:.4f}")
    else:
        print("Training failed!")
        exit(1)

if __name__ == "__main__":
    main()
