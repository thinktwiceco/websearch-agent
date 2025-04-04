from pymilvus import MilvusClient


client = MilvusClient("query_db.db")

client.create_collection("query_collection", dimension=1536)