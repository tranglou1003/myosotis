#!/bin/bash

# Health check script for deployment verification
# Usage: ./health-check.sh [base_url]

BASE_URL=${1:-"http://localhost"}
API_URL="$BASE_URL:8000"
FRONTEND_URL="$BASE_URL"

echo "🔍 VoiceClone Studio Health Check"
echo "Frontend URL: $FRONTEND_URL"
echo "API URL: $API_URL"
echo ""

# Function to check URL
check_url() {
    local url=$1
    local name=$2
    local timeout=${3:-10}
    
    echo -n "Checking $name... "
    
    if curl -f -s --max-time $timeout "$url" > /dev/null 2>&1; then
        echo "✅ OK"
        return 0
    else
        echo "❌ FAILED"
        return 1
    fi
}

# Function to check API endpoints
check_api() {
    echo "🔍 API Health Checks:"
    
    # Health endpoint
    check_url "$API_URL/health" "Health endpoint"
    
    # Voice options endpoints
    check_url "$API_URL/voice-options/vietnamese" "Vietnamese voices" 15
    check_url "$API_URL/voice-options/english" "English voices" 15
    
    echo ""
}

# Function to check frontend
check_frontend() {
    echo "🔍 Frontend Health Checks:"
    
    # Main page
    check_url "$FRONTEND_URL" "Frontend main page"
    
    # Static assets (if accessible)
    if curl -f -s --max-time 5 "$FRONTEND_URL/static/css/" > /dev/null 2>&1; then
        echo "Static assets... ✅ OK"
    else
        echo "Static assets... ⚠️ Not accessible (may be normal)"
    fi
    
    echo ""
}

# Function to check system resources
check_resources() {
    echo "🔍 System Resource Checks:"
    
    # Docker containers (if running in Docker)
    if command -v docker &> /dev/null; then
        echo "Docker containers:"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep voiceclone || echo "No VoiceClone containers found"
        echo ""
        
        # Container health
        for container in $(docker ps --format "{{.Names}}" | grep voiceclone); do
            health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no-healthcheck")
            echo "$container health: $health"
        done
        echo ""
    fi
    
    # System resources
    echo "System resources:"
    echo "Memory usage: $(free -h | grep Mem | awk '{print $3 "/" $2}')"
    echo "Disk usage: $(df -h . | tail -1 | awk '{print $3 "/" $2 " (" $5 " used)"}')"
    echo ""
}

# Function to run comprehensive test
run_tests() {
    echo "🧪 Running comprehensive tests..."
    
    # Wait for services to be ready
    echo "Waiting for services to start..."
    sleep 5
    
    local failed=0
    
    # Check backend health
    if ! check_url "$API_URL/health" "Backend health" 30; then
        ((failed++))
    fi
    
    # Check frontend
    if ! check_url "$FRONTEND_URL" "Frontend" 30; then
        ((failed++))
    fi
    
    # Test API endpoints
    echo ""
    echo "🔍 Testing API endpoints:"
    
    # Test Vietnamese voices
    if curl -f -s --max-time 15 "$API_URL/voice-options/vietnamese" | grep -q "voice"; then
        echo "Vietnamese voices API... ✅ OK"
    else
        echo "Vietnamese voices API... ❌ FAILED"
        ((failed++))
    fi
    
    # Test English voices  
    if curl -f -s --max-time 15 "$API_URL/voice-options/english" | grep -q "voice"; then
        echo "English voices API... ✅ OK"
    else
        echo "English voices API... ❌ FAILED"
        ((failed++))
    fi
    
    echo ""
    
    if [ $failed -eq 0 ]; then
        echo "🎉 All tests passed! VoiceClone Studio is ready."
        return 0
    else
        echo "❌ $failed test(s) failed. Please check the logs."
        return 1
    fi
}

# Main execution
case "${2:-full}" in
    "api")
        check_api
        ;;
    "frontend") 
        check_frontend
        ;;
    "resources")
        check_resources
        ;;
    "test")
        run_tests
        ;;
    "full"|*)
        check_frontend
        check_api
        check_resources
        echo "🏁 Health check completed."
        ;;
esac
