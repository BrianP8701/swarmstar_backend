from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List, Any

from swarmstar.models import SwarmNode

from app.utils.security import validate_token

router = APIRouter()


class SetCurrentNodeRequest(BaseModel):
    node_id: Optional[str] = None


class SetCurrentNodeResponse(BaseModel):
    node_logs: Any = None

@router.put("/tree/set_current_node", response_model=SetCurrentNodeResponse)
async def set_current_node(
    set_current_node_request: SetCurrentNodeRequest,
    user_id: str = Depends(validate_token),
):
    try:
        node_id = set_current_node_request.node_id
        
        node = SwarmNode.get(node_id)
        node_logs = node.developer_logs
        
        return {
            "node_logs": node_logs
        }

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
