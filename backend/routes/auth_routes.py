import time
from fastapi import APIRouter
from pydantic import BaseModel

try:
    from ..auth import farmer_signup, farmer_login, consumer_signup, consumer_login
except ImportError:
    from auth import farmer_signup, farmer_login, consumer_signup, consumer_login

router = APIRouter(prefix="/api")

class FarmerSignupRequest(BaseModel):
    name: str
    email: str = ""
    password: str
    mobile: str = ""

class LoginRequest(BaseModel):
    email: str # Serves as identifier (email or mobile)
    password: str

class ConsumerSignupRequest(BaseModel):
    name: str
    email: str = ""
    password: str
    mobile: str = ""
    location: str = ""

@router.post("/farmer/signup")
def api_farmer_signup(req: FarmerSignupRequest):
    result = farmer_signup(req.name, req.email, req.password, req.mobile)
    if "error" in result:
        return {"success": False, "message": result["error"]}
    return {"success": True, "user": result}

@router.post("/farmer/login")
def api_farmer_login(req: LoginRequest):
    start_time = time.time()
    result = farmer_login(req.email, req.password)
    duration = (time.time() - start_time) * 1000
    print(f"[Auth] Farmer login for {req.email} took {duration:.2f}ms")
    
    if "error" in result:
        return {"success": False, "message": result["error"]}
    return {"success": True, **result}

@router.post("/consumer/signup")
def api_consumer_signup(req: ConsumerSignupRequest):
    result = consumer_signup(req.name, req.email, req.password, req.mobile, req.location)
    if "error" in result:
        return {"success": False, "message": result["error"]}
    return {"success": True, "user": result}

@router.post("/consumer/login")
def api_consumer_login(req: LoginRequest):
    start_time = time.time()
    result = consumer_login(req.email, req.password)
    duration = (time.time() - start_time) * 1000
    print(f"[Auth] Consumer login for {req.email} took {duration:.2f}ms")
    
    if "error" in result:
        return {"success": False, "message": result["error"]}
    return {"success": True, **result}
