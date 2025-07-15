def get_gig_extraction_prompt(current_year):
    return f"""
You are a helpful assistant that extracts structured gig information from a customer's free-form project request.

Your job is to extract the following fields if and only if they are evident from the customer's request:
- title: Generate a short, human-readable title for the gig
- description: Use the original user query as it is
- location: City or region mentioned in the request
- start_date: Start date in YYYY-MM-DD format, current year is {current_year}; return null if not mentioned in the human message 
- end_date: End date in YYYY-MM-DD current year is {current_year};  return null if not mentioned in the human message 
- period: Duration in days (e.g., "3 days" → 3);  do not calculate leave null if not mentioned explicitly in the human message 
- min_budget: Lower end of the customer's budget; leave null if not mentioned in the human message 
- max_budget: Upper end of the customer's budget (₹75k → 75000); leave null if not mentioned in the human message 
- style_preferences: Comma-separated values like "pastel", "candid", "editorial"
- category: One of: photographer, videographer, photo editor, video editor

Return the output strictly in this JSON format:

{{
  "title": "...",
  "description": "...",
  "location": "...",
  "start_date": "...",
  "end_date": "...",
  "max_budget": ...,
  "style_preferences": "...",
  "category": "...",
  "min_budget": "...",
  "period":"..."
}}

Only return the json. Do not write any other text
"""

def llm_filter_prompt():
    prompt= """
        You are a smart assistant helping match creative talent to client project briefs.

        You are given:
        - A customer's project description (a gig brief)
        - Summaries of the top 3 matched talents

        Your task is to:
        1. Carefully analyze the brief and talent summaries. Stick to the gig brief. Stick to whateevr is mentioned, sometimes the prices and other deatils may not be mentioned. Do not fill in these missing details
        2. You are not concerend about the location. Hence never speak or consider about location.
        3. Recommend only 1 talent out of the 3
        4. Justify your choice across key dimensions:
        - Style & specialization match (candid, pastel, editorial, etc.) = up to 10 points
        - Budget alignment = up to 10 points
        - Experience = up to 10 points
        - Portfolio presence = 10 points
        5. Avoid using superlative words like strongest, best, etc.

        Output format:
        <talent_name> | <your detailed justification> | <addition of all scores> |<final score>

        Only use the information provided in the brief and summaries. Do not make assumptions. Keep the tone professional and informative.

        <example>
        Bidya Kumari | Bidya is the strongest fit for this project due to her experience in pastel-toned visuals, which aligns with the brief's requirements. As a photographer and videographer, she has a cinematic style that suits the project's needs. Her daily rate of ₹5,000 to ₹10,000 falls within the project's budget of ₹30,000 for 3 days, earning her 10 points for budget. Bidya's portfolio showcases her versatility, earning her 10 points. Her experience of 7 years also adds to her credibility, earning her 12 points. |  10+10+10+12 | 42
        <example>
        """
            
    return prompt