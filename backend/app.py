# app.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from typing import Annotated
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
import shutil
import os
import traceback  # For stack trace printing
from tumor_classifier import predict_from_image_path

# Initialize FastAPI app
app = FastAPI()

# SQLite database setup
DATABASE_URL = "sqlite:///./db.sqlite"
Base = declarative_base()

class ImageRecord(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    classification = Column(String)
    feedback = Column(Boolean, default=None)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Directory to store uploaded images
IMAGE_DIR = "images"
Path(IMAGE_DIR).mkdir(parents=True, exist_ok=True)

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint: Classify image and store in SQLite
@app.post("/classify/")
async def classify_image_endpoint(db: Annotated[Session, Depends(get_db)], file: UploadFile = File(...)):
    # First, insert a new record in the database to get the image_id
    image_record = ImageRecord(filename="", classification="")
    db.add(image_record)
    db.commit()
    db.refresh(image_record)  # Now we have the image_id

    image_id = image_record.id

    # Create the final filename using the image_id
    image_filename = f"{image_id}.jpg"  # Save as .jpg or other appropriate extension
    image_path = os.path.join(IMAGE_DIR, image_filename)

    try:
        # Save the uploaded image using image_id as the filename
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Classify the image
        predicted_class = predict_from_image_path(image_path)

        # Update the image record in the database with the actual filename and classification
        image_record.filename = image_filename
        image_record.classification = str(predicted_class)
        db.commit()
        db.refresh(image_record)

    except Exception as e:
        # Print the stack trace for debugging
        traceback.print_exc()

        # Cleanup: if there's an error, delete the file and rollback the transaction
        if os.path.exists(image_path):
            os.remove(image_path)
        db.rollback()

        raise HTTPException(status_code=500, detail=f"Error in classification: {str(e)}")

    finally:
        db.close()

    # Return classification result
    return JSONResponse(content={"filename": image_filename, "classification": predicted_class, "id": image_id})

# Endpoint: Feedback on classification
@app.post("/feedback/{image_id}")
async def feedback_endpoint(image_id: int, feedback: bool, db: Annotated[Session, Depends(get_db)]):
    image_record = db.query(ImageRecord).filter(ImageRecord.id == image_id).first()

    if not image_record:
        raise HTTPException(status_code=404, detail="Image not found")

    # Update feedback
    image_record.feedback = feedback
    db.commit()
    db.refresh(image_record)

    db.close()

    return JSONResponse(content={"message": "Feedback received", "image_id": image_id, "feedback": feedback})
