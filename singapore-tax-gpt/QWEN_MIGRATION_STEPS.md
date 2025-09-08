# Step-by-Step Migration from OpenAI to Qwen

## Step 1: Get Alibaba Cloud API Key (5 minutes)

### Option A: International Account
1. Go to https://www.alibabacloud.com/
2. Click "Free Account" 
3. Sign up with email
4. Verify your email
5. Go to https://dashscope.console.aliyun.com/
6. Create API Key and copy it

### Option B: Chinese Account (if you have Alipay)
1. Go to https://dashscope.aliyun.com/
2. Login with Alipay
3. Click "API-KEY管理" 
4. Create new API key

## Step 2: Install Required Package

```bash
cd /Users/ryanyin/LionTax-AI/singapore-tax-gpt
pip install dashscope langchain-community
```

## Step 3: Update .env File

```bash
# Add this line to your .env file
echo "DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx" >> .env
```

## Step 4: Create Qwen Test File

Create `test_qwen.py` to verify it works:

```python
#!/usr/bin/env python
"""Test Qwen API connection."""

import os
from dotenv import load_dotenv
import dashscope

load_dotenv()

# Test basic Qwen API
dashscope.api_key = os.environ.get("DASHSCOPE_API_KEY")

from dashscope import Generation

# Test English
response = Generation.call(
    model='qwen-turbo',
    prompt='What is the GST rate in Singapore?'
)
print("English Test:", response.output.text)

# Test Chinese
response = Generation.call(
    model='qwen-turbo', 
    prompt='新加坡的GST税率是多少？'
)
print("Chinese Test:", response.output.text)
```

## Step 5: Update qa_working.py

Replace the OpenAI initialization with Qwen:

```python
# OLD CODE (around line 94):
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(temperature=0, model="gpt-4-turbo-preview")

# NEW CODE:
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    temperature=0,
    openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
    openai_api_key=os.environ.get("DASHSCOPE_API_KEY"),
    model_name="qwen-turbo"
)
```

## Step 6: Update Embeddings (Optional - Keep OpenAI for now)

For now, keep using OpenAI embeddings since they work well:
```python
# Keep this unchanged for now:
embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get("OPENAI_API_KEY"))
```

Later you can switch to Qwen embeddings if needed.

## Step 7: Test the System

```bash
# Test with English
python -c "from qa_working import answer_question; print(answer_question('What is GST rate?')[0])"

# Test with Chinese
python -c "from qa_working import answer_question; print(answer_question('新加坡的个人所得税率是多少？')[0])"
```

## Step 8: Update Prompts for Bilingual Support

In `qa_working.py`, update the prompt to handle both languages:

```python
# Around line 889, update the prompt:
prompt = f"""You are a Singapore tax expert. Answer in the same language as the question.
如果问题是中文，请用中文回答。If question is in English, answer in English.

Document Excerpts Searched:
{context[:5000]}

User Question: {question}{supplemental_info}

INSTRUCTIONS:
1. Answer in the SAME LANGUAGE as the question
2. Provide a direct, clear answer
3. Use information from documents and supplemental info
4. Include 3-5 bullet points with details
5. Be concise but comprehensive
6. Do NOT use markdown formatting

Answer:"""
```

## Step 9: Run Full Test Suite

```bash
python test_document_search.py
python test_multi_questions.py
```

## Step 10: Update Streamlit App (Optional)

If you want Chinese UI:

```python
# In app_main.py, add language selector:
language = st.selectbox("Language/语言", ["English", "中文"])

if language == "中文":
    st.title("🇸🇬 新加坡税务助手")
    user_input = st.text_input("请输入您的税务问题：")
else:
    st.title("🇸🇬 Singapore Tax Assistant")
    user_input = st.text_input("Enter your tax question:")
```

## Costs
- Qwen-turbo: ¥0.008/1000 tokens (~$0.0011 USD)
- About 15x cheaper than GPT-4

## If Something Goes Wrong

### Common Issues:

1. **"API key not found"**
   - Make sure DASHSCOPE_API_KEY is in .env
   - Run `source .env` or restart terminal

2. **"Model not found"**
   - Use "qwen-turbo" not "qwen-turbo-preview"

3. **Chinese characters show as ???**
   - Add to top of files: `# -*- coding: utf-8 -*-`

4. **Slow responses**
   - Normal - Qwen-turbo takes 2-3 seconds
   - Consider qwen-turbo-latest for faster responses

## Next Steps After Migration
1. Test with Singapore tax questions in Chinese
2. Consider translating singapore_tax_facts.json to Chinese
3. Add Chinese PDF documents to the database
4. Update UI to be fully bilingual