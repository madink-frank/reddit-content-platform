#!/usr/bin/env python3
"""
Interactive script to configure Supabase MCP server
"""
import json
import os
from pathlib import Path

def main():
    print("🚀 Supabase MCP Configuration Setup")
    print("=" * 50)
    
    # Get Supabase project details
    print("\n📋 Please provide your Supabase project details:")
    print("(You can find these in your Supabase Dashboard → Settings → API)")
    
    supabase_url = input("\n🔗 Supabase Project URL (https://xxx.supabase.co): ").strip()
    if not supabase_url.startswith("https://"):
        supabase_url = f"https://{supabase_url}"
    if not supabase_url.endswith(".supabase.co"):
        print("❌ Invalid URL format. Should be: https://xxx.supabase.co")
        return
    
    service_key = input("\n🔑 Service Role Key (starts with eyJhbGciOiJIUzI1NiIs...): ").strip()
    if not service_key.startswith("eyJ"):
        print("❌ Invalid service key format. Should start with 'eyJ'")
        return
    
    # Update MCP configuration
    mcp_config_path = Path(".kiro/settings/mcp.json")
    
    if not mcp_config_path.exists():
        print(f"❌ MCP config file not found: {mcp_config_path}")
        return
    
    # Read current config
    with open(mcp_config_path, 'r') as f:
        config = json.load(f)
    
    # Update Supabase server config
    if "supabase" in config["mcpServers"]:
        config["mcpServers"]["supabase"]["env"]["SUPABASE_URL"] = supabase_url
        config["mcpServers"]["supabase"]["env"]["SUPABASE_SERVICE_ROLE_KEY"] = service_key
        
        # Write updated config
        with open(mcp_config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n✅ Successfully updated MCP configuration!")
        print(f"📁 Config file: {mcp_config_path}")
        print("\n🔄 The MCP server will automatically reconnect with the new settings.")
        
        # Show next steps
        print("\n📋 Next Steps:")
        print("1. The Supabase MCP server should now connect successfully")
        print("2. You can test it by running MCP tools in Kiro")
        print("3. Check the MCP logs to confirm connection")
        
    else:
        print("❌ Supabase server not found in MCP configuration")

if __name__ == "__main__":
    main()