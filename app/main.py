"""
FastAPI application for HealthLabelCheck
FSSAI Food Labelling Regulation API
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
import json
import os

from app.models import RegulationRecord, get_min_font_size
from app.smart_search import SmartSearch
from app.llm import get_llm

# Initialize FastAPI app
app = FastAPI(
    title="HealthLabelCheck API",
    description="FSSAI Food Labelling Regulation Checker API",
    version="1.0.0"
)

# Load records on startup
RECORDS = []
SEARCH_ENGINE = None


def load_records_from_json():
    """Load records from JSON file"""
    global RECORDS, SEARCH_ENGINE
    json_path = 'data/records.json'
    
    if not os.path.exists(json_path):
        print(f"Warning: {json_path} not found, trying to load from sample_records.py")
        try:
            from data.sample_records import SAMPLE_RECORDS
            RECORDS = SAMPLE_RECORDS
        except ImportError:
            print("Error: Could not load records from any source")
            RECORDS = []
        return
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            RECORDS = json.load(f)
        print(f"Loaded {len(RECORDS)} records")
        
        # Initialize smart search engine
        SEARCH_ENGINE = SmartSearch(RECORDS)
        print("Smart search engine initialized")
    except Exception as e:
        print(f"Error loading records: {e}")
        RECORDS = []


# Load records on startup
load_records_from_json()


# Request/Response Models
class QuestionRequest(BaseModel):
    """Request model for questions"""
    question: str = Field(..., min_length=1, max_length=500)
    context: Optional[str] = None


class QuestionResponse(BaseModel):
    """Response model for questions"""
    question: str
    answer: str
    relevant_regulations: List[str]


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=1000)
    include_context: bool = Field(default=True, description="Include relevant regulations as context")


class ChatResponse(BaseModel):
    """Response model for chat endpoint with LLM"""
    answer: str
    confidence: Optional[float] = None
    follow_up: Optional[str] = None
    context_used: Optional[List[str]] = None


class FontSizeRequest(BaseModel):
    """Request for calculating minimum font size"""
    panel_length_cm: float = Field(..., gt=0)
    panel_width_cm: float = Field(..., gt=0)


class FontSizeResponse(BaseModel):
    """Response with font size calculation"""
    panel_area_cm2: float
    min_letter_height_mm: float
    regulation: str = "6.1"


class RegulationResponse(BaseModel):
    """Response model for a single regulation"""
    regulation_no: str
    requirement: str
    applies_to: str
    details: str
    exemption: str
    source_doc: str


# API Endpoints

@app.get("/", tags=["General"])
def root():
    """Root endpoint with API information"""
    return {
        "name": "HealthLabelCheck API",
        "version": "1.0.0",
        "description": "FSSAI Food Labelling Regulation Checker",
        "endpoints": {
            "health": "/health",
            "records": "/records",
            "record_by_id": "/records/{regulation_no}",
            "search": "/search",
            "questions": "/questions",
            "font_size": "/font-size"
        }
    }


@app.get("/health", tags=["General"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "records_loaded": len(RECORDS),
        "service": "HealthLabelCheck API"
    }


@app.get("/records", response_model=List[RegulationResponse], tags=["Regulations"])
def get_records(
    limit: int = Query(default=10, ge=1, le=100, description="Number of records to return")
):
    """Get all regulation records with optional limit"""
    return RECORDS[:limit]


@app.get("/records/{regulation_no}", response_model=RegulationResponse, tags=["Regulations"])
def get_record_by_id(regulation_no: str):
    """Get a specific regulation by its number"""
    for record in RECORDS:
        if record['regulation_no'] == regulation_no:
            return record
    
    raise HTTPException(
        status_code=404,
        detail=f"Regulation {regulation_no} not found"
    )


@app.get("/search", response_model=List[RegulationResponse], tags=["Search"])
def search_regulations(
    q: str = Query(..., min_length=1, description="Search query"),
    use_smart: bool = Query(default=True, description="Use smart TF-IDF search")
):
    """Search regulations by keyword with optional smart ranking"""
    
    if use_smart and SEARCH_ENGINE:
        # Use smart search with TF-IDF ranking
        smart_results = SEARCH_ENGINE.search(q, top_k=10)
        return [result['record'] for result in smart_results]
    
    # Fall back to simple keyword search
    results = []
    query_lower = q.lower()
    
    for record in RECORDS:
        if (query_lower in record['requirement'].lower() or
            query_lower in record['details'].lower() or
            query_lower in record['regulation_no'].lower() or
            query_lower in record['applies_to'].lower()):
            results.append(record)
    
    return results


@app.post("/questions", response_model=QuestionResponse, tags=["Questions"])
def answer_question(question_req: QuestionRequest):
    """
    Answer common questions about FSSAI labelling requirements
    """
    question = question_req.question.lower()
    relevant_regs = []
    answer = ""
    
    # Simple keyword matching for common questions
    if "mandatory" in question or "must" in question or "required" in question:
        mandatory_count = sum(1 for r in RECORDS if 'all packaged foods' in r['applies_to'].lower())
        answer = f"There are {mandatory_count} mandatory declarations required for all packaged foods. "
        answer += "These include: Name of Food, List of Ingredients, Nutritional Information (if applicable), "
        answer += "Allergens, Manufacturer Address, Net Quantity, Dates, FSSAI License, Veg/Non-Veg Symbol, and more."
        relevant_regs = ["5.1", "5.2", "5.3", "5.4", "5.5", "5.6", "5.7", "5.8", "5.10"]
    
    elif "vegetarian" in question or "veg" in question or "symbol" in question:
        answer = "The vegetarian symbol must be a green filled circle inside a square border. "
        answer += "The non-vegetarian symbol must be a brown filled circle inside a square border. "
        answer += "Minimum symbol size: 3mm diameter circle."
        relevant_regs = ["5.10"]
    
    elif "nutrition" in question:
        answer = "Nutritional information is required for all packaged foods with surface area greater than 100 cm². "
        answer += "Must declare: Energy, Protein, Carbohydrate (of which sugars), Fat (of which saturated fat and trans fat), and Sodium "
        answer += "per 100g/100ml and per serve. Some exemptions apply for small packages and certain categories."
        relevant_regs = ["5.3"]
    
    elif "font" in question or "size" in question:
        answer = "Minimum font size depends on the principal display panel area: "
        answer += "<40 cm²: 1.0mm, 40-170 cm²: 1.5mm, 170-650 cm²: 2.0mm, >650 cm²: 3.0mm minimum letter height. "
        answer += "Use the /font-size endpoint to calculate for your specific package."
        relevant_regs = ["6.1"]
    
    elif "fssai" in question and "license" in question:
        answer = "Every packaged food must display the FSSAI License or Registration number. "
        answer += "This must be printed along with the FSSAI logo. The license number is issued by FSSAI after registration."
        relevant_regs = ["5.8"]
    
    elif "ingredient" in question:
        answer = "A complete list of ingredients must be declared in descending order of composition by weight. "
        answer += "Ingredients constituting less than 5% may be listed in any order after other ingredients. "
        answer += "Exemptions: single ingredient foods and fresh fruits/vegetables."
        relevant_regs = ["5.2"]
    
    else:
        answer = "I can help you with questions about FSSAI labelling requirements. Try asking about: "
        answer += "mandatory declarations, vegetarian symbols, nutrition information, font sizes, FSSAI license, or ingredients."
        relevant_regs = []
    
    return QuestionResponse(
        question=question_req.question,
        answer=answer,
        relevant_regulations=relevant_regs
    )


@app.post("/font-size", response_model=FontSizeResponse, tags=["Tools"])
def calculate_font_size(request: FontSizeRequest):
    """
    Calculate minimum font size based on principal display panel dimensions
    """
    area = request.panel_length_cm * request.panel_width_cm
    min_height = get_min_font_size(area)
    
    return FontSizeResponse(
        panel_area_cm2=round(area, 2),
        min_letter_height_mm=min_height
    )


@app.get("/mandatory-checklist", response_model=List[RegulationResponse], tags=["Regulations"])
def get_mandatory_checklist():
    """Get all mandatory requirements for packaged foods"""
    mandatory = []
    for record in RECORDS:
        if 'all packaged foods' in record['applies_to'].lower():
            mandatory.append(record)
    return mandatory


@app.post("/chat", response_model=ChatResponse, tags=["LLM"])
def chat_with_llm(request: ChatRequest):
    """
    Chat with HealthLabelCheck AI assistant
    Uses LLM to provide natural language answers about FSSAI regulations
    """
    try:
        llm = get_llm()
        
        # Optionally add context from relevant regulations
        context = None
        context_regs = []
        
        if request.include_context and SEARCH_ENGINE:
            # Search for relevant regulations
            search_results = SEARCH_ENGINE.search(request.message, top_k=3)
            if search_results:
                context_parts = []
                for result in search_results:
                    reg = result['record']
                    context_parts.append(
                        f"Regulation {reg['regulation_no']}: {reg['requirement']}\n"
                        f"Details: {reg['details']}\n"
                        f"Applies to: {reg['applies_to']}\n"
                        f"Exemption: {reg['exemption']}"
                    )
                    context_regs.append(reg['regulation_no'])
                context = "\n\n".join(context_parts)
        
        # Get LLM response
        response = llm.answer_question(request.message, context=context)
        
        return ChatResponse(
            answer=response.get('answer', ''),
            confidence=response.get('confidence'),
            follow_up=response.get('follow_up'),
            context_used=context_regs if context_regs else None
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LLM error: {str(e)}. Make sure .env file is configured with API keys."
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
