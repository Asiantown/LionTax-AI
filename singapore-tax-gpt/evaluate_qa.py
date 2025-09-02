#!/usr/bin/env python
"""Evaluation suite for Singapore Tax Q&A system."""

import json
import sys
import time
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime

# Import both Q&A systems
from qa_working import answer_question as answer_old
from qa_enhanced import EnhancedTaxQA


@dataclass
class TestCase:
    """Test case for Q&A evaluation."""
    question: str
    expected_facts: List[str]
    category: str
    importance: str  # critical, high, medium, low


class QAEvaluator:
    """Evaluate Q&A system performance."""
    
    def __init__(self):
        """Initialize evaluator with test cases."""
        self.test_cases = self._create_test_cases()
        self.enhanced_qa = EnhancedTaxQA()
        
    def _create_test_cases(self) -> List[TestCase]:
        """Create comprehensive test cases."""
        return [
            # Critical: Tax Rates
            TestCase(
                question="What are the current personal income tax rates for Singapore residents?",
                expected_facts=["20,000", "0%", "2%", "3.5%", "7%", "11.5%", "15%", "18%", "19%", "19.5%", "20%", "22%", "320,000"],
                category="Tax Rates",
                importance="critical"
            ),
            TestCase(
                question="What is the tax rate for non-residents?",
                expected_facts=["22%", "flat rate", "non-resident"],
                category="Tax Rates",
                importance="critical"
            ),
            TestCase(
                question="At what income level do I start paying income tax in Singapore?",
                expected_facts=["20,000", "tax-free", "threshold"],
                category="Tax Thresholds",
                importance="critical"
            ),
            TestCase(
                question="What is the highest marginal tax rate for individuals?",
                expected_facts=["22%", "320,000", "highest"],
                category="Tax Rates",
                importance="critical"
            ),
            TestCase(
                question="How is tax calculated for someone earning S$80,000 annually?",
                expected_facts=["3,350", "4.19%", "76,650"],
                category="Tax Calculation",
                importance="critical"
            ),
            
            # Critical: Reliefs
            TestCase(
                question="What personal reliefs am I entitled to as a Singapore resident?",
                expected_facts=["Earned Income", "Spouse", "Child", "Parent", "CPF"],
                category="Tax Reliefs",
                importance="critical"
            ),
            TestCase(
                question="How much can I claim for spouse relief if my spouse has no income?",
                expected_facts=["2,000", "spouse relief"],
                category="Tax Reliefs",
                importance="critical"
            ),
            TestCase(
                question="What is the maximum amount I can claim for child relief?",
                expected_facts=["4,000", "child relief", "qualifying child"],
                category="Tax Reliefs",
                importance="critical"
            ),
            TestCase(
                question="Can I claim tax relief for my parents? What are the conditions?",
                expected_facts=["9,000", "parent relief", "55 years", "4,000"],
                category="Tax Reliefs",
                importance="critical"
            ),
            TestCase(
                question="What is the Earned Income Relief and how is it calculated?",
                expected_facts=["1,000", "1%", "earned income"],
                category="Tax Reliefs",
                importance="critical"
            ),
            
            # High: GST and Other Taxes
            TestCase(
                question="What is the current GST rate in Singapore?",
                expected_facts=["9%", "GST", "2024"],
                category="GST",
                importance="high"
            ),
            TestCase(
                question="What are the stamp duty rates for property purchase?",
                expected_facts=["1%", "2%", "3%", "4%", "5%", "6%", "180,000"],
                category="Stamp Duty",
                importance="high"
            ),
            TestCase(
                question="What is the ABSD rate for Singapore citizens buying their second property?",
                expected_facts=["20%", "second", "ABSD", "citizen"],
                category="Stamp Duty",
                importance="high"
            ),
            
            # Medium: Deadlines and Procedures
            TestCase(
                question="When is the tax filing deadline for individuals?",
                expected_facts=["18 April", "15 April", "e-filing", "paper"],
                category="Deadlines",
                importance="medium"
            ),
            TestCase(
                question="How many days must I be in Singapore to be considered a tax resident?",
                expected_facts=["183", "days", "resident"],
                category="Tax Residency",
                importance="medium"
            ),
            
            # Complex Calculations
            TestCase(
                question="Calculate tax for someone earning $150,000 with $10,000 in reliefs",
                expected_facts=["140,000", "tax", "relief"],
                category="Tax Calculation",
                importance="high"
            ),
            TestCase(
                question="What's the effective tax rate for someone earning $250,000?",
                expected_facts=["250,000", "effective", "rate", "%"],
                category="Tax Calculation",
                importance="high"
            ),
        ]
    
    def evaluate_answer(self, answer: str, test_case: TestCase) -> Dict:
        """Evaluate if answer contains expected facts."""
        answer_lower = answer.lower()
        
        # Check for expected facts
        facts_found = []
        facts_missing = []
        
        for fact in test_case.expected_facts:
            fact_lower = fact.lower()
            # Check if fact appears in answer (handle numbers with/without commas)
            fact_normalized = fact.replace(",", "")
            if fact_lower in answer_lower or fact_normalized in answer_lower.replace(",", ""):
                facts_found.append(fact)
            else:
                facts_missing.append(fact)
        
        # Calculate score
        if len(test_case.expected_facts) > 0:
            accuracy = len(facts_found) / len(test_case.expected_facts)
        else:
            accuracy = 1.0 if answer else 0.0
        
        # Check answer quality
        has_specific_numbers = any(char.isdigit() for char in answer)
        is_evasive = any(phrase in answer_lower for phrase in [
            "context does not specify",
            "not available",
            "cannot provide",
            "refer to iras",
            "consult the latest"
        ])
        
        return {
            "accuracy": accuracy,
            "facts_found": facts_found,
            "facts_missing": facts_missing,
            "has_numbers": has_specific_numbers,
            "is_evasive": is_evasive,
            "answer_length": len(answer)
        }
    
    def run_evaluation(self, use_enhanced: bool = True) -> Dict:
        """Run full evaluation suite."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "system": "enhanced" if use_enhanced else "original",
            "total_tests": len(self.test_cases),
            "by_category": {},
            "by_importance": {},
            "detailed_results": []
        }
        
        print(f"\nRunning evaluation on {'Enhanced' if use_enhanced else 'Original'} Q&A System")
        print("=" * 60)
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"[{i}/{len(self.test_cases)}] Testing: {test_case.question[:50]}...")
            
            # Get answer
            start_time = time.time()
            
            if use_enhanced:
                answer, sources = self.enhanced_qa.answer_question(test_case.question)
            else:
                answer, sources = answer_old(test_case.question)
            
            response_time = time.time() - start_time
            
            # Evaluate answer
            evaluation = self.evaluate_answer(answer, test_case)
            evaluation["response_time"] = response_time
            evaluation["question"] = test_case.question
            evaluation["category"] = test_case.category
            evaluation["importance"] = test_case.importance
            
            # Store result
            results["detailed_results"].append(evaluation)
            
            # Update category stats
            if test_case.category not in results["by_category"]:
                results["by_category"][test_case.category] = {
                    "count": 0,
                    "total_accuracy": 0,
                    "evasive_count": 0
                }
            
            cat_stats = results["by_category"][test_case.category]
            cat_stats["count"] += 1
            cat_stats["total_accuracy"] += evaluation["accuracy"]
            if evaluation["is_evasive"]:
                cat_stats["evasive_count"] += 1
            
            # Update importance stats
            if test_case.importance not in results["by_importance"]:
                results["by_importance"][test_case.importance] = {
                    "count": 0,
                    "total_accuracy": 0,
                    "perfect_answers": 0
                }
            
            imp_stats = results["by_importance"][test_case.importance]
            imp_stats["count"] += 1
            imp_stats["total_accuracy"] += evaluation["accuracy"]
            if evaluation["accuracy"] == 1.0:
                imp_stats["perfect_answers"] += 1
            
            # Print result
            status = "✅" if evaluation["accuracy"] >= 0.8 else "⚠️" if evaluation["accuracy"] >= 0.5 else "❌"
            print(f"  {status} Accuracy: {evaluation['accuracy']:.1%} | "
                  f"Time: {response_time:.2f}s | "
                  f"Evasive: {'Yes' if evaluation['is_evasive'] else 'No'}")
            
            if evaluation["facts_missing"]:
                print(f"     Missing facts: {', '.join(evaluation['facts_missing'][:3])}")
        
        # Calculate summary statistics
        all_accuracies = [r["accuracy"] for r in results["detailed_results"]]
        critical_accuracies = [r["accuracy"] for r in results["detailed_results"] 
                               if r["importance"] == "critical"]
        
        results["summary"] = {
            "overall_accuracy": sum(all_accuracies) / len(all_accuracies) if all_accuracies else 0,
            "critical_accuracy": sum(critical_accuracies) / len(critical_accuracies) if critical_accuracies else 0,
            "total_evasive": sum(1 for r in results["detailed_results"] if r["is_evasive"]),
            "avg_response_time": sum(r["response_time"] for r in results["detailed_results"]) / len(results["detailed_results"]),
            "perfect_answers": sum(1 for r in results["detailed_results"] if r["accuracy"] == 1.0)
        }
        
        # Calculate category averages
        for cat, stats in results["by_category"].items():
            stats["avg_accuracy"] = stats["total_accuracy"] / stats["count"] if stats["count"] > 0 else 0
            stats["evasive_rate"] = stats["evasive_count"] / stats["count"] if stats["count"] > 0 else 0
        
        # Calculate importance averages
        for imp, stats in results["by_importance"].items():
            stats["avg_accuracy"] = stats["total_accuracy"] / stats["count"] if stats["count"] > 0 else 0
            stats["perfect_rate"] = stats["perfect_answers"] / stats["count"] if stats["count"] > 0 else 0
        
        return results
    
    def print_summary(self, results: Dict):
        """Print evaluation summary."""
        print("\n" + "=" * 60)
        print(f"EVALUATION SUMMARY - {results['system'].upper()} SYSTEM")
        print("=" * 60)
        
        summary = results["summary"]
        print(f"\n📊 Overall Performance:")
        print(f"  - Overall Accuracy: {summary['overall_accuracy']:.1%}")
        print(f"  - Critical Questions Accuracy: {summary['critical_accuracy']:.1%}")
        print(f"  - Perfect Answers: {summary['perfect_answers']}/{results['total_tests']}")
        print(f"  - Evasive Responses: {summary['total_evasive']}/{results['total_tests']}")
        print(f"  - Avg Response Time: {summary['avg_response_time']:.2f}s")
        
        print(f"\n📈 By Category:")
        for cat, stats in results["by_category"].items():
            print(f"  {cat}:")
            print(f"    - Accuracy: {stats['avg_accuracy']:.1%}")
            print(f"    - Evasive Rate: {stats['evasive_rate']:.1%}")
        
        print(f"\n🎯 By Importance:")
        for imp, stats in results["by_importance"].items():
            print(f"  {imp.capitalize()}:")
            print(f"    - Accuracy: {stats['avg_accuracy']:.1%}")
            print(f"    - Perfect Rate: {stats['perfect_rate']:.1%}")
    
    def compare_systems(self):
        """Compare original vs enhanced system."""
        print("\n🔬 COMPARING Q&A SYSTEMS")
        print("=" * 60)
        
        # Test original system
        print("\n1. Testing Original System...")
        original_results = self.run_evaluation(use_enhanced=False)
        self.print_summary(original_results)
        
        # Test enhanced system
        print("\n2. Testing Enhanced System...")
        enhanced_results = self.run_evaluation(use_enhanced=True)
        self.print_summary(enhanced_results)
        
        # Compare results
        print("\n" + "=" * 60)
        print("📊 COMPARISON")
        print("=" * 60)
        
        orig_summary = original_results["summary"]
        enh_summary = enhanced_results["summary"]
        
        accuracy_improvement = enh_summary["overall_accuracy"] - orig_summary["overall_accuracy"]
        critical_improvement = enh_summary["critical_accuracy"] - orig_summary["critical_accuracy"]
        evasive_reduction = orig_summary["total_evasive"] - enh_summary["total_evasive"]
        
        print(f"\n✨ Improvements:")
        print(f"  - Overall Accuracy: {orig_summary['overall_accuracy']:.1%} → {enh_summary['overall_accuracy']:.1%} "
              f"({'↑' if accuracy_improvement > 0 else '↓'} {abs(accuracy_improvement):.1%})")
        print(f"  - Critical Accuracy: {orig_summary['critical_accuracy']:.1%} → {enh_summary['critical_accuracy']:.1%} "
              f"({'↑' if critical_improvement > 0 else '↓'} {abs(critical_improvement):.1%})")
        print(f"  - Evasive Responses: {orig_summary['total_evasive']} → {enh_summary['total_evasive']} "
              f"({'↓' if evasive_reduction > 0 else '↑'} {abs(evasive_reduction)})")
        print(f"  - Perfect Answers: {orig_summary['perfect_answers']} → {enh_summary['perfect_answers']} "
              f"({'↑' if enh_summary['perfect_answers'] > orig_summary['perfect_answers'] else '↓'} "
              f"{abs(enh_summary['perfect_answers'] - orig_summary['perfect_answers'])})")
        
        # Save results to JSON
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "original": original_results,
            "enhanced": enhanced_results,
            "improvements": {
                "accuracy": accuracy_improvement,
                "critical_accuracy": critical_improvement,
                "evasive_reduction": evasive_reduction,
                "perfect_answers": enh_summary["perfect_answers"] - orig_summary["perfect_answers"]
            }
        }
        
        with open("evaluation_results.json", "w") as f:
            json.dump(comparison, f, indent=2)
        
        print(f"\n💾 Results saved to evaluation_results.json")
        
        return comparison


def main():
    """Main evaluation function."""
    evaluator = QAEvaluator()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--compare":
        # Compare both systems
        evaluator.compare_systems()
    elif len(sys.argv) > 1 and sys.argv[1] == "--original":
        # Test original system only
        results = evaluator.run_evaluation(use_enhanced=False)
        evaluator.print_summary(results)
    else:
        # Test enhanced system only
        results = evaluator.run_evaluation(use_enhanced=True)
        evaluator.print_summary(results)
        
        # Save results
        with open("evaluation_enhanced.json", "w") as f:
            json.dump(results, f, indent=2)
        print("\n💾 Results saved to evaluation_enhanced.json")


if __name__ == "__main__":
    main()