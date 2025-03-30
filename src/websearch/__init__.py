class Config:
    chunk_size: int
    chunk_overlap: int
    max_generated_queries: int
    max_generated_links: int


config: Config = {
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "max_generated_queries": 1,
    "max_generated_links": 1,
}
