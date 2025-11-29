"""
Supabase Authentication Configuration
"""

import os
from supabase import create_client, Client

# Supabase Configuration - Your actual Supabase project details
SUPABASE_URL = "https://uaobzwfyiafogxymergn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVhb2J6d2Z5aWFmb2d4eW1lcmduIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ0MTgwMDMsImV4cCI6MjA3OTk5NDAwM30.VLpKZUNcVf-0GV505Nm-QFJx3JyJ3JGOY7JVHNPDf1E"

# For development, you can use these environment variables or replace with actual values
# In production, use environment variables for security
supabase_url = os.getenv("SUPABASE_URL", SUPABASE_URL)
supabase_key = os.getenv("SUPABASE_KEY", SUPABASE_KEY)

# Initialize Supabase client
supabase: Client = create_client(supabase_url, supabase_key)

# Authentication settings
JWT_SECRET = os.getenv("JWT_SECRET", "your-jwt-secret-key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Email configuration (for Supabase auth)
EMAIL_CONFIRMATION_REQUIRED = True
PASSWORD_MIN_LENGTH = 6
