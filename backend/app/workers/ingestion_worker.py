# app/workers/ingestion_worker.py
"""
Skeleton ingestion worker.

Later you can turn this into a Celery/RQ worker or a simple cron job
that scans for PENDING learning_materials and processes them.
"""

import fitz  # PyMuPDF
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.learning_material import LearningMaterial


def extract_text_from_pdf(path: str) -> str:
    doc = fitz.open(path)
    texts: list[str] = []
    for page in doc:
        texts.append(page.get_text())
    return "\n".join(texts)


def simple_chunk(text: str, max_chars: int = 1500) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunks.append(text[start:end])
        start = end
    return chunks


def process_material(material_id: int) -> None:
    db: Session = SessionLocal()
    try:
        material = db.get(LearningMaterial, material_id)
        if not material:
            print(f"Material {material_id} not found")
            return

        print(f"Processing material {material_id}: {material.path}")
        text = extract_text_from_pdf(material.path)
        chunks = simple_chunk(text)

        # TODO: for each chunk:
        #  - generate embedding with your chosen model
        #  - store chunk metadata in DB (content_chunks table)
        #  - index into OpenSearchVectorStore

        material.status = "READY"
        db.add(material)
        db.commit()
        print(f"Material {material_id} marked as READY")
    finally:
        db.close()


if __name__ == "__main__":
    # quick manual test:
    # process_material(1)
    pass
