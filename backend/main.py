from fastapi import FastAPI,Request
from fastapi.responses import PlainTextResponse,JSONResponse
from  pydantic import  BaseModel 
from fastapi import HTTPException
from starlette.exceptions import HTTPException as starletteHTTPException 
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder

 
 
 
 
 
class Post(BaseModel):
      title: str 
      language:str 
      description: str |None=None
      likes:int 
      
      
class UnicornException(Exception):
    def __init__(self, name:str):
        self.name=name
        
        
app=FastAPI()

@app.exception_handler(UnicornException)
def unicorn_exception_handler(
    request: Request,
    exc: UnicornException
):
    return JSONResponse(
        status_code=418,
        content={"message":f"Oops!{exc.name} did something.There goes a rainbow... "},
    )
    
    
    

posts = [
    {
        "id": 1,
        "title": "Hello FastAPI",
        "language": "Python",
        "description": "First API",
        "author": "Divas",
        "category": "backend",
        "difficulty": "beginner",
        "likes": 42
    },
    {
        "id": 2,
        "title": "Understanding Python Lists",
        "language": "Python",
        "description": "Learn how lists work in Python",
        "author": "Rahul",
        "category": "python",
        "difficulty": "beginner",
        "likes": 67
    },
    {
        "id": 3,
        "title": "REST API Basics",
        "language": "Python",
        "description": "Introduction to REST APIs",
        "author": "Ananya",
        "category": "backend",
        "difficulty": "beginner",
        "likes": 89
    },
    {
        "id": 4,
        "title": "SQL Joins Explained",
        "language": "SQL",
        "description": "Understanding INNER JOIN and LEFT JOIN",
        "author": "Arjun",
        "category": "database",
        "difficulty": "intermediate",
        "likes": 124
    },
    {
        "id": 5,
        "title": "Machine Learning Pipeline",
        "language": "Python",
        "description": "Building a basic ML pipeline",
        "author": "Priya",
        "category": "machine-learning",
        "difficulty": "intermediate",
        "likes": 156
    },
    {
        "id": 6,
        "title": "React Components",
        "language": "JavaScript",
        "description": "Understanding reusable React components",
        "author": "Karan",
        "category": "frontend",
        "difficulty": "beginner",
        "likes": 73
    },
    {
        "id": 7,
        "title": "FastAPI Path Parameters",
        "language": "Python",
        "description": "Working with dynamic URL paths",
        "author": "Divas",
        "category": "backend",
        "difficulty": "intermediate",
        "likes": 98
    },
    {
        "id": 8,
        "title": "FastAPI Query Parameters",
        "language": "Python",
        "description": "Filtering and searching API data",
        "author": "Divas",
        "category": "backend",
        "difficulty": "intermediate",
        "likes": 115
    },
    {
        "id": 9,
        "title": "Linear Algebra for ML",
        "language": "Python",
        "description": "Vectors and matrices for machine learning",
        "author": "Neha",
        "category": "machine-learning",
        "difficulty": "advanced",
        "likes": 201
    },
    {
        "id": 10,
        "title": "PostgreSQL Basics",
        "language": "SQL",
        "description": "Getting started with PostgreSQL",
        "author": "Vikram",
        "category": "database",
        "difficulty": "beginner",
        "likes": 81
    }
]

@app.get("/unicorns/{name}")
def read_unicorn(name:str):
    if name=="Yolo":
        raise UnicornException(name=name)
    return {"Unicorn name":name}




@app.post("/post/")
def create_post(post: Post):
    post_dict = post.model_dump()

    default_title = "This is Snippets sharing app"
    post_dict.update({"default_title": default_title})

    posts.append(post_dict)

    return post_dict



@app.get("/posts/{id}")
def get_post(id: int):
    for post in posts:
        if post["id"] == id:
            return post

    raise HTTPException(
        status_code=404,
        detail="Item not found"
    )
        
        
        
        
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request,exc:RequestValidationError):
    message="Validation Errors"
    
    for error in exc.errors():
         message += f"\nField: {error['loc']}, Error: {error['msg']}"
    return PlainTextResponse(message, status_code=400)
    


    
class Snippets(BaseModel):
        code:str
        lang:str 
        lines:int 
        
        
@app.post("/snippets")
def create_snippets(snippets:Snippets):
        return snippets
        
    
@app.get("/snippets")
def get_snippets():
    return {"message": "the snippets"}
    
    
            

        
   









