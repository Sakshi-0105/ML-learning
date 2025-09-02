from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    computed_field,
)  # base model is a classs
from typing import List, Dict

## nested model
class Address(BaseModel):
    city: str
    state: str
    pin: str


## field validator works in two mode before and after
class Paitent(BaseModel):

    name: str
    email: EmailStr
    age: int = Field(gt=0)  # age is greater than 0 non negative
    married: bool = None  ## default value is required for optional values
    weight: float  # stops type convertion of pydantic
    height: float
    contact: Dict[str, str]
    address: Address

    ## computed field , creating new field with the help of other field
    @computed_field()
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height**2), 2)



add_dic={"city":"sehore","state":"mp","pin":"4777"}
address1=Address(**add_dic)


paitent = {
    "name": "sakshi",
    "age": 61,
    "weight": 3.4,
    "height": 1,
    "email": "abc@icici.com",
    "contact": {"phone": "12345"},
    "address":address1
}


paitent1 = Paitent(**paitent)  ## destructured paitent
print(paitent1.address)  ## here we are passing the object of paitent
temp=paitent1.model_dump(exclude='age')# similary include 
# paitent1.model_dump(exclude_unset=True) remove the fields which not set during object creation , remove default values
print(paitent1)#pydantic object
print(temp) # python dictornary