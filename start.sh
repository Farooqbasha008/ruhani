#!/bin/bash

# RUHANI Startup Script
echo "🚀 Starting RUHANI - Your AI Wellness Companion"

# Check if .env file exists in backend
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Warning: backend/.env file not found!"
    echo "📝 Please copy backend/env.example to backend/.env and configure your API keys"
    echo "🔑 Required API keys:"
    echo "   - GROQ_API_KEY (for LLM & STT)"
    echo "   - ELEVENLABS_API_KEY (for TTS)"
    echo "   - FETCHAI_API_KEY (for public info)"
    echo "   - CORAL_API_KEY (for activity logging)"
    echo "   - Snowflake database credentials"
    echo ""
fi

# Start backend
echo "🔧 Starting backend server..."
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend development server..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ RUHANI is starting up!"
echo "📱 Frontend: http://localhost:5173"
echo "🔌 Backend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user to stop
wait

# Cleanup
echo ""
echo "🛑 Stopping servers..."
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
echo "✅ RUHANI stopped" 