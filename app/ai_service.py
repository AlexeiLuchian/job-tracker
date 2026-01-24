import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

def extract_skills(job_description):
    """
    Extract technical skills from a job description using Groq API.
    
    Args:
        job_description (str): The full job description text
        
    Returns:
        list: List of skill names (e.g., ["Python", "SQL", "Docker"])
    """
    if not job_description or job_description.strip() == '':
        return []
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"""Extract technical skills and requirements from this job description.
Return ONLY a JSON array of skill names (strings), nothing else. No explanation, no markdown.
Example: ["Python", "SQL", "AWS", "Docker"]

Job Description:
{job_description}"""
            }],
            temperature=0.3,
            max_tokens=500
        )
        
        response_text = response.choices[0].message.content
        
        # Extract JSON array from response
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            skills = json.loads(json_match.group(0))
            return skills
        else:
            print(f"Could not find JSON in response: {response_text}")
            return []
        
    except Exception as e:
        print(f"Error extracting skills: {e}")
        return []