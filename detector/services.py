import google.generativeai as genai
from decouple import config
import logging

logger = logging.getLogger(__name__)

class TreatmentService:
    @staticmethod
    def get_treatment_plan(disease_name, confidence):
        """
        Generates a treatment plan using Google's Gemini AI.
        """
        api_key = config("GEMINI_API_KEY", default=None)
        
        if not api_key:
            logger.warning("GEMINI_API_KEY is missing. Skipping AI treatment plan.")
            return {
                "status": "warning",
                "message": "AI treatment plan is unavailable because the API key is missing. Please contact the administrator."
            }

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""
            The user has a plant with a detected disease: "{disease_name}" (Confidence: {confidence:.1%}).
            
            Please provide a detailed and practical treatment plan. Structure your response as follows:
            1. **Immediate Actions**: What should the farmer do right now?
            2. **Chemical Control**: Recommended fungicides or pesticides (mention active ingredients).
            3. **Organic/Natural Control**: Non-chemical alternatives.
            4. **Prevention**: How to stop this from happening again.
            
            Keep the advice concise, actionable, and easy to understand for a farmer.
            """
            
            response = model.generate_content(prompt)
            
            if response.text:
                return {
                    "status": "success",
                    "treatment_plan": response.text,
                    "model": "Gemini Pro"
                }
            else:
                return {
                    "status": "error",
                    "message": "AI returned an empty response."
                }
            
        except Exception as e:
            logger.error(f"Error generating treatment plan: {str(e)}")
            return {
                "status": "error",
                "message": "Failed to generate treatment plan due to an internal error."
            }
