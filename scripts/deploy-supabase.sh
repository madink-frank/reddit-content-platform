#!/bin/bash

# Supabase deployment script for Reddit Content Platform
set -e

echo "🚀 Starting Supabase deployment for Reddit Content Platform..."

# Check if Supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI not found. Installing..."
    curl -L https://github.com/supabase/cli/releases/download/v1.123.4/supabase_linux_amd64.tar.gz | tar -xz
    sudo mv supabase /usr/local/bin/supabase
    echo "✅ Supabase CLI installed"
fi

# Check if logged in to Supabase
if ! supabase projects list &> /dev/null; then
    echo "❌ Not logged in to Supabase. Please run: supabase login"
    exit 1
fi

# Initialize Supabase project if not already done
if [ ! -f "supabase/config.toml" ]; then
    echo "📝 Initializing Supabase project..."
    supabase init
fi

# Link to remote project (you'll need to set your project ref)
echo "🔗 Linking to Supabase project..."
read -p "Enter your Supabase project reference: " PROJECT_REF
supabase link --project-ref $PROJECT_REF

# Run database migrations
echo "📊 Running database migrations..."
supabase db push

# Deploy Edge Functions
echo "⚡ Deploying Edge Functions..."
supabase functions deploy reddit-crawler

# Generate TypeScript types
echo "🔧 Generating TypeScript types..."
supabase gen types typescript --local > types/supabase.ts

# Set environment variables
echo "🔐 Setting up environment variables..."
echo "Please set the following environment variables in your deployment platform:"
echo ""
echo "DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.$PROJECT_REF.supabase.co:5432/postgres"
echo "SUPABASE_URL=https://$PROJECT_REF.supabase.co"
echo "SUPABASE_ANON_KEY=[YOUR-ANON-KEY]"
echo "SUPABASE_SERVICE_ROLE_KEY=[YOUR-SERVICE-ROLE-KEY]"
echo ""

# Get project details
echo "📋 Project Details:"
supabase status

echo ""
echo "✅ Supabase deployment completed!"
echo ""
echo "Next steps:"
echo "1. Update your .env file with the Supabase credentials"
echo "2. Deploy your FastAPI application to your preferred platform"
echo "3. Update CORS settings in Supabase dashboard"
echo "4. Configure authentication providers if needed"
echo ""
echo "🌐 Your Supabase project URL: https://$PROJECT_REF.supabase.co"
echo "📊 Supabase Dashboard: https://supabase.com/dashboard/project/$PROJECT_REF"