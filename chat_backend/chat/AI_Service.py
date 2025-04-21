import cohere

API_KEY = "//KEY API CHATBOT CỦA BẠN"
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
