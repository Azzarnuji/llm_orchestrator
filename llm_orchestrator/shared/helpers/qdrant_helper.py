import os
import uuid
from typing import List
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct,
    PayloadSchemaType,
    VectorParams,
    Distance,
    Filter,
    FieldCondition,
    MatchValue
)

load_dotenv()

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = os.getenv("QDRANT_PORT", 6333)
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)

class QdrantHelper:
    _instance: 'QdrantHelper' = None
    client: QdrantClient

    def __new__(cls):
        """
        Creates and returns a singleton instance of QdrantHelper.

        This method ensures that only one instance of QdrantHelper exists by checking if an instance 
        has already been created. If not, it initializes the instance, sets up a Qdrant client 
        connection using the environment variables QDRANT_HOST, QDRANT_PORT, and QDRANT_API_KEY, 
        and creates a collection named 'llm_orchestrator' with a default vector configuration if 
        it doesn't already exist.

        Returns:
            QdrantHelper: The singleton instance of QdrantHelper.
        """

        if cls._instance is None:
            print(f"Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}")
            cls._instance = super().__new__(cls)
            cls._instance.client = QdrantClient(
                url=f"{QDRANT_HOST}:{QDRANT_PORT}",
                api_key=QDRANT_API_KEY,
            )
            # Buat collection jika belum ada, dengan named vector "default"
            collections = cls._instance.client.get_collections().collections
            if not any(c.name == "llm_orchestrator" for c in collections):
                cls._instance.client.recreate_collection(
                    collection_name="llm_orchestrator",
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
                )
        return cls._instance

    def ensure_indexes(self, collection_name: str, payload_filter: dict):

        """
        Ensures that indexes are created for the specified fields in a Qdrant collection.

        This method checks each key-value pair in the provided payload filter and determines
        the appropriate payload schema type (e.g., KEYWORD, BOOL, INTEGER, FLOAT) based on the
        value's data type. It then attempts to create a payload index for each field in the
        specified collection. If the index already exists, it silently ignores the error and 
        continues with other fields.

        Args:
            collection_name (str): The name of the collection in Qdrant where indexes should be created.
            payload_filter (dict): A dictionary where keys are field names and values are the data 
                                types to be indexed.

        Raises:
            Exception: If an unexpected error occurs while creating an index, it is raised unless
                    it is an "already exists" error, which is ignored.
        """

        for key, value in payload_filter.items():
            if isinstance(value, str):
                schema = PayloadSchemaType.KEYWORD
            elif isinstance(value, bool):
                schema = PayloadSchemaType.BOOL
            elif isinstance(value, int):
                schema = PayloadSchemaType.INTEGER
            elif isinstance(value, float):
                schema = PayloadSchemaType.FLOAT
            else:
                continue

            try:
                self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name=key,
                    field_schema=schema
                )
            except Exception as e:
                # Abaikan error kalau index sudah ada
                if "already exists" not in str(e):
                    raise

    def upsert_with_filter(self, collection_name: str, payload_filter: dict, vector: List[float], payload: dict):
        # Pastikan index sudah dibuat
        """
        Upserts a point in a Qdrant collection based on a filter.

        The method first ensures that the required payload indexes exist in the collection.
        It then creates a Qdrant filter based on the provided payload_filter and searches
        for points in the collection that match the filter. If a point is found, its ID is
        used for the upsert operation. If no point is found, a new UUID is generated and
        used as the point ID.

        The method then upserts a point in the collection with the specified vector and
        payload. The vector is stored under the name "default", which is the default
        vector name in the collection's schema.

        Args:
            collection_name (str): The name of the collection in Qdrant where the upsert should occur.
            payload_filter (dict): A dictionary where keys are field names and values are the values to be filtered.
            vector (List[float]): The vector to be upserted.
            payload (dict): The payload to be upserted.

        Returns:
            str: The ID of the upserted point.
        """
        self.ensure_indexes(collection_name, payload_filter)

        # Buat filter Qdrant
        qdrant_filter = Filter(
            must=[
                FieldCondition(key=k, match=MatchValue(value=v))
                for k, v in payload_filter.items()
            ]
        )

        # Cari apakah sudah ada point sesuai filter
        found_points, _ = self.client.scroll(
            collection_name=collection_name,
            scroll_filter=qdrant_filter,
            limit=1
        )

        if found_points:
            point_id = found_points[0].id
        else:
            point_id = str(uuid.uuid4())

        # Upsert dengan vector bernama "default" (sesuai schema)
        self.client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            ]
        )

        return point_id
