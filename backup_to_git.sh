#!/bin/bash

# Set Git configuration
export HOME=/home/ubuntu

# Navigate to your project directory
cd /home/ubuntu/officetracker

# Add all changes
git add office_tracker.db

# Create a commit with timestamp
commit_message="Automated DB backup $(date '+%Y-%m-%d %H:%M:%S')"
git commit -m "$commit_message"

# Push to remote repository
git push origin main 