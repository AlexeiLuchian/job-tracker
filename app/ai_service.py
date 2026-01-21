import ollama
import json
import re

def extract_skills(job_description):
    """
    Extract technical skills from a job description using Ollama AI.

    Args:
        job_description (str): The full job description text

    Returns:
        list: List of skill names (e.g., ['Python', 'SQL', 'Docker'])
    """
    if not job_description or job_description.strip() == '':
        return []
    
    try:
        # Call Ollama API
        response = ollama.chat(
            model='llama3.2',
            messages=[{
                'role': 'user',
                'content': f"""Extract technical skills and requirements from this job description.
Return ONLY a JSON array of skill names (strings), nothing else. No explanation, no markdown, just the JSON array.
Example: ["Python", "SQL", "AWS", "Docker"]

Job Description:
{job_description}"""
            }]
        )

        # Get the response text
        response_text = response['message']['content']

        # Try to extract JSON from response
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            skills = json.loads(json_str)
            return skills
        else:
            print(f"Could not find JSON in response: {response_text}")
            return []

    except Exception as e:
        print(f"Error extracting skills: {e}")
        return []