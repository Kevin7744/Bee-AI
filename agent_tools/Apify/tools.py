# from pydantic import BaseModel, Field
# from langchain.tools import BaseTool
# from langchain.agents import Tool
# from langchain.docstore.document import Document
# from langchain.indexes import VectorstoreIndexCreator
# from langchain_community.document_loaders import ApifyWrapper

# class CrawlWebsiteInput(BaseModel):
#     query: str = Field(description="The URL of the website to crawl.")

# class CrawlWebsiteOutput(BaseModel):
#     index: VectorstoreIndexCreator = Field(description="Vectorstore index created from the crawled website content.")

# class CrawlWebsiteTool(BaseTool):
#     name = "crawl_website_and_index"
#     description = "Tool for crawling a website and creating a vector index."
#     args_schema = CrawlWebsiteInput
#     result_schema = CrawlWebsiteOutput

#     def _run(self, inputs): 
#         apify = ApifyWrapper()

#         loader = apify.call_actor(
#             actor_id="apify/website-content-crawler",
#             run_input={"startUrls": [{"url": inputs.query}], "maxCrawlPages": 10, "crawlerType": "cheerio"},
#             dataset_mapping_function=lambda item: Document(
#                 page_content=item["text"] or "", metadata={"source": item["url"]}
#             ),
#         )
#         index = VectorstoreIndexCreator().from_loaders([loader])
#         return {"index": index}