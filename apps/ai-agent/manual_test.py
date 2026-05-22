"""
manual_test.py

Run this file to manually test the AI Agent module and see the LLM's outputs in action!
Command: python manual_test.py
"""
import json
import time
from agents.user_modeling_agent import simulate_review
from agents.recommendation_agent import get_recommendations

def test_task_a():
    print("\n" + "="*50)
    print("🚀 TESTING TASK A: USER MODELING (SIMULATED REVIEW)")
    print("="*50)
    
    # 1. Define a sample Nigerian User Persona
    user_persona = {
        "user_id": "U12345",
        "purchase_history": ["Infinix Hot 10", "Oraimo Powerbank"],
        "avg_rating_given": 4.2,
        "price_sensitivity": "high",
        "preferred_categories": ["Electronics", "Gadgets"],
        "is_cold_start": False
    }
    
    # 2. Define a product to review
    product = {
        "name": "JBL Flip 6 Waterproof Speaker",
        "category": "Electronics",
        "price": 62000,
        "brand": "JBL",
        "description": "Portable Bluetooth speaker with deep bass and waterproof design."
    }
    
    print(f"User: Budget-conscious buyer who likes Electronics.")
    print(f"Product: {product['name']} (₦{product['price']})")
    print("Generating review via Gemini 1.5 Pro...\n")
    
    start_time = time.time()
    result = simulate_review(user_persona, product)
    elapsed = time.time() - start_time
    
    print(f"✅ Generated in {elapsed:.2f} seconds!")
    print(f"⭐ Predicted Rating: {result.get('predicted_rating')}/5.0")
    print(f"📝 Simulated Review:\n\"{result.get('simulated_review')}\"")
    print(f"🧠 AI Reasoning:\n{result.get('reasoning')}")


def test_task_b():
    print("\n" + "="*50)
    print("🚀 TESTING TASK B: RECOMMENDATION ENGINE (COLD-START)")
    print("="*50)
    
    # 1. Define a brand new user (Cold-Start)
    cold_start_persona = {
        "user_id": "NEW_USER_999",
        "purchase_history": [],
        "price_sensitivity": "medium",
        "preferred_categories": ["Fashion"],
        "is_cold_start": True
    }
    
    context_query = "I want a nice shoe for an owambe party this weekend."
    domain = "Fashion"
    
    print(f"User: Brand new user (Cold-Start)")
    print(f"Query: \"{context_query}\"")
    print("Fetching FAISS context & ranking via Gemini 1.5 Pro...\n")
    
    start_time = time.time()
    result = get_recommendations(cold_start_persona, top_k=3, domain=domain, context_query=context_query)
    elapsed = time.time() - start_time
    
    print(f"✅ Generated in {elapsed:.2f} seconds!")
    print(f"❄️ Is Cold Start: {result.get('is_cold_start')}")
    
    print("\n🎯 Top Recommendations:")
    for i, rec in enumerate(result.get('recommendations', [])):
        print(f"  {i+1}. {rec['item_name']} (Score: {rec['score']})")
        print(f"     Reason: {rec['reason']}")


if __name__ == "__main__":
    test_task_a()
    time.sleep(2) # brief pause between API calls
    test_task_b()
    print("\n" + "="*50)
    print("🎉 ALL MANUAL TESTS COMPLETED SUCCESSFULLY!")
    print("="*50 + "\n")
