from fastapi import APIRouter,HTTPException, Query,Depends,status
from typing import Annotated
from datetime import datetime,timezone
from ..auth import get_current_user

from sqlmodel import Session, select

from ..database import SessionDep, get_session

from ..models import User,Snip,SnipCreate,SnipPublic,SnipUpdate


router = APIRouter(
    prefix="/api/snippets",
    tags=["snippets"],
    responses={404: {"description": "Not Found"}},
)

@router.post("/",response_model=SnipPublic,status_code=status.HTTP_201_CREATED)


def create_snip(
   snip_in:SnipCreate,
   current_user:Annotated[User,Depends(get_current_user)],
   session:SessionDep,
   
   ):
   db_snip=Snip(**snip_in.model_dump(),owner_id=current_user.id)
   session.add(db_snip)
   session.commit()
   session.refresh(db_snip)
   return db_snip




@router.get("/",response_model=list[SnipPublic])
def read_snippets(
   session:SessionDep,
   offset:Annotated[int,Query(ge=0)]=0,
   limit:Annotated[int,Query(ge=1,le=100)]=100,
   ):
   
   snipps=session.exec(
      select(Snip)
      .order_by(Snip.id.desc()) # type: ignore
      .offset(offset)
      .limit(limit) 
   ).all()
   
   return snipps 

@router.get("/{id}",response_model=SnipPublic)
def read_snippet(
   id:int,
   session:SessionDep
):
   snip=session.get(Snip,id)
   if not snip:
      raise HTTPException(status_code=404,detail="Snip not Found")
   
   return snip


@router.patch("/{id}",response_model=SnipPublic)
def update_snip(
   id:int,
   snip_in:SnipUpdate,
   current_user:Annotated[User,Depends(get_current_user)],
   session: Session = Depends(get_session),
   
   ):
   
   snip_db=session.get(Snip,id)
   
   if not snip_db:
      raise HTTPException(status_code=404,detail="Snippet not found")
   if snip_db.owner_id!=current_user.id:
      raise HTTPException(
         status_code=403,
         detail="Not Your Snippet"
      )
      
      
   snip_db.sqlmodel_update(snip_in.model_dump(exclude_unset=True))
   snip_db.updated_at=datetime.now(timezone.utc)
   session.add(snip_db)
   session.commit()
   session.refresh(snip_db)
   return snip_db
   
   
   
@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_snippet(
   id:int,
   current_user:Annotated[User,Depends(get_current_user)],
   session:SessionDep):
   
   
   snip=session.get(Snip,id)
   if not snip:
      raise HTTPException(status_code=404,detail="Snippet not found")
   
   if snip.owner_id!=current_user.id:
      raise HTTPException(status_code=403,detail="Not Your Snippet")
   
   session.delete(snip)
   session.commit()
   
   return {"ok":True}


