from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field

from planner import allocate_space
from floorplan import generate_floorplan
from layouts import get_layouts
from cost import estimate_cost
from wall_design import recommend_wall_design
from chatbot import handle_chat
from report import generate_report
from material import estimate_materials
from budget_optimizer import optimize_budget
from history import init_db, save_plan, get_history, get_plan, delete_plan
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

os.makedirs("static", exist_ok=True)
init_db()

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WallRequest(BaseModel):
    room_type: str


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Something went wrong while processing your request.",
            "detail": str(exc)
        }
    )

@app.get("/project-info")
def project_info():

    return {
        "project_name": "AI-Powered Architectural Planning and Floor Plan Generation System",
        "version": "1.0",
        "features": [
            "Floor Plan Generation",
            "Layout Recommendations",
            "Cost Estimation",
            "Vastu Suggestions",
            "Wall Design Recommendations"
        ]
    }

@app.post("/wall-design")
def wall_design(data: WallRequest):

    recommendations = recommend_wall_design(
        data.room_type
    )

    return {
        "room_type": data.room_type,
        "recommendations": recommendations
    }

class HouseRequest(BaseModel):
    area: int = Field(..., gt=0, le=20000)
    bedrooms: int = Field(..., gt=0, le=10)
    bathrooms: int = Field(..., gt=0, le=10)
    style: str
    layout_type: str = "A"
    vastu: bool = False
    user_id: str | None = None

class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(data: ChatRequest, request: Request):
    result = handle_chat(data.message, base_url=str(request.base_url))
    return result

@app.get("/")
def root():
    return {
        "message": "AI Architect Running"
    }


@app.get("/layouts")
def layouts():
    return get_layouts()


def _build_plan(data: HouseRequest, request: Request):
    # Room Allocation
    rooms = allocate_space(
        data.area,
        data.bedrooms,
        data.bathrooms
    )

    # Generate Floor Plan
    image_path = generate_floorplan(
        data.area,
        data.bedrooms,
        data.bathrooms,
        rooms
    )

    # Cost Estimation
    cost = estimate_cost(data.area)

    # Material Estimation
    materials = estimate_materials(data.area)

    # Vastu Recommendations
    vastu_rules = {}

    if data.vastu:
        vastu_rules = {
            "entrance": "East",
            "kitchen": "South-East",
            "master_bedroom": "South-West",
            "living_room": "North-East"
        }

    plan = {
        "area": data.area,
        "bedrooms": data.bedrooms,
        "bathrooms": data.bathrooms,
        "style": data.style,
        "layout_type": data.layout_type,

        "available_layouts": get_layouts(),

        "rooms": rooms,

        "cost_estimation": cost,

        "material_estimation": materials,

        "vastu": data.vastu,
        "vastu_rules": vastu_rules,

        "image_url": f"{str(request.base_url).rstrip('/')}/static/floor_plan.png",

        "status": "Plan Generated Successfully"
    }

    return plan, image_path


@app.post("/generate")
def generate_plan(data: HouseRequest, request: Request):
    plan, _ = _build_plan(data, request)

    if data.user_id:
        plan_id = save_plan(data.user_id, plan)
        plan["saved_plan_id"] = plan_id

    return plan


@app.post("/generate-report")
def generate_report_endpoint(data: HouseRequest, request: Request):
    plan, image_path = _build_plan(data, request)

    pdf_path = generate_report(plan, image_path=image_path)

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename="AI_Architect_Floor_Plan_Report.pdf"
    )


class MaterialRequest(BaseModel):
    area: int = Field(..., gt=0, le=20000)


@app.post("/material-estimate")
def material_estimate(data: MaterialRequest):
    return estimate_materials(data.area)


class BudgetRequest(BaseModel):
    budget: int = Field(..., gt=0)
    area: int | None = Field(default=None, gt=0, le=20000)
    bedrooms: int | None = Field(default=None, gt=0, le=10)
    bathrooms: int | None = Field(default=None, gt=0, le=10)


@app.post("/budget-optimizer")
def budget_optimizer(data: BudgetRequest):
    return optimize_budget(
        budget=data.budget,
        area=data.area,
        bedrooms=data.bedrooms,
        bathrooms=data.bathrooms
    )


class SavePlanRequest(BaseModel):
    user_id: str
    title: str | None = None
    plan: dict


@app.post("/save-plan")
def save_plan_endpoint(data: SavePlanRequest):
    plan_id = save_plan(data.user_id, data.plan, title=data.title)
    return {
        "status": "saved",
        "plan_id": plan_id
    }


@app.get("/history/{user_id}")
def history_endpoint(user_id: str):
    return {
        "user_id": user_id,
        "plans": get_history(user_id)
    }


@app.get("/history/{user_id}/{plan_id}")
def history_detail_endpoint(user_id: str, plan_id: int):
    plan = get_plan(plan_id, user_id=user_id)
    if not plan:
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": "Plan not found"}
        )
    return plan


@app.delete("/history/{user_id}/{plan_id}")
def delete_plan_endpoint(user_id: str, plan_id: int):
    deleted = delete_plan(plan_id, user_id)
    if not deleted:
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": "Plan not found or already deleted"}
        )
    return {"status": "deleted", "plan_id": plan_id}