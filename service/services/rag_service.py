from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
from db.firestore import get_db
from services.embedding_service import generate_embedding

EMBEDDING_COLLECTION = "log_embeddings"

def get_relevant_logs(user_id: str, query: str, limit: int = 3) -> list[dict]:
    db = get_db()

    query_vector = generate_embedding(query)
    collection = db.collection(EMBEDDING_COLLECTION)

    vector_query = collection.where("userId", "==", user_id).find_nearest(
        vector_field="embedding",
        query_vector=Vector(query_vector),
        distance_measure=DistanceMeasure.COSINE,
        limit=limit,
    )
    
    results = vector_query.get()
    return [doc.to_dict() for doc in results]