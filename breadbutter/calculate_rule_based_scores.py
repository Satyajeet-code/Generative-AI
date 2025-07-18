from get_distance import get_dist

def calculate_location_score(talent,brief):
    score = 0
    reasons = []
    if brief['location']:
        # Location score
        if talent['city'].lower() == brief['location'].lower():
            score += 25
            reasons.append("The Gig's and the talent's locations match exactly")
        elif talent['can_travel']:
            distance = get_dist(talent['city'].lower(), brief['location'].lower())  
            if distance <= talent['max_travel_distance_km']+10:
                score += 20
                reasons.append("The talet can travel to gig's location")
            else:
                score-=10
                reasons.append("The talent can't travel to the gig's location")
        else:
            score -= 10
            reasons.append("The talent doesn't travel")
        return score, reasons
    else:
        return 0,["location not provided"]

def calculate_budget_score(talent, brief):
    score = 0
    reasons = []

    talent_min = talent["min_budget"]
    talent_max = talent["max_budget"]

    gig_min = brief.get("min_budget")
    gig_max = brief.get("max_budget")

    # Normalize gig budget
    if gig_min is None and gig_max is not None:
        gig_min = int(gig_max * 0.7)
        reasons.append(f"Min budget not provided, assumed as 70% of max: ₹{gig_min}.")

    if gig_max is None and gig_min is not None:
        gig_max = talent_max
        reasons.append(f"Max budget not provided, assumed as talent's max: ₹{gig_max}.")

    if gig_min is not None and gig_max is not None:
        if gig_max >= talent_min:
            score += 25
            reasons.append("Talent is within the customer's budget range.")

            if talent_min >= gig_min and talent_max <= gig_max:
                score += 20
                reasons.append("Talent's full budget range fits within customer's range.")
            elif talent_min <= gig_max <= talent_max:
                score += 5
                reasons.append("Talent's minimum fits and upper range is slightly above customer's max.")
        else:
            score -= 10
            reasons.append("Talent's minimum budget is above the customer's maximum budget.")
    else:
        reasons.append("No budget provided by customer; neutral score.")

    return score, reasons

def has_portfolio(talent):
    score=0
    reasons=[]
    if talent["portfolio_links"]:
        score+=10
        reasons.append("Talent has portfolio")
    else:
        score+=5
        reasons.append("Talent doesn't have portfolio")
    return score, reasons

def calculate_rule_based(talents, brief):
    scored_talents = []

    for talent in talents:
        location_score, location_reasons = calculate_location_score(talent, brief)
        budget_score, budget_reasons= calculate_budget_score(talent, brief)
        portfolio_score, portfolio_reasons = has_portfolio(talent)

        total_score = location_score + budget_score + portfolio_score
        reasons = location_reasons + budget_reasons + portfolio_reasons

        scored_talents.append({
            "id": talent["id"],
            "name": talent["talent_name"],
            "total_score": total_score,
            "reasons": reasons
        })

    # Sort by score in descending order
    scored_talents.sort(key=lambda x: x["total_score"], reverse=True)

    # Return top 3
    return scored_talents[:3]
