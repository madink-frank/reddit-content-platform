# Supabase MCP Server Setup Guide

## Current Status
✅ uvx installed and available  
⏳ Supabase project configuration needed

## Step-by-Step Setup

### 1. Create Supabase Project (5 minutes)
1. Go to https://supabase.com/dashboard
2. Sign in with your GitHub account
3. Click **"New Project"**
4. Fill in project details:
   - **Name**: `reddit-content-platform`
   - **Database Password**: Choose a secure password (save it!)
   - **Region**: Select closest to your location
5. Click **"Create new project"**
6. Wait 2-3 minutes for project creation

### 2. Get API Keys (2 minutes)
1. In your Supabase dashboard, go to **Settings** → **API**
2. Copy these two values:
   - **Project URL**: `https://[your-project-ref].supabase.co`
   - **service_role** key (the secret one, not anon/public)

### 3. Configure MCP Server
Run the interactive setup script:
```bash
python scripts/setup-supabase-mcp.py
```

Or manually update `.kiro/settings/mcp.json`:
```json
{
  "mcpServers": {
    "supabase": {
      "command": "uvx",
      "args": ["mcp-server-supabase"],
      "env": {
        "SUPABASE_URL": "https://your-actual-project-ref.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "your-actual-service-role-key"
      },
      "disabled": false,
      "autoApprove": ["get_project_url", "get_anon_key", "list_tables"]
    }
  }
}
```

### 4. Verify Connection
After updating the config:
1. Check MCP logs in Kiro for successful connection
2. The server should automatically reconnect
3. You should see logs like: `Successfully connected to MCP server`

## Troubleshooting

### Common Issues
- **"spawn uvx ENOENT"**: uvx not installed → Already fixed ✅
- **"Project reference in URL is not valid"**: Using placeholder values → Update with real project details
- **Connection timeout**: Check internet connection and Supabase project status

### Testing MCP Tools
Once connected, you can test these tools:
- `get_project_url` - Returns your project URL
- `get_anon_key` - Returns the anonymous/public key  
- `list_tables` - Lists database tables

## Next Steps After Setup
1. Set up database schema (see SUPABASE_DEPLOYMENT_STEPS.md)
2. Configure environment variables for your app
3. Deploy to Vercel/production

## Need Help?
If you encounter issues:
1. Check the MCP logs in Kiro
2. Verify your Supabase project is active
3. Confirm API keys are correct
4. Try disabling/re-enabling the MCP server