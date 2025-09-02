from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from qdrantConnection import client
from pydantic import BaseModel
from typing import List
import random
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException
import pandas as pd
from pathlib import Path


router = APIRouter(prefix="/movies", tags=["Movies"])
encoder = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

collection_name = "movies-data"

# schema for movie
class Movie(BaseModel):
    name: str
    director: str
    description: str
    year: int


@router.get("/")
def home():
    return "welcome to app"


# insert single movie
@router.post("/v1/insertMovie")
def qdrantMovieInsert(movie: Movie):
    try:
        movieData = f"{movie.description} {movie.name} {movie.director} {movie.year}"
        movieId = random.randint(1000, 9999)
        client.upsert(
            collection_name="movies-data",
            points=[
                PointStruct(
                    id=movieId,
                    vector=encoder.encode(movieData).tolist(),
                    payload=movie.dict(),
                )
            ],
        )
        return JSONResponse(
            status_code=201,
            content={"id": movieId, "message": "movies inserted successfully"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# get suggentions based on query
@router.post("/v1/getsuggetions")
def qdrantSearchMovies(query: str):
    try:
        hits = client.search(
            collection_name=collection_name,
            query_vector=encoder.encode(query).tolist(),
            limit=3,
        )
        result = []
        for hit in hits:
            result.append({"payload": hit.payload, "score": hit.score, "id": hit.id})

        return JSONResponse(
            status_code=200, content={"message": "sending data", "result": result}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# inserting multiple movies
@router.post("/v1/insertMultipleMovies")
def insertMultipleMovies(movies: List[Movie]):
    try:
        points = []
        for movie in movies:
            movieData = f"{movie.description} {movie.name} {movie.director} {movie.year}"
            movieId = random.randint(1000, 9999)
            point = PointStruct(
                id=movieId,
                vector=encoder.encode(movieData).tolist(),
                payload=movie.dict(),
            )

            points.append(point)

        client.upsert(collection_name="movies-data", points=points)
        return JSONResponse(status_code=200, content="movies inserted at once")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# inserting through csv
@router.post("/v1/insertCSV")
def insertMoviesThroughCsv(path: str):
    try:
        csvPath = Path(__file__).parent / path
        df = pd.read_csv(csvPath)
        points = []
        for _, row in df.iterrows():
            movieId = random.randint(1000, 9999)
            movieData = (
                f"{row['description']} {row['name']} {row['year']} {row['director']}"
            )
            point = PointStruct(
                id=movieId,
                vector=encoder.encode(movieData).tolist(),
                payload=row.to_dict(),
            )
            points.append(point)

        client.upsert(collection_name=collection_name, points=points)
        return JSONResponse(status_code=200, content="movies inserted by csv")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"CSV file {csvPath} not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
