from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Annotated, Literal
from pydantic import BaseModel, Field, computed_field
import json


class Paitent(BaseModel):
    id: Annotated[
        str, Field(..., description="id of the paitent", examples=["P001", "P002"])
    ]
    name: Annotated[str, Field(..., description="name of the paitent")]
    city: Annotated[str, Field(..., description="city where paitent live")]
    age: Annotated[int, Field(..., gt=0, lt=120, description="age of paitent")]
    gender: Annotated[
        Literal["Male", "Female", "others"], Field(..., description="gender of paitent")
    ]
    height: Annotated[float, Field(..., gt=0, description="Height of Paitent")]
    weight: Annotated[float, Field(..., gt=0, description="Weight of paitent")]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight / (self.height**2), 2)
        return bmi

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi <= 24.9:
            return "Normal"
        else:
            return "Overweight"


app = FastAPI()

def getPatientsFrom():
    with open("paitents.json", "r") as f:
        data = json.load(f)
    return data
def savePatientsTo(data):
    with open("paitents.json", "w") as f:
        json.dump(data, f)

@app.post('/create')
def createPaitent(paitent:Paitent):
    # load previous data
    data=getPatientsFrom()
    # check paitent already exists
    if paitent.id in data:
        raise HTTPException(status_code=400, detail="Patient already exists")
    # insert data
    data[paitent.id]=paitent.model_dump(exclude=["id"])
    # save data
    savePatientsTo(data)
    return JSONResponse(status_code=201,content={"message":"paitent created successfully"})

















@app.get("/")
def hello():
    """Home endpoint"""
    data = getPatientsFrom()
    return {"message": data}


@app.get("/about")
def about():
    """About endpoint"""
    return {"message": "its about page"}


@app.get("/specific/{id}")
def get_specific(id: str):
    """Returns dynamic ID"""
    data = getPatientsFrom()
    if id in data:
        return {"message": f"{data[id]}"}
    raise HTTPException(status_code=404, detail="paitent not found")


@app.get("/sort")
def sort_paitents(
    sort_by: str = Query(..., description="sort on the basis of age, city"),
    order: str = Query("asc", description="sort in asc and desc order"),
):  ## triple dots in query function is used to make a variable required
    valid_fields = ["age", "city"]
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"invalid field select {sort_by}")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail=f"invalid field select {order}")
    data = getPatientsFrom()
    sort_order = True if order == "desc" else False
    sortdata = sorted(
        data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order
    )
    return sortdata
