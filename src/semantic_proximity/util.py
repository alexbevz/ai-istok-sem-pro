import csv

from typing import Union

from sentence_transformers import SentenceTransformer
from qdrant_client.local.distances import cosine_similarity, euclidean_distance, manhattan_distance

from src.semantic_proximity.config import EmbeddingConfig
from src.semantic_proximity.exception import MissingFileColumnsException

import polars as pl

embedding_config = EmbeddingConfig()

class EmbeddingUtil:

    _model = SentenceTransformer(embedding_config.get_embedding_model())

    @classmethod
    def calculate_embedding(cls, text: Union[str,list[str]]):
        return cls._model.encode(text)
    
class SimilarityUtil:

    @classmethod
    def choose_distance_metric(cls, distance_metric: str):
        if distance_metric == "cosine":
            return cosine_similarity
        elif distance_metric == "euclidean":
            return euclidean_distance
        elif distance_metric == "manhattan":
            return manhattan_distance
        return cosine_similarity

class CollectionUtil:

    @classmethod
    def convert_name_to_qdrant(cls, user_id: int, name: str):
        return f"user_{user_id}_{name}"

class FileUtil:

    @classmethod
    def get_file_handler(cls, file_name: str, separator: str=','):
        file_ext = file_name.split('.')[-1].lower()
        cls._separator = separator
        match file_ext:
            case "csv" | "txt":
                return cls._csv_reader
            case "xls" | "xlsx":
                return cls._excel_reader
            case "json":
                return cls._json_reader
            case "parquet":
                return cls._parquet_reader
            case _:
                return cls._default_reader
    
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
    def _default_reader(cls, file):
        file_content = cls._convert_bytes_to_text(file)
        return [{"content": item,
                "user_content_id": None}
                for item in file_content.split('\n') if item.strip()]
    
    @classmethod
    def _change_columns_to_lowercase(cls, data: pl.DataFrame):
        for column in data.columns:
            data = data.rename({column: column.lower()})
        return data
    
    @classmethod
    def _check_for_required_columns(cls, data: pl.DataFrame):
        required_columns = ["content", "user_content_id"]
        for column in required_columns:
            if column not in data.columns:
                raise MissingFileColumnsException(f"Required column {column} not found in the file")

    @classmethod
    def _convert_bytes_to_text(cls, file):
        return file.read().decode('utf-8')
    