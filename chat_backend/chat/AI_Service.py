import cohere

API_KEY = "HKALTJdnC4pBKNoSSk8FMgrCcl1C04NuE7UKnm2m"
co = cohere.Client(API_KEY)

class CohereService:
    @staticmethod
    async def get_ai_reply(prompt):
        try:
            response = co.chat(  
                model="command-r",
                message=prompt, 
                temperature=0.7
            )
            return response.text.strip()  
        except Exception as e:
            return f"Error: {e}"
