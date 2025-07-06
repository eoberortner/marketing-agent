#!/usr/bin/env python3
"""
Performance Comparison: Sequential vs Parallel Processing

This script compares the performance of the original sequential processing
with the new parallel processing approach.
"""

import time
import statistics
from typing import List, Dict
from functions import update_knowledge_base, update_knowledge_base_parallel


def run_performance_test(test_name: str, test_func, *args, **kwargs) -> Dict:
    """
    Run a performance test and return timing results.
    """
    print(f"\n🧪 Running {test_name}...")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        test_func(*args, **kwargs)
        success = True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        success = False
    
    end_time = time.time()
    duration = end_time - start_time
    
    return {
        "test_name": test_name,
        "duration": duration,
        "success": success,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }


def run_multiple_tests(test_func, num_runs: int = 3, *args, **kwargs) -> List[Dict]:
    """
    Run a test function multiple times and return all results.
    """
    results = []
    
    for i in range(num_runs):
        print(f"\n🔄 Run {i+1}/{num_runs}")
        result = run_performance_test(f"Test Run {i+1}", test_func, *args, **kwargs)
        results.append(result)
        
        # Small delay between runs
        if i < num_runs - 1:
            time.sleep(2)
    
    return results


def analyze_results(results: List[Dict]) -> Dict:
    """
    Analyze test results and calculate statistics.
    """
    if not results:
        return {}
    
    durations = [r["duration"] for r in results if r["success"]]
    
    if not durations:
        return {"error": "No successful runs"}
    
    analysis = {
        "test_name": results[0]["test_name"],
        "total_runs": len(results),
        "successful_runs": len(durations),
        "failed_runs": len(results) - len(durations),
        "min_duration": min(durations),
        "max_duration": max(durations),
        "avg_duration": statistics.mean(durations),
        "median_duration": statistics.median(durations),
        "std_deviation": statistics.stdev(durations) if len(durations) > 1 else 0,
        "all_durations": durations
    }
    
    return analysis


def print_analysis(analysis: Dict):
    """
    Print formatted analysis results.
    """
    if "error" in analysis:
        print(f"❌ {analysis['error']}")
        return
    
    print(f"\n📊 Performance Analysis: {analysis['test_name']}")
    print("=" * 50)
    print(f"Total runs: {analysis['total_runs']}")
    print(f"Successful runs: {analysis['successful_runs']}")
    print(f"Failed runs: {analysis['failed_runs']}")
    print(f"Min duration: {analysis['min_duration']:.2f}s")
    print(f"Max duration: {analysis['max_duration']:.2f}s")
    print(f"Average duration: {analysis['avg_duration']:.2f}s")
    print(f"Median duration: {analysis['median_duration']:.2f}s")
    if analysis['std_deviation'] > 0:
        print(f"Standard deviation: {analysis['std_deviation']:.2f}s")


def compare_performance(sequential_results: List[Dict], parallel_results: List[Dict]):
    """
    Compare sequential vs parallel performance.
    """
    seq_analysis = analyze_results(sequential_results)
    par_analysis = analyze_results(parallel_results)
    
    print("\n🏁 PERFORMANCE COMPARISON")
    print("=" * 60)
    
    if "error" in seq_analysis or "error" in par_analysis:
        print("❌ Cannot compare due to test failures")
        return
    
    # Calculate improvement
    improvement = ((seq_analysis['avg_duration'] - par_analysis['avg_duration']) / 
                  seq_analysis['avg_duration']) * 100
    
    print(f"Sequential Average: {seq_analysis['avg_duration']:.2f}s")
    print(f"Parallel Average:   {par_analysis['avg_duration']:.2f}s")
    print(f"Improvement:        {improvement:.1f}%")
    
    if improvement > 0:
        print(f"✅ Parallel processing is {improvement:.1f}% faster")
    else:
        print(f"⚠️ Sequential processing is {abs(improvement):.1f}% faster")
    
    # Additional metrics
    print(f"\n📈 Additional Metrics:")
    print(f"Sequential Min:     {seq_analysis['min_duration']:.2f}s")
    print(f"Parallel Min:       {par_analysis['min_duration']:.2f}s")
    print(f"Sequential Max:     {seq_analysis['max_duration']:.2f}s")
    print(f"Parallel Max:       {par_analysis['max_duration']:.2f}s")


def main():
    """
    Main function to run performance comparison.
    """
    print("🚀 Performance Comparison: Sequential vs Parallel Processing")
    print("=" * 60)
    
    # Configuration
    num_runs = 2  # Reduced for demo purposes
    parallel_config = {
        "max_fetch_workers": 5,
        "max_process_workers": 3,
        "max_storage_workers": 2,
        "use_async_fetch": True
    }
    
    print(f"Configuration:")
    print(f"  - Number of runs per test: {num_runs}")
    print(f"  - Parallel fetch workers: {parallel_config['max_fetch_workers']}")
    print(f"  - Parallel process workers: {parallel_config['max_process_workers']}")
    print(f"  - Parallel storage workers: {parallel_config['max_storage_workers']}")
    print(f"  - Use async fetch: {parallel_config['use_async_fetch']}")
    
    # Run sequential tests
    print("\n🔄 Running sequential tests...")
    sequential_results = run_multiple_tests(
        update_knowledge_base, 
        num_runs=num_runs
    )
    
    # Run parallel tests
    print("\n🔄 Running parallel tests...")
    parallel_results = run_multiple_tests(
        update_knowledge_base_parallel,
        num_runs=num_runs,
        **parallel_config
    )
    
    # Analyze results
    print("\n📊 Analyzing results...")
    seq_analysis = analyze_results(sequential_results)
    par_analysis = analyze_results(parallel_results)
    
    print_analysis(seq_analysis)
    print_analysis(par_analysis)
    
    # Compare performance
    compare_performance(sequential_results, parallel_results)
    
    print("\n✅ Performance comparison completed!")


def quick_test():
    """
    Quick test to verify both functions work.
    """
    print("🧪 Quick Test: Sequential vs Parallel")
    print("=" * 40)
    
    # Test sequential
    print("\n🔄 Testing sequential processing...")
    seq_result = run_performance_test("Sequential", update_knowledge_base)
    
    # Test parallel
    print("\n🔄 Testing parallel processing...")
    par_result = run_performance_test("Parallel", update_knowledge_base_parallel)
    
    # Quick comparison
    if seq_result["success"] and par_result["success"]:
        improvement = ((seq_result["duration"] - par_result["duration"]) / 
                      seq_result["duration"]) * 100
        print(f"\n📊 Quick Comparison:")
        print(f"Sequential: {seq_result['duration']:.2f}s")
        print(f"Parallel:   {par_result['duration']:.2f}s")
        print(f"Improvement: {improvement:.1f}%")
    else:
        print("\n❌ One or both tests failed")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_test()
    else:
        main() 