
from pydantic import BaseModel, ConfigDict, Field


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    idea: str = Field(
        min_length=10,
        max_length=5000,
        description="Business idea to turn into a product blueprint",
    )
    currency: str = Field(
        default="USD",
        pattern=r"^[A-Z]{3}$",
        description="Three-letter uppercase currency code",
    )


class Feature(BaseModel):
    name: str
    description: str
    priority: str


class UserFlow(BaseModel):
    name: str
    steps: list[str]


class TechStack(BaseModel):
    frontend: str
    backend: str
    database: str
    ai: str
    infrastructure: str
    mobile: str


class DevelopmentPhase(BaseModel):
    name: str
    duration: str
    deliverables: list[str]


class BudgetEstimate(BaseModel):
    currency: str
    development_min: int
    development_max: int
    monthly_running_min: int
    monthly_running_max: int
    assumptions: list[str]


class DashboardWidget(BaseModel):
    name: str
    purpose: str
    sample_value: str


class PrototypeSpec(BaseModel):
    page_name: str
    layout_description: str
    widgets: list[DashboardWidget]
    primary_actions: list[str]


class ProductBlueprint(BaseModel):
    product_name: str
    summary: str
    target_users: list[str]
    problem: str
    value_proposition: str
    assumptions: list[str]
    features: list[Feature]
    user_flows: list[UserFlow]
    tech_stack: TechStack
    development_phases: list[DevelopmentPhase]
    budget: BudgetEstimate
    prototype: PrototypeSpec


class AnalyzeResponse(BaseModel):
    project_id: str
    status: str
    blueprint: ProductBlueprint
