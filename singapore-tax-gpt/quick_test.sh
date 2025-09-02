#!/bin/bash
# Quick test script for Q&A improvements

echo "🧪 Quick Q&A Test"
echo "================"
echo ""

echo "1. Testing tax rates..."
python qa_working.py "What are the current income tax rates?" 2>/dev/null | head -20
echo ""

echo "2. Testing tax calculation..."
python qa_working.py "Calculate tax for someone earning 80000" 2>/dev/null | head -5
echo ""

echo "3. Testing reliefs..."
python qa_working.py "How much is spouse relief?" 2>/dev/null | head -5
echo ""

echo "4. Testing GST..."
python qa_working.py "What is the GST rate?" 2>/dev/null | head -5
echo ""

echo "✅ If you see specific numbers above (not 'context does not specify'), the fix is working!"