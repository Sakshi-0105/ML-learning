from pydantic import BaseModel,EmailStr,AnyUrl,Field,field_validator # base model is a classs
from typing import List,Dict,Optional,Annotated


## field validator works in two mode before and after

class Paitent(BaseModel):

    name: str
    email:EmailStr
    age:int=Field(gt=0) #age is greater than 0 non negative
    married:Optional[bool]=None ## default value is required for optional values
    weight:Annotated[float,Field(description="weight of person",default=0.0,strict=True)] # stops type convertion of pydantic

    @field_validator('email')
    @classmethod
    def email_validator(cls,value:EmailStr):
        valid_domains=['icici.com','hdfc.com']
        domain= value.split('@')[-1]
        if domain not in valid_domains:
            raise ValueError('domain is not valid')
        return value
    
    @field_validator('name',mode='after') # value after type corecion (type conversion like '23'-> int 23)
    @classmethod
    def name_validator(cls,value:str):
        return value.upper()




def insertPaitent(paitent:Paitent):
    print(f"inserting {paitent.name} into database")

def updatePaitent(paitent:Paitent):
    print(f"updating {paitent.name} into database")

paitent={"name":"sakshi","age":24,"weight":3.4,"email":"abc@icici.com"}
paitent1=Paitent(**paitent)## destructured paitent
insertPaitent(paitent1)
updatePaitent(paitent1)## here we are passing the object of paitent