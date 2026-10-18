from fastapi import APIRouter,HTTPException, Query,Depends,status
from fastapi_pagination import Page, add_pagination,paginate
from typing import Annotated
from datetime import datetime,timezone
from ..auth import get_current_user
from sqlmodel import Session, col, or_, select,func
from ..database import SessionDep, get_session
from ..models import User,Snip,SnipCreate,SnipPublic,SnipUpdate,VoteIn,Vote


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
   db_snip=Snip(**snip_in.model_dump(),owner_id=current_user.id) # type: ignore
   session.add(db_snip)
   session.commit()
   session.refresh(db_snip)
   return db_snip




@router.get("/",response_model=Page[SnipPublic])
def read_snippets(
   session:SessionDep,
   offset:Annotated[int,Query(ge=0)]=0,
   limit:Annotated[int,Query(ge=1,le=100)]=100,
   owner_id:int|None=None,
   language:str|None=None,
   q:str|None=None,
   sort:str="new",
   ):
   
   statement=select(Snip)
   
   if owner_id is  not None:
      statement=statement.where(Snip.owner_id==owner_id)
   if language:
      statement=statement.where(Snip.language==language)
   if q:
      statement=statement.where(
         or_(
            col(Snip.title).ilike(f"%{q}%"),
            col(Snip.description).ilike(f"%{q}%")
            )
         )
      
      
   snipps = session.exec(
    statement
    .order_by(
        Snip.vote_count.desc() if sort == "top" else Snip.id.desc(), # type: ignore
        Snip.id.desc(), # type: ignore
    )
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


@router.put("/{id}/vote",response_model=SnipPublic)
def set_vote(
   id:int,
   vote_in:VoteIn,
   current_user:Annotated[User,Depends(get_current_user)],
   session: Session = Depends(get_session),
   ):
   snip_db=session.get(Snip,id)
   
   if not snip_db:
      raise HTTPException(status_code=404,detail="Snippet not found")
   
   
   vote=session.get(Vote,(current_user.id,id))
   
   
   if vote is None:
      vote=Vote(
         user_id=current_user.id, # type: ignore
         snip_id=id,
         value=vote_in.value,
      )
      
      session.add(vote)
      
   else:
      vote.value=vote_in.value
      
      
   total=session.exec(
      select(func.sum(Vote.value))
      .where(Vote.snip_id==id)
   ).one()
   
   snip_db.vote_count=total or 0 
   
   session.add( snip_db)
   session.commit()
   session.refresh( snip_db)
   
   
   return snip_db
   
   
@router.delete("/{id}/vote",response_model=SnipPublic)
def  delete_vote(
   id:int,
   current_user:Annotated[User,Depends(get_current_user)],
   session: Session = Depends(get_session),
):
   
   snippet=session.get(Snip,id)
   
   if snippet is None:
      raise HTTPException(status_code=404,detail="Snippets not found")
   
   
   vote=session.get(Vote,(current_user.id,id))
   
   if vote:
    session.delete(vote)
   
      
   total=session.exec(
      select(func.sum(Vote.value))
      .where(Vote.snip_id==id)
   ).one()
      
   snippet.vote_count=total or 0 
   
   session.add(snippet)
   session.commit()
   session.refresh(snippet)
   
   return snippet



      
      
   

