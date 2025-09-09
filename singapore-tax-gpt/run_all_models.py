#!/usr/bin/env python
"""Run separate evaluations for each model to compare on Confident AI."""

import os
import subprocess
from dotenv import load_dotenv
load_dotenv()

print("🏆 Running All Model Evaluations")
print("=" * 70)

# Create separate scripts for each model
liontax_script = """
import os
os.environ["CONFIDENT_API_KEY"] = "confident_us_FDfVbEnV7U0mP+ywkdeKj6Uhtic2VeNoVaO7dgqQTLY="
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "sk-dummy")

from deepeval.dataset import EvaluationDataset
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric
from deepeval import evaluate
from qa_lite import answer_question

print("Testing LionTax...")
dataset = EvaluationDataset()
dataset.pull(alias="singapore-tax-iras")

test_cases = []
for golden in dataset.goldens:
    actual_output, _ = answer_question(golden.input)
    test_case = LLMTestCase(input=golden.input, actual_output=actual_output)
    test_cases.append(test_case)

evaluate(test_cases=test_cases, metrics=[AnswerRelevancyMetric()], hyperparameters={"model": "LionTax-Groq-Qwen"})
print("LionTax complete!")
"""

gpt4_script = """
import os
os.environ["CONFIDENT_API_KEY"] = "confident_us_FDfVbEnV7U0mP+ywkdeKj6Uhtic2VeNoVaO7dgqQTLY="
os.environ["OPENAI_API_KEY"] = "{}"

from deepeval.dataset import EvaluationDataset
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric
from deepeval import evaluate
import openai

print("Testing GPT-4...")
dataset = EvaluationDataset()
dataset.pull(alias="singapore-tax-iras")

client = openai.OpenAI()
test_cases = []
for golden in dataset.goldens:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{{"role": "system", "content": "You are a Singapore tax expert."}}, {{"role": "user", "content": golden.input}}],
        temperature=0
    )
    test_case = LLMTestCase(input=golden.input, actual_output=response.choices[0].message.content)
    test_cases.append(test_case)

evaluate(test_cases=test_cases, metrics=[AnswerRelevancyMetric()], hyperparameters={{"model": "GPT-4"}})
print("GPT-4 complete!")
""".format(os.getenv("OPENAI_API_KEY", ""))

claude_script = """
import os
os.environ["CONFIDENT_API_KEY"] = "confident_us_FDfVbEnV7U0mP+ywkdeKj6Uhtic2VeNoVaO7dgqQTLY="
os.environ["ANTHROPIC_API_KEY"] = "{}"

from deepeval.dataset import EvaluationDataset
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric
from deepeval import evaluate
from anthropic import Anthropic

print("Testing Claude-3...")
dataset = EvaluationDataset()
dataset.pull(alias="singapore-tax-iras")

client = Anthropic()
test_cases = []
for golden in dataset.goldens:
    response = client.messages.create(
        model="claude-3-sonnet-20241022",
        max_tokens=500,
        messages=[{{"role": "user", "content": f"You are a Singapore tax expert. Answer: {{golden.input}}"}}]
    )
    test_case = LLMTestCase(input=golden.input, actual_output=response.content[0].text)
    test_cases.append(test_case)

evaluate(test_cases=test_cases, metrics=[AnswerRelevancyMetric()], hyperparameters={{"model": "Claude-3-Sonnet"}})
print("Claude-3 complete!")
""".format(os.getenv("ANTHROPIC_API_KEY", ""))

# Run each model separately
print("\n1️⃣ Running LionTax evaluation...")
with open("temp_liontax.py", "w") as f:
    f.write(liontax_script)
subprocess.run(["python", "temp_liontax.py"])

if os.getenv("OPENAI_API_KEY"):
    print("\n2️⃣ Running GPT-4 evaluation...")
    with open("temp_gpt4.py", "w") as f:
        f.write(gpt4_script)
    subprocess.run(["python", "temp_gpt4.py"])
else:
    print("\n⚠️ Skipping GPT-4 (no API key)")

if os.getenv("ANTHROPIC_API_KEY"):
    print("\n3️⃣ Running Claude-3 evaluation...")
    with open("temp_claude.py", "w") as f:
        f.write(claude_script)
    subprocess.run(["python", "temp_claude.py"])
else:
    print("\n⚠️ Skipping Claude (no API key)")

# Cleanup
for f in ["temp_liontax.py", "temp_gpt4.py", "temp_claude.py"]:
    if os.path.exists(f):
        os.remove(f)

print("\n" + "=" * 70)
print("✅ ALL EVALUATIONS COMPLETE!")
print("=" * 70)
print("\n📊 To compare models on Confident AI:")
print("1. Go to https://app.confident-ai.com")
print("2. Click 'Compare Test Results' in sidebar")
print("3. Select the test runs with different model names")
print("\nYou should see 3 separate test runs with hyperparameters:")
print("  - model: LionTax-Groq-Qwen")
print("  - model: GPT-4")
print("  - model: Claude-3-Sonnet")