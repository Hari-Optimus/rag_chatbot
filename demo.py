import os
import json
 
import requests
from dotenv import load_dotenv
 
from backend.core.config import Config
load_dotenv()
 
 
 
# Setup the Payloads header
headers = {'Content-Type': 'application/json','api-key': Config.AZURE_SEARCH_KEY}
params = {'api-version': Config.AZURE_SEARCH_API_VERSION}
 
# # BLOB_CONTAINER_NAME=Config.BLOB_CONTAINER_NAME
 
# datasource_payload = {
#     "name": Config.DATASOURCE_NAME,
#     "description": "Demo files to demonstrate ai search capabilities.",
#     "type": "sharepoint",
#     "credentials": {
#     "connectionString": "SharePointOnlineEndpoint=https://optimusinfo.sharepoint.com.mcas.ms/sites/IndiaTeam;ApplicationId=1cea657c-c9d0-4b4c-a4a1-a89d3afe2db4;ApplicationSecret=BWB8Q~jYD2m16Cmmb94n3MU.nCJHUFHQKaWUrb60"
#   },
#   "container": {
#     "name": "useQuery",
#     "query": "includeLibrary=https://optimusinfo.sharepoint.com.mcas.ms/sites/IndiaTeam/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2FIndiaTeam%2FShared%20Documents%2FCompany%20Policies&viewid=e1474bba%2D2d3b%2D4546%2D8135%2Dcddcc2b01278"
#   },
# }
# r = requests.put(Config.AZURE_SEARCH_ENDPOINT+ "/datasources/" + Config.DATASOURCE_NAME,
#                  data=json.dumps(datasource_payload), headers=headers, params=params)
# print(r.status_code)
# print(r.ok)
 
 
# Create an index
 
from backend.core.config import Config
 
 
index_payload = {
   
    "name": Config.INDEX_NAME,
    "vectorSearch": {
        "algorithms": [
            {
                "name": "use-hnsw",
                "kind": "hnsw",
            }
        ],
        "compressions": [ 
            {
                "name": "use-scalar",
                "kind": "scalarQuantization",
                "rescoringOptions": {
                    "enableRescoring": "true",
                    "defaultOversampling": 10,
                    "rescoreStorageMethod": "preserveOriginals"
                },
                "scalarQuantizationParameters": {
                    "quantizedDataType": "int8"
                },
                "truncationDimension": 1024
            },
            {
                "name": "use-binary",
                "kind": "binaryQuantization",
                "rescoringOptions": {
                    "enableRescoring": "true",
                    "defaultOversampling": 10,
                    "rescoreStorageMethod": "preserveOriginals"
                },
                "truncationDimension": 1024
            }
        ],
       
        "vectorizers": [
            {
                "name": "use-openai",
                "kind": "azureOpenAI",
                "azureOpenAIParameters": {
                    "resourceUri": Config.AZURE_OPENAI_ENDPOINT,
                    "apiKey": Config.AZURE_OPENAI_API_KEY,
                    "deploymentId": Config.EMBEDDING_DEPLOYMENT_NAME,
                    "modelName": Config.EMBEDDING_DEPLOYMENT_NAME
                }
            }
        ],
        "profiles": [
           {
                "name": "vector-profile-hnsw-scalar",
                "compression": "use-scalar",
                "algorithm": "use-hnsw",
                "vectorizer": "use-openai"
           },
           {
                "name": "vector-profile-hnsw-binary",
                "compression": "use-binary",
                "algorithm": "use-hnsw",
                "vectorizer": "use-openai"
           }
         ]
    },
    "semantic": {
        "configurations": [
            {
                "name": "my-semantic-config",
                "prioritizedFields": {
                    "titleField": {
                        "fieldName": "title"
                    },
                    "prioritizedContentFields": [
                        {
                            "fieldName": "chunk"
                        }
                    ],
                    "prioritizedKeywordsFields": []
                }
            }
        ]
    },
    "fields": [
        {"name": "id", "type": "Edm.String", "key": "true", "analyzer": "keyword", "searchable": "true", "retrievable": "true", "sortable": "false", "filterable": "false","facetable": "false"},
        {"name": "ParentKey", "type": "Edm.String", "searchable": "true", "retrievable": "true", "facetable": "false", "filterable": "true", "sortable": "false"},
        {"name": "title", "type": "Edm.String", "searchable": "true", "retrievable": "true", "facetable": "false", "filterable": "true", "sortable": "false"},
        {"name": "name", "type": "Edm.String", "searchable": "true", "retrievable": "true", "sortable": "false", "filterable": "false", "facetable": "false"},
        {"name": "location", "type": "Edm.String", "searchable": "true", "retrievable": "true", "sortable": "false", "filterable": "false", "facetable": "false"},  
        {"name": "chunk","type": "Edm.String", "searchable": "true", "retrievable": "true", "sortable": "false", "filterable": "false", "facetable": "false"},
        {
            "name": "chunkVector",
            "type": "Collection(Edm.Half)",
            "dimensions": 1536,
            "vectorSearchProfile": "vector-profile-hnsw-scalar",
            "searchable": "true",
            "retrievable": "false",
            "filterable": "false",
            "sortable": "false",
            "facetable": "false",
            "stored": "false" 
        }
    ]
}
 
r = requests.put(Config.AZURE_SEARCH_ENDPOINT + "/indexes/" + Config.INDEX_NAME,
                 data=json.dumps(index_payload), headers=headers, params=params)
print(r.status_code)
print(r.ok)
print(r.text)
 
 
# Create a skillset
skillset_payload = {
    "name": Config.SKILLSET_NAME,
    "description": "e2e Skillset for RAG - Files",
    "skills":
    [
        {
            "@odata.type": "#Microsoft.Skills.Vision.OcrSkill",
            "description": "Extract text (plain and structured) from image.",
            "context": "/document/normalized_images/*",
            "defaultLanguageCode": "en",
            "detectOrientation": True,
            "inputs": [
                {
                  "name": "image",
                  "source": "/document/normalized_images/*"
                }
            ],
                "outputs": [
                {
                  "name": "text",
                  "targetName" : "images_text"
                }
            ]
        },
        {
            "@odata.type": "#Microsoft.Skills.Text.MergeSkill",
            "description": "Create merged_text, which includes all the textual representation of each image inserted at the right location in the content field. This is useful for PDF and other file formats that supported embedded images.",
            "context": "/document",
            "insertPreTag": " ",
            "insertPostTag": " ",
            "inputs": [
                {
                  "name":"text", "source": "/document/content"
                },
                {
                  "name": "itemsToInsert", "source": "/document/normalized_images/*/images_text"
                },
                {
                  "name":"offsets", "source": "/document/normalized_images/*/contentOffset"
                }
            ],
            "outputs": [
                {
                  "name": "mergedText",
                  "targetName" : "merged_text"
                }
            ]
        },
        {
            "@odata.type": "#Microsoft.Skills.Text.SplitSkill",
            "context": "/document",
            "textSplitMode": "pages",  # although it says "pages" it actally means chunks, not actual pages
            "maximumPageLength": 500, # 5000 characters is default and a good choice
            "pageOverlapLength": 70,  # 15% overlap among chunks
            "defaultLanguageCode": "en",
            "inputs": [
                {
                    "name": "text",
                    "source": "/document/merged_text"
                }
            ],
            "outputs": [
                {
                    "name": "textItems",
                    "targetName": "chunks"
                }
            ]
        },
        {
            "@odata.type": "#Microsoft.Skills.Text.AzureOpenAIEmbeddingSkill",
            "description": "Azure OpenAI Embedding Skill",
            "context": "/document/chunks/*",
            "resourceUri": Config.AZURE_OPENAI_ENDPOINT,
            "apiKey": Config.AZURE_OPENAI_API_KEY,
            "deploymentId": Config.EMBEDDING_DEPLOYMENT_NAME,
            "modelName": Config.EMBEDDING_DEPLOYMENT_NAME,
            "inputs": [
                {
                    "name": "text",
                    "source": "/document/chunks/*"
                }
            ],
            "outputs": [
                {
                    "name": "embedding",
                    "targetName": "vector"
                }
            ]
        }
    ],
    "indexProjections": {
        "selectors": [
            {
                "targetIndexName": Config.INDEX_NAME,
                "parentKeyFieldName": "ParentKey",
                "sourceContext": "/document/chunks/*",
                "mappings": [
                    {
                        "name": "title",
                        "source": "/document/title"
                    },
                    {
                        "name": "name",
                        "source": "/document/name"
                    },
                    {
                        "name": "location",
                        "source": "/document/location"
                    },
                    {
                        "name": "chunk",
                        "source": "/document/chunks/*"
                    },
                    {
                        "name": "chunkVector",
                        "source": "/document/chunks/*/vector"
                    }
                ]
            }
        ],
        "parameters": {
            "projectionMode": "skipIndexingParentDocuments"
        },
        # "cognitiveServices": {
        # "@odata.type": "#Microsoft.Azure.Search.CognitiveServicesByKey",
        # "description": Config.COG_SERVICE_NAME,
        # "key": Config.COG_SERVICES_KEY
    # }
    }
}
 

r = requests.put(Config.AZURE_SEARCH_ENDPOINT + "/skillsets/" + Config.SKILLSET_NAME,
                 data=json.dumps(skillset_payload), headers=headers, params=params)
print(r.status_code)
print(r.ok)
 
 
# # Create an indexer
indexer_payload = {
    "name": Config.INDEXER_NAME,
    "dataSourceName": Config.DATASOURCE_NAME,
    "targetIndexName": Config.INDEX_NAME,
    "skillsetName": Config.SKILLSET_NAME,
    

    "schedule" : { "interval" : "PT30M"},
    "fieldMappings": [
        {
          "sourceFieldName" : "metadata_title",
          "targetFieldName" : "title"
        },
        {
          "sourceFieldName" : "metadata_storage_name",
          "targetFieldName" : "name"
        },
        {
          "sourceFieldName" : "metadata_storage_path",
          "targetFieldName" : "location"
        }
    ],
    "outputFieldMappings":[],
    "parameters":
    {
        "maxFailedItems": -1,
        "maxFailedItemsPerBatch": -1,
        "configuration":
        {
            "dataToExtract": "contentAndMetadata",
            "imageAction": "generateNormalizedImages"
        }
    }
}

r = requests.put(Config.AZURE_SEARCH_ENDPOINT + "/indexers/" + Config.INDEXER_NAME,
                 data=json.dumps(indexer_payload), headers=headers, params=params)
print(r)
print(r.status_code)
print(r.ok)


 