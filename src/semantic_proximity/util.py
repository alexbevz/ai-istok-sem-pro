import uuid
from typing import Union

from sentence_transformers import SentenceTransformer
from qdrant_client.local.distances import cosine_similarity, euclidean_distance, manhattan_distance

from src.semantic_proximity.config import EmbeddingConfig
from src.semantic_proximity.exception import MissingFileColumnsException

from src.semantic_proximity.repository import (collectionRep,
                                               itemRep)

from src.semantic_proximity.exception import (CollectionDoesNotExistException,
                                              InsuffucientAccessRightsException,
                                              WrongCollectionException,)

import polars as pl

class EmbeddingUtil:

    _model = SentenceTransformer(EmbeddingConfig.get_embedding_model())

    @classmethod
    def calculate_embedding(cls, text: Union[str,list[str]]):
        return cls._model.encode(text)
    
class SimilarityUtil:

    @classmethod
    def choose_distance_metric(cls, distance_metric: str):
        distance_metrics_dict = {
            "cosine": cosine_similarity,
            "euclidean": euclidean_distance,
            "manhattan": manhattan_distance
        }
        return distance_metrics_dict.get(distance_metric, cosine_similarity)

class CollectionUtil:

    @classmethod
    def generate_qdrant_name(cls):
        return str(uuid.uuid4())
    
    @classmethod
    async def get_collection(cls, collection_id: int, db):
        data_collection = await collectionRep.get_by_id(model_id=collection_id,
                                                              session=db)
        if not data_collection:
            raise CollectionDoesNotExistException(f"Collection with id {collection_id} doesn't exist")
        return data_collection

    @classmethod
    async def get_collection_item(cls, collection_id: int, item_id: int, db):
        collection_item = await itemRep.get_by_id(model_id=item_id,
                                                        session=db)
        if not collection_item:
            raise CollectionItemDoesNotExistException(f"Item with id {item_id} doesn't exist in collection {collection_id}")
        if collection_item.data_collection_id != collection_id:
            raise WrongCollectionException(f"Item with id {item_id} doesn't belong to collection {collection_id}")
        return collection_item
        

    @classmethod
    async def check_collection_owner(cls, collection, user):
        if collection.user_id != user.id:
            raise InsuffucientAccessRightsException(f"User {user.id} is not owner of collection {collection.id}")

class FileUtil:

    @classmethod
    def get_file_handler(cls, file_name: str, separator: str=','):
        file_ext = file_name.split('.')[-1].lower()
        cls._separator = separator
        file_handler_dict = {
            "csv": cls._csv_reader,
            "txt": cls._csv_reader,
            "xls": cls._excel_reader,
            "xlsx": cls._excel_reader,
            "json": cls._json_reader,
            "parquet": cls._parquet_reader
        }
        return file_handler_dict.get(file_ext, cls._default_reader)
    
    @classmethod
    def _parquet_reader(cls, file):
        df = pl.read_parquet(file)
        return cls._get_data_from_dataframe(df)

    @classmethod
    def _json_reader(cls, file):
        df = pl.read_json(file)
        return cls._get_data_from_dataframe(df)

    @classmethod
    def _csv_reader(cls, file):
        df = pl.read_csv(file, separator=cls._separator)
        return cls._get_data_from_dataframe(df)
    
    @classmethod
    def _excel_reader(cls, file):
        df = pl.read_excel(file)
        return cls._get_data_from_dataframe(df)

    @classmethod
    def _get_data_from_dataframe(cls, df: pl.DataFrame):
        df = cls._change_columns_to_lowercase(df)
        cls._check_for_required_columns(df)
        df = df.with_columns(df['user_content_id'].cast(pl.String))
        data = df.to_dicts()
        return data
    
    @classmethod
    def get_batches(cls, items: list, batch_size: int = 100) -> list:
        batches = []
        for i in range(0, len(items), batch_size):
            batches.append(items[i:i + batch_size])
        return batches

    @classmethod
    def _default_reader(cls, file):
        """По дефолту просто читает файл по строкам"""
        file_content = cls._convert_bytes_to_text(file)
        lines = file_content.split('\n')
        data = list()
        for line in lines:
            if line.strip():
                data.append({
                    "content": line,
                    "user_content_id": None
                    })
        return data
    
    @classmethod
    def _change_columns_to_lowercase(cls, data: pl.DataFrame):
        for column in data.columns:
            data = data.rename({column: column.lower()})
        return data
    
    @classmethod
    def _check_for_required_columns(cls, data: pl.DataFrame):
        required_columns = {"content", "user_content_id"}
        accepted_columns = set(data.columns)
        missing_columns = required_columns - accepted_columns
        if missing_columns:
            raise MissingFileColumnsException(f"Required columns ({', '.join(missing_columns)}) not found in the file")

    @classmethod
    def _convert_bytes_to_text(cls, file):
        return file.read().decode('utf-8')
    