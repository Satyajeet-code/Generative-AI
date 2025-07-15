from langchain.schema import SystemMessage, HumanMessage
import json
from datetime import datetime

import numpy as np
from sentence_transformers import SentenceTransformer

import torch
from prompts import get_gig_extraction_prompt,llm_filter_prompt

from sklearn.metrics.pairwise import cosine_similarity

from calculate_rule_based_scores import calculate_rule_based

def write_gig_to_db(user_query, conn,cursor,llm):

    current_datetime = datetime.now()
    current_year = current_datetime.year

    prompt=get_gig_extraction_prompt(current_year)
    system_prompt = SystemMessage(content=prompt)

    human_prompt = HumanMessage(content=user_query)

    response = llm.invoke([system_prompt, human_prompt])

    gig_data=json.loads(response.content)

    customer_id = 1

    insert_query = """
        INSERT INTO gigs (
            customer_id,
            title,
            description,
            location,
            start_date,
            end_date,
            max_budget,
            style_preferences,
            category,
            min_budget,
            period
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
    values = (
        customer_id,
        gig_data.get("title"),
        gig_data.get("description"),
        gig_data.get("location"),
        gig_data.get("start_date"),
        gig_data.get("end_date"),
        gig_data.get("max_budget"),
        gig_data.get("style_preferences"),
        gig_data.get("category"),
        gig_data.get("min_budget"),
        gig_data.get("period")
        
    )

    try:
        cursor.execute(insert_query, values)
        conn.commit()
        return gig_data 
        
    except Exception as e:
        conn.rollback()
        print(f"Error writing gig to DB: {e}")
        return None
    


def get_talents(gig_data,cursor):
    category = gig_data["category"]
    cursor.execute("""
        SELECT t.id, t.name as talent_name, t.city, t.experience_years, 
            t.pricing_model, t.min_budget, t.max_budget, t.portfolio_links,
            t.created_at, t.can_travel, t.max_travel_distance_km,
            c.name as category_name
        FROM talent t
        JOIN talent_categories tc ON t.id = tc.talent_id
        JOIN categories c ON tc.category_id = c.id
        WHERE c.name = %s;
    """, (category,))
    results = cursor.fetchall()
    return results


def get_vector_search_result(user_query,cursor,model_name):

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = SentenceTransformer(model_name, device=device)

    query_embedding = model.encode(user_query)

    cursor.execute("SELECT * FROM talent WHERE embedding IS NOT NULL;")
    rows = cursor.fetchall()

    scored_results = []
    talent_list=[]
    for row in rows:
        talent_id = row["id"]
        name = row["name"]
        embedding_str = row["embedding"]
        summary=row["summary"]
        talent_vector = np.array(json.loads(embedding_str)).reshape(1, -1)
        query_embedding = np.array(query_embedding).reshape(1, -1)
       
        similarity = cosine_similarity(query_embedding, talent_vector)[0][0]
        scored_results.append((talent_id, name, summary, similarity))
        
    
    scored_results.sort(key=lambda x: x[2], reverse=True)

    
    for talent_id, name, summary, score in scored_results[:3]:
        print(f"Talent ID: {talent_id}, Name: {name},Similarity Score: {score:.4f}")
        talent_dict={
            "name":name,
            "summary": summary,
            "similarity score with user query":float(score)
        }
        talent_list.append(talent_dict)
    return talent_list


def get_llm_verdict(user_query,llm,talent_list):
    system_prompt = SystemMessage(content=llm_filter_prompt())
    human_prompt = HumanMessage(content=f"""
        Gig Brief:
        {user_query}

        Top 3 Matching Talents:
        {talent_list}
        """)
    response = llm.invoke([system_prompt, human_prompt])
    llm_result_name=response.content.split("|")[0].strip()
    llm_result_reasons=response.content.split("|")[1].strip()
    llm_total_score=response.content.split("|")[3].strip()

    return llm_result_name, llm_result_reasons, llm_total_score
    

def merge_and_format_results(rule_based_results, llm_result_name, llm_result_reasons, llm_total_score):
  
    formatted_results = []
    for talent in rule_based_results:
        paragraph = " ".join(talent['reasons'])  
        formatted_talent = {
            'name': talent['name'],
            'score': talent['total_score'],
            'justification': paragraph
        }
        formatted_results.append(formatted_talent)

  
    llm_entry = {
        'name': llm_result_name,
        'score': llm_total_score,
        'justification': llm_result_reasons
    }
    if len(formatted_results) == 0:
        formatted_results.append(llm_entry)
        
    elif len(formatted_results)< 3 and formatted_results[-1]["name"].lower() != llm_result_name.lower():
     
        formatted_results.append(llm_entry)
    elif len(formatted_results) == 3 and formatted_results[-1]["name"].lower() != llm_result_name.lower():
    
        formatted_results[-1] = llm_entry

    return formatted_results

def get_final_recommendation(user_query, conn,cursor,llm,model_name):

    gig_data =write_gig_to_db(user_query, conn,cursor,llm)

    if gig_data["category"]!=None:
        results=get_talents(gig_data,cursor)

        scored_talent=calculate_rule_based(results, gig_data)

        talent_list=get_vector_search_result(user_query,cursor,model_name)


        llm_result_name, llm_result_reasons, llm_total_score=get_llm_verdict(user_query,llm,talent_list)
        
        final_results =merge_and_format_results(scored_talent, llm_result_name, llm_result_reasons, llm_total_score)

        return final_results
    else:
        return "category not specified"
