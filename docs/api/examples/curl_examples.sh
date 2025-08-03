#!/bin/bash

# Reddit Content Platform API - cURL Examples
# Make sure to set your base URL and tokens

BASE_URL="http://localhost:8000"
ACCESS_TOKEN="your_access_token_here"
REFRESH_TOKEN="your_refresh_token_here"

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

echo -e "${GREEN}Reddit Content Platform API - cURL Examples${NC}"
echo "=============================================="

# Function to make authenticated requests
auth_request() {
    curl -s -H "Authorization: Bearer $ACCESS_TOKEN" -H "Content-Type: application/json" "$@"
}

echo -e "\\n${YELLOW}1. Authentication${NC}"
echo "=================="

echo "Starting OAuth2 flow..."
curl -X GET "$BASE_URL/api/v1/auth/login"

echo -e "\\nExchange code for tokens (replace with actual code and state):"
echo "curl -X POST \"$BASE_URL/api/v1/auth/login\" \\\\"
echo "  -H \"Content-Type: application/json\" \\\\"
echo "  -d '{\"code\": \"your_auth_code\", \"state\": \"your_state\"}'"

echo -e "\\nRefresh token:"
echo "curl -X POST \"$BASE_URL/api/v1/auth/refresh\" \\\\"
echo "  -H \"Authorization: Bearer $REFRESH_TOKEN\""

echo -e "\\n${YELLOW}2. Keywords Management${NC}"
echo "======================"

echo "Create keyword:"
KEYWORD_RESULT=$(auth_request -X POST "$BASE_URL/api/v1/keywords" \\
  -d '{"keyword": "artificial intelligence", "description": "AI discussions"}')
echo "$KEYWORD_RESULT" | jq '.'

echo -e "\\nGet keywords:"
auth_request -X GET "$BASE_URL/api/v1/keywords?page=1&page_size=20" | jq '.'

echo -e "\\nGet keyword by ID:"
auth_request -X GET "$BASE_URL/api/v1/keywords/1" | jq '.'

echo -e "\\nUpdate keyword:"
auth_request -X PUT "$BASE_URL/api/v1/keywords/1" \\
  -d '{"keyword": "machine learning", "description": "Updated ML description"}' | jq '.'

echo -e "\\n${YELLOW}3. Crawling Operations${NC}"
echo "======================"

echo "Start crawling:"
CRAWL_RESULT=$(auth_request -X POST "$BASE_URL/api/v1/crawling/start" \\
  -d '{"keyword_ids": [1, 2], "limit": 100, "subreddits": ["MachineLearning", "artificial"]}')
echo "$CRAWL_RESULT" | jq '.'

echo -e "\\nGet crawling status:"
auth_request -X GET "$BASE_URL/api/v1/crawling/status" | jq '.'

echo -e "\\nGet crawling history:"
auth_request -X GET "$BASE_URL/api/v1/crawling/history?page=1&page_size=10" | jq '.'

echo -e "\\n${YELLOW}4. Posts and Data${NC}"
echo "=================="

echo "Search posts:"
auth_request -X GET "$BASE_URL/api/v1/posts?keyword_ids=1&page=1&page_size=20" | jq '.'

echo -e "\\nGet post by ID:"
auth_request -X GET "$BASE_URL/api/v1/posts/1" | jq '.'

echo -e "\\nGet trending posts:"
auth_request -X GET "$BASE_URL/api/v1/posts/trending?limit=10&time_period=24h" | jq '.'

echo -e "\\n${YELLOW}5. Trend Analysis${NC}"
echo "=================="

echo "Get trend analysis:"
auth_request -X GET "$BASE_URL/api/v1/trends?keyword_ids=1,2&time_period=7d" | jq '.'

echo -e "\\n${YELLOW}6. Content Generation${NC}"
echo "======================"

echo "Generate content:"
CONTENT_RESULT=$(auth_request -X POST "$BASE_URL/api/v1/content/generate" \\
  -d '{"content_type": "blog_post", "keyword_ids": [1], "template_id": 1}')
echo "$CONTENT_RESULT" | jq '.'

echo -e "\\nGet generated content:"
auth_request -X GET "$BASE_URL/api/v1/content?limit=10" | jq '.'

echo -e "\\nGet content by ID:"
auth_request -X GET "$BASE_URL/api/v1/content/1" | jq '.'

echo -e "\\n${YELLOW}7. System Monitoring${NC}"
echo "===================="

echo "Health check:"
curl -s -X GET "$BASE_URL/health" | jq '.'

echo -e "\\nDetailed health check:"
curl -s -X GET "$BASE_URL/health/detailed" | jq '.'

echo -e "\\nAPI version info:"
curl -s -X GET "$BASE_URL/api/version" | jq '.'

echo -e "\\nPrometheus metrics:"
curl -s -X GET "$BASE_URL/metrics"

echo -e "\\n${GREEN}Examples completed!${NC}"
echo "====================="
echo "Make sure to:"
echo "1. Replace BASE_URL with your actual API URL"
echo "2. Set ACCESS_TOKEN and REFRESH_TOKEN with real values"
echo "3. Install jq for JSON formatting: brew install jq (macOS) or apt-get install jq (Ubuntu)"
