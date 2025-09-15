# Viết code để tìm kiếm sách/query từ Weavite
import weaviate
from weaviate.embedded import EmbeddedOptions
import ssl
import urllib3

# Disable SSL warnings and certificate verification for this demo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context


# Khởi tạo Weaviate và kết nối
vector_db_client = weaviate.connect_to_local(port=8079, grpc_port=50060)
print("DB is ready: {}".format(vector_db_client.is_ready()))

# In ra DB is ready: True

import pandas as pd

from weaviate.classes.config import Configure, Property, DataType, Tokenization

COLLECTION_NAME = "BookCollection"

book_collection = vector_db_client.collections.get(COLLECTION_NAME)
response = book_collection.query.hybrid(query="Horror", limit=5, alpha=0.5)

# In kết quả
for result in response.objects:
    movie = result.properties
    print(
        "Title: {}, Description: {}, Genre: {}".format(
            movie["title"], movie["description"], movie["genre"]
        )
    )

# Nhớ đóng kết nối nha
vector_db_client.close()
