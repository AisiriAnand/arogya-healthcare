const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'Backend server is running' });
});

// Sample endpoint for doctor data
app.get('/api/doctors', (req, res) => {
  const doctors = [
    {
      id: 1,
      name: 'Dr. Rajesh Kumar',
      specialty: 'General Medicine',
      hospital: 'Rural Health Center',
      experience: 10,
      rating: 4.5
    },
    {
      id: 2,
      name: 'Dr. Priya Singh',
      specialty: 'Pediatrics',
      hospital: 'Community Hospital',
      experience: 8,
      rating: 4.7
    },
    {
      id: 3,
      name: 'Dr. Amit Patel',
      specialty: 'Surgery',
      hospital: 'District Hospital',
      experience: 15,
      rating: 4.6
    }
  ];
  res.json(doctors);
});

// Sample endpoint for health articles
app.get('/api/articles', (req, res) => {
  const articles = [
    {
      id: 1,
      title: 'Understanding Diabetes',
      category: 'Chronic Diseases',
      content: 'Diabetes is a chronic disease that affects how your body processes blood glucose.',
      author: 'Dr. Health Expert',
      date: '2024-01-15'
    },
    {
      id: 2,
      title: 'Importance of Regular Exercise',
      category: 'Wellness',
      content: 'Regular exercise helps maintain a healthy lifestyle and prevents many diseases.',
      author: 'Fitness Coach',
      date: '2024-01-20'
    }
  ];
  res.json(articles);
});

// Sample endpoint for medication reminders
app.get('/api/reminders', (req, res) => {
  const reminders = [
    {
      id: 1,
      medication: 'Aspirin',
      dosage: '100mg',
      frequency: 'Once daily',
      time: '08:00 AM'
    }
  ];
  res.json(reminders);
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
  console.log(`Backend server is running on http://localhost:${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/api/health`);
});
