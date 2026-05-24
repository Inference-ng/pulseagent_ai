from prompts.nigerian_context import get_context_for_persona

TASK_A_BASE_PROMPT = """You are an AI tasked with simulating realistic e-commerce reviews for a specific user persona.

Given the user persona details and a product, you must predict a star rating (1-5) and write a simulated review (3-5 sentences).

{nigerian_context}

Anchor the predicted rating to the user's average rating given (±1 star max deviation for consistent users).
Price sensitivity should influence the rating heavily based on the product's price.
Users with fewer than 3 past purchases are semi-cold-start: widen the allowable rating deviation to ±1.5 stars and reduce confidence by 0.15.

You must provide a reasoning string explaining your decision, and a confidence score between 0.0 and 1.0.
"""

# Keep this for backward compatibility
TASK_A_SYSTEM_PROMPT = TASK_A_BASE_PROMPT.format(nigerian_context="You are a Nigerian e-commerce shopper.")

TASK_A_HUMAN_PROMPT = """User Persona:
User ID: {user_id}
Average Rating Given: {avg_rating_given}
Price Sensitivity: {price_sensitivity}
Preferred Categories: {preferred_categories}
Is Cold Start: {is_cold_start}
Purchase History Context: {history_context}

Product to Review:
Name: {product_name}
Category: {product_category}
Price: {product_price}
Brand: {product_brand}
Description: {product_description}

Provide the simulated review based on these details.
"""