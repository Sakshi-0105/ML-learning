from pydantic import BaseModel,EmailStr,Field,model_validator # base model is a classs
from typing import List,Dict


## field validator works in two mode before and after

class Paitent(BaseModel):

    name: str
    email:EmailStr
    age:int=Field(gt=0) #age is greater than 0 non negative
    married: bool=None ## default value is required for optional values
    weight: float # stops type convertion of pydantic 
    contact:Dict[str,str]

## model validator validation on group of fields in model
    @model_validator(mode='after')
    def  validate_emergency_contact(cls,model):
        if model.age>60 and 'emergency' not in model.contact:
            raise ValueError("emergency required for olds")
        return model



def insertPaitent(paitent:Paitent):
    print(f"inserting {paitent.name} into database")

def updatePaitent(paitent:Paitent):
    print(f"updating {paitent.name} into database")

paitent={"name":"sakshi","age":61,"weight":3.4,"email":"abc@icici.com" ,"contact":{"phone":"12345"}}
paitent1=Paitent(**paitent)## destructured paitent
insertPaitent(paitent1)
updatePaitent(paitent1)## here we are passing the object of paitent