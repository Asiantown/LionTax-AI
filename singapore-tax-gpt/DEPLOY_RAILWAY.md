# Deploy to Railway - Full Singapore Tax GPT

## Quick Deploy Steps:

### 1. Go to Railway
Visit https://railway.app and sign in with GitHub

### 2. Create New Project
- Click "New Project"
- Select "Deploy from GitHub repo"
- Choose: `Asiantown/LionTax-AI`

### 3. Configure Environment Variables
Add these in Railway dashboard:
```
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
ANONYMIZED_TELEMETRY=False
```

### 4. Set Root Directory (Important!)
In Settings > General:
- Root Directory: `/singapore-tax-gpt`

### 5. Deploy
Railway will automatically:
- Install Rust compiler for tiktoken
- Build the ChromaDB database
- Start the Streamlit app

### 6. Generate Domain
In Settings > Networking:
- Click "Generate Domain"
- Your app will be live at the generated URL

## What You Get:
✅ Full Q&A system with 9 Singapore tax documents
✅ Income tax calculator with all reliefs
✅ Property stamp duty calculator (BSD + ABSD)
✅ Professional dark theme UI
✅ Database persistence
✅ Auto-scaling

## Troubleshooting:

### If build fails:
1. Check logs in Railway dashboard
2. Ensure root directory is set to `/singapore-tax-gpt`
3. Verify OPENAI_API_KEY is set

### If app crashes:
1. Check if port binding is correct (Railway sets $PORT automatically)
2. Verify all environment variables are set

## Local Testing:
```bash
cd singapore-tax-gpt
streamlit run app_main.py
```

Visit http://localhost:8501