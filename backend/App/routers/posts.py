from fastapi import APIRouter,HTTPException
router=APIRouter(
   
   prefix="/api/snippets/",
   tags=["snippets"],
   responses={404:{"description":"Not Found"}}
)

@router.post("/",response_model=SnipPublic)

def create_snip(snip:SnipCreate,session:SessionDep):
   db_snip=Snip.model_validate(snip)
   session.add(db_snip)
   session.commit()
   session.refresh(db_snip)
   return db_snip


@router.get("",response_model=list[SnipPublic])
def read_heroes(
   session:SessionDep,
   offset:int=0,
   limit:Annotated[int,Query(le=100)]=100,
   ):
   
   snipps=session.exec(
      select(Snip)
      .offset(offset)
      .limit(limit) 
   ).all()
   
   return snipps 

@router.get("/{id}",response_model=SnipPublic)
def  read_hero(
   id:int,
   session:SessionDep
):
   snip=session.get(Snip,id)
   if not snip:
      raise HTTPException(status_code=404,detail="Snip not Found")
   
   return snip


@router.patch("/{id}",response_model=SnipPublic)
def update_snip(id:int,session:SessionDep,snip:SnipUpdate):
   snip_db=session.get(Snip,id)
   if not snip_db:
      raise HTTPException(status_code=404,detail="Snippet not found")
   snip_data=snip.model_dump(exclude_unset=True)
   snip_db.sqlmodel_update(snip_data)
   session.add(snip_db)
   session.commit()
   session.refresh(snip_db)
   return snip_db
   
   
@router.delete("/{id}")
def delete_hero(id:int,session:SessionDep):
   snip=session.get(Snip,id)
   if not snip:
      raise HTTPException(status_code=404,detail="Snippet not found")
   session.delete(snip)
   session.commit()
   
   return {"ok":True}