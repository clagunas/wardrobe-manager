from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import datetime

ALLOWED_CATEGORIES = [
    "Top",
    "Pants",
    "Outerwear",
    "Shoes",
    "Accessories",
    "Dresses",
    "Bags"
]

ALLOWED_SEASONS = [
    "Spring/Fall",
    "Summer",
    "Winter",
    "All-year"
]

# should not matter if capital letters !! tbd 
class ClothingItemBase(BaseModel):
    name: str = Field(
        ..., description="Name of the clothing item", example="Blue Jeans"
    )
    category: Literal["Top",
                      "Pants",
                      "Outerwear",
                      "Shoes",
                      "Accessories",
                      "Dresses",
                      "Bags"] = Field(..., description="Category (e.g., pants, shirt, shoes)", example="Pants"
    )
    style: List[str] = Field(
        default_factory=list,
        description="Style tags",
        example=["long sleeve", "sport"],
    )
    colors: List[str] = Field(
        default_factory=list,
        description="List of colors",
        example=["blue", "black"],
    )
    second_hand: Optional[bool] = Field(None, description="Whether the item is second-hand", example=True)
    brand: Optional[str] = Field(None, description="Brand name", example="Levi's")
    season: Optional[Literal["Spring/Fall",
                             "Summer",
                             "Winter",
                             "All-year"]] = Field(None, description="Season", example="Summer")
    price: Optional[float] = Field(None, description="Price in euros", example=79.99)
    date_added: Optional[datetime] = Field(None, description="Date when the item was added", example="2023-08-31")
    place: Optional[str] = Field(None, description="Place of purchase", example="Albacete")
    comment: Optional[str] = Field(None, description="Additional comments", example="Bought on sale")
    image_filename: Optional[str] = Field(
        None,
        description="Filename of the item's image",
        example="jeans.jpg",
    )


class ClothingItem(ClothingItemBase):
    id: str = Field(..., description="Unique identifier")


class ClothingItemFilter(BaseModel):
    category: Optional[List[Literal["Top",
                      "Pants",
                      "Outerwear",
                      "Shoes",
                      "Accessories",
                      "Dresses",
                      "Bags"]]] = Field(
        None, description="Filter by category", examples=[["Top", "Pants"]]
    )
    season: Optional[List[Literal["Spring/Fall",
                             "Summer",
                             "Winter",
                             "All-year"]]] = Field(None, description="Filter by season", examples=[["Summer"]])
    color: Optional[List[str]] = Field(None, description="Filter by color", examples=[["Blue", "Black"]])
    brand: Optional[List[str]] = Field(None, description="Filter by brand", examples=[["Levi's"]])
    second_hand: Optional[List[bool]] = Field(None, description="Filter by second-hand status", examples=[[True]])

# Model for updating an existing item (all optional)
class ClothingItemUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the clothing item", example="Blue Jeans")
    category: Optional[List[Literal["Top",
                      "Pants",
                      "Outerwear",
                      "Shoes",
                      "Accessories",
                      "Dresses",
                      "Bags"]]] = Field(None, description="Category (e.g., pants, shirt, shoes)", example="Pants")
    brand: Optional[str] = Field(None, description="Brand name", example="Levi's")
    color: Optional[List[str]] = Field(None, description="List of colors", example=["blue", "black"])
    second_hand: Optional[bool] = Field(None, description="Whether the item is second-hand", example=True)
    season: Optional[List[Literal["Spring/Fall",
                             "Summer",
                             "Winter",
                             "All-year"]]] = Field(None, description="Season", example="Summer")
    price: Optional[float] = Field(None, description="Price in euros", example=79.99)
    date_added: Optional[datetime] = Field(None, description="Date when the item was added", example="2023-08-31")
    place: Optional[str] = Field(None, description="Place of purchase", example="Albacete")
    comment: Optional[str] = Field(None, description="Additional comments", example="Bought on sale")
    image_filename: Optional[str] = Field(
        None,
        description="Filename of the item's image",
        example="jeans.jpg",
    )