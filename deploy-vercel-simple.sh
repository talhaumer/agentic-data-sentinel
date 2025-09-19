#!/bin/bash
# Simple Vercel deployment script

echo "🚀 Deploying Data Sentinel v1 to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Login to Vercel (if not already logged in)
echo "🔐 Checking Vercel authentication..."
vercel whoami || vercel login

# Deploy to Vercel
echo "📦 Deploying application..."
vercel --prod

echo "✅ Deployment complete!"
echo "🌐 Your app should be available at the provided URL"
