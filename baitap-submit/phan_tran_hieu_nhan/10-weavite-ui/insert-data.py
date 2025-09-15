# Viết code để insert dữ liệu vào Weavite
import weaviate
from weaviate.embedded import EmbeddedOptions
import ssl
import urllib3

# Disable SSL warnings and certificate verification for this demo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

embedded_options = EmbeddedOptions(
    additional_env_vars={
        # Kích hoạt các module cần thiết: text2vec-transformers
        "ENABLE_MODULES": "backup-filesystem,text2vec-transformers",
        "BACKUP_FILESYSTEM_PATH": "/tmp/backups",  # Chỉ định thư mục backup
        "LOG_LEVEL": "panic",  # Chỉ định level log, chỉ log khi có lỗi
        "TRANSFORMERS_INFERENCE_API": "http://localhost:8000",  # API của model embedding
    },
    persistence_data_path="data",  # Lưu trữ dữ liệu vào thư mục data
)

# Khởi tạo Weaviate và kết nối
vector_db_client = weaviate.WeaviateClient(embedded_options=embedded_options)
vector_db_client.connect()
print("DB is ready: {}".format(vector_db_client.is_ready()))

# In ra DB is ready: True

import pandas as pd

from weaviate.classes.config import Configure, Property, DataType, Tokenization

COLLECTION_NAME = "BookCollection"


def create_collection():
    movie_collection = vector_db_client.collections.create(
        name=COLLECTION_NAME,
        vectorizer_config=Configure.Vectorizer.text2vec_transformers(),
        properties=[
            Property(
                name="title",
                data_type=DataType.TEXT,
                vectorize_property_name=True,
                tokenization=Tokenization.LOWERCASE,
            ),
            Property(
                name="author",
                data_type=DataType.TEXT,
                tokenization=Tokenization.WHITESPACE,
            ),
            Property(
                name="description",
                data_type=DataType.TEXT,
                tokenization=Tokenization.WHITESPACE,
            ),
            Property(
                name="genre",
                data_type=DataType.TEXT,
                tokenization=Tokenization.WHITESPACE,
            ),
            Property(name="intro", data_type=DataType.TEXT, skip_vectorization=True),
        ],
    )

    data = pd.read_csv("commonlit_texts.csv")

    sent_to_vector_db = data.to_dict(orient="records")
    total_records = len(sent_to_vector_db)
    print(f"Inserting data to Vector DB: Total records: {total_records}")

    with movie_collection.batch.dynamic() as batch:
        for data_row in sent_to_vector_db:
            print(f"Inserting: {data_row['title']}")
            batch.add_object(properties=data_row)

    print("Data inserted successfully")


if vector_db_client.collections.exists(COLLECTION_NAME):
    print(f"Collection {COLLECTION_NAME} already exists")
else:
    create_collection()

# Nhớ đóng kết nối nha
vector_db_client.close()
