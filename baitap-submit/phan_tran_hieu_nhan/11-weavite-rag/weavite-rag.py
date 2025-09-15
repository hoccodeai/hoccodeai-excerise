# Áp dụng Weaviate để tạo ra một RAG flow đơn giản, gợi ý sách hay, dựa theo query của người dùng.
# Thay vì hard code query, hãy lấy query từ người dùng input ở console, hoặc tạo app bằng Gradio.

import os
from dotenv import load_dotenv
import weaviate
from weaviate.classes.config import Configure
from weaviate.embedded import EmbeddedOptions

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

embedded_options = EmbeddedOptions(
    additional_env_vars={
        # Kích hoạt các module cần thiết, nhớ thêm generative-openai
        "ENABLE_MODULES": "backup-filesystem,text2vec-transformers,generative-openai",
        "BACKUP_FILESYSTEM_PATH": "/tmp/backups",  # Chỉ định thư mục backup
        "LOG_LEVEL": "panic",
        "TRANSFORMERS_INFERENCE_API": "http://localhost:8000",
        "OPENAI_APIKEY": OPENAI_API_KEY,  # Truyền API Key của OpenAI
    },
    persistence_data_path="data",
)

vector_db_client = weaviate.WeaviateClient(embedded_options=embedded_options)
vector_db_client.connect()
print("DB is ready: {}".format(vector_db_client.is_ready()))


from weaviate.classes.config import Configure, Property, DataType, Tokenization
import pandas as pd

COLLECTION_NAME = "BookCollectionRAG"


def create_collection():
    # Đọc dữ liệu từ file JSON
    data = pd.read_json("movies-2020s.json")

    # Tạo schema cho collection
    movie_collection = vector_db_client.collections.create(
        name=COLLECTION_NAME,
        vector_config=Configure.Vectors.text2vec_transformers(),
        # Sử dụng LLM của OpenAI để generate output
        generative_config=Configure.Generative.openai(
            model="gpt-4o",
            # max_tokens=500,
            # presence_penalty=0,
            # temperature=0.7,
            # top_p=0.7,
        ),
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

    # Chuyển đổi dữ liệu để import
    sent_to_vector_db = data.to_dict(orient="records")
    total_records = len(sent_to_vector_db)
    print(f"Inserting data to Vector DB. Total records: {total_records}")

    # Import dữ liệu vào DB theo batch
    with movie_collection.batch.dynamic() as batch:
        for data_row in sent_to_vector_db:
            print(f"Inserting: {data_row['title']}")
            batch.add_object(properties=data_row)

    print("Data saved to Vector DB")


if vector_db_client.collections.exists(COLLECTION_NAME):
    print("Collection {} already exists".format(COLLECTION_NAME))
else:
    create_collection()


def search_book(query):
    books = vector_db_client.collections.get(COLLECTION_NAME)
    # Dùng chung prompt để tạo 1 kết quả duy nhất với grouped_task
    response = books.generate.near_text(
        query=query,
        grouped_task="Viết một bài giới thiệu ngắn gọn các cuốn sách này.",
        limit=3,
    )

    results = []
    for movie in response.objects:
        movie_tuple = (movie.properties["description"], movie.properties["title"])
        results.append(movie_tuple)
    return results


import gradio as gr

with gr.Blocks(title="Tìm kiếm sách với Vector Database") as interface:
    query = gr.Textbox(label="Tìm kiếm sách", placeholder="Tên, tác giả, thể loại,...")
    search = gr.Button(value="Search")
    gallery = gr.Gallery(
        label="Books",
        show_label=False,
        columns=[5],
        rows=[3],
        object_fit="contain",
        height="auto",
    )
    search.click(search_book, inputs=query, outputs=gallery)

interface.queue().launch()
vector_db_client.close()
