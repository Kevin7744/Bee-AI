from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain.agents import Tool
from langchain.docstore.document import Document
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.document_loaders import ApifyDatasetLoader

class LoadApifyDatasetInput(BaseModel):
    dataset_id: str = Field(description="The ID of the Apify dataset to load.")

class LoadApifyDatasetOutput(BaseModel):
    data: list = Field(description="List of documents loaded from the Apify dataset.")

class LoadApifyDatasetTool(BaseTool):
    name = "load_apify_dataset"
    description = "Tool for loading data from an Apify dataset."
    args_schema = LoadApifyDatasetInput
    result_schema = LoadApifyDatasetOutput

    def _run(self, inputs):
        loader = ApifyDatasetLoader(
            dataset_id=inputs.dataset_id,
            dataset_mapping_function=lambda item: Document(
                page_content=item.get("text", ""), metadata={"source": item.get("url", "")}
            ),
        )
        data = loader.load()
        return {"data": data}
