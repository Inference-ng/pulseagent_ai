from .nigerian_context import NIGERIAN_SHOPPER_CONTEXT

TASK_A_SYSTEM_PROMPT = f"""You are an AI tasked with simulating realistic e-commerce reviews for a specific user persona.

Given the user persona details and a product, you must predict a star rating (1-5) and write a simulated review (3-5 sentences).

{{nigerian_context}}

Anchor the predicted rating to the user's average rating given (±1 star max deviation for consistent users).
Price sensitivity should influence the rating heavily based on the product's price.

You must provide a reasoning string explaining your decision, and a confidence score between 0.0 and 1.0.
""".format(nigerian_context=NIGERIAN_SHOPPER_CONTEXT)

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
