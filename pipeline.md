{
    "name": "Ecommerce_Pipeline",
    "objectId": "be00a03f-ca2d-48ae-8c70-1cd5fd33ff1a",
    "properties": {
        "activities": [
            {
                "name": "Get Metadata",
                "type": "GetMetadata",
                "dependsOn": [],
                "policy": {
                    "timeout": "0.12:00:00",
                    "retry": 0,
                    "retryIntervalInSeconds": 30,
                    "secureOutput": false,
                    "secureInput": false
                },
                "typeProperties": {
                    "fieldList": [
                        "childItems"
                    ],
                    "datasetSettings": {
                        "annotations": [],
                        "type": "DelimitedText",
                        "typeProperties": {
                            "location": {
                                "type": "AzureBlobFSLocation",
                                "folderPath": "ecommerce_data",
                                "fileSystem": "data"
                            },
                            "columnDelimiter": ",",
                            "escapeChar": "\\",
                            "firstRowAsHeader": true,
                            "quoteChar": "\""
                        },
                        "schema": [],
                        "externalReferences": {
                            "connection": "4a3c905d-9ca7-41ec-a4cf-6580d989f89f"
                        }
                    },
                    "storeSettings": {
                        "type": "AzureBlobFSReadSettings",
                        "recursive": true,
                        "enablePartitionDiscovery": false
                    },
                    "formatSettings": {
                        "type": "DelimitedTextReadSettings"
                    }
                }
            },
            {
                "name": "ForEach",
                "type": "ForEach",
                "dependsOn": [
                    {
                        "activity": "Get Metadata",
                        "dependencyConditions": [
                            "Succeeded"
                        ]
                    }
                ],
                "typeProperties": {
                    "items": {
                        "value": "@activity('Get Metadata').output.childItems",
                        "type": "Expression"
                    },
                    "activities": [
                        {
                            "name": "Copy data",
                            "type": "Copy",
                            "dependsOn": [],
                            "policy": {
                                "timeout": "0.12:00:00",
                                "retry": 0,
                                "retryIntervalInSeconds": 30,
                                "secureOutput": false,
                                "secureInput": false
                            },
                            "typeProperties": {
                                "source": {
                                    "type": "DelimitedTextSource",
                                    "storeSettings": {
                                        "type": "AzureBlobFSReadSettings",
                                        "recursive": false,
                                        "enablePartitionDiscovery": false
                                    },
                                    "formatSettings": {
                                        "type": "DelimitedTextReadSettings"
                                    },
                                    "datasetSettings": {
                                        "annotations": [],
                                        "type": "DelimitedText",
                                        "typeProperties": {
                                            "location": {
                                                "type": "AzureBlobFSLocation",
                                                "fileName": {
                                                    "value": "@{item().name}",
                                                    "type": "Expression"
                                                },
                                                "folderPath": "ecommerce_data",
                                                "fileSystem": "data"
                                            },
                                            "columnDelimiter": ",",
                                            "escapeChar": "\\",
                                            "firstRowAsHeader": true,
                                            "quoteChar": "\""
                                        },
                                        "schema": [],
                                        "externalReferences": {
                                            "connection": "4a3c905d-9ca7-41ec-a4cf-6580d989f89f"
                                        }
                                    }
                                },
                                "sink": {
                                    "type": "ParquetSink",
                                    "storeSettings": {
                                        "type": "AzureBlobStorageWriteSettings"
                                    },
                                    "formatSettings": {
                                        "type": "ParquetWriteSettings",
                                        "enableVertiParquet": true
                                    },
                                    "datasetSettings": {
                                        "annotations": [],
                                        "connectionSettings": {
                                            "name": "Ecommerce_Data",
                                            "properties": {
                                                "annotations": [],
                                                "type": "Lakehouse",
                                                "typeProperties": {
                                                    "workspaceId": "4b342d94-0249-4527-bcaa-5e7a49ec0bb7",
                                                    "artifactId": "41ebc24d-a955-4459-bf47-450d310623b9",
                                                    "rootFolder": "Files"
                                                },
                                                "externalReferences": {
                                                    "connection": "33502b3b-fafd-4967-a4e4-4a831e99abad"
                                                }
                                            }
                                        },
                                        "type": "Parquet",
                                        "typeProperties": {
                                            "location": {
                                                "type": "LakehouseLocation",
                                                "fileName": {
                                                    "value": "@{replace(item().name,'.csv','')}",
                                                    "type": "Expression"
                                                },
                                                "folderPath": "bronze"
                                            },
                                            "compressionCodec": "snappy"
                                        },
                                        "schema": []
                                    }
                                },
                                "enableStaging": false,
                                "enableSkipIncompatibleRow": true,
                                "translator": {
                                    "type": "TabularTranslator",
                                    "typeConversion": true,
                                    "typeConversionSettings": {
                                        "allowDataTruncation": true,
                                        "treatBooleanAsNumber": false
                                    }
                                }
                            }
                        }
                    ]
                }
            },
            {
                "name": "minorTransformation",
                "type": "TridentNotebook",
                "dependsOn": [
                    {
                        "activity": "ForEach",
                        "dependencyConditions": [
                            "Succeeded"
                        ]
                    },
                    {
                        "activity": "Copy data1",
                        "dependencyConditions": [
                            "Succeeded"
                        ]
                    },
                    {
                        "activity": "Copy_Data_Orders",
                        "dependencyConditions": [
                            "Succeeded"
                        ]
                    }
                ],
                "policy": {
                    "timeout": "0.12:00:00",
                    "retry": 0,
                    "retryIntervalInSeconds": 30,
                    "secureOutput": false,
                    "secureInput": false
                },
                "typeProperties": {
                    "notebookId": "e90a4147-42b3-4fdf-bf52-bbbe19fdb25a",
                    "workspaceId": "4b342d94-0249-4527-bcaa-5e7a49ec0bb7"
                },
                "externalReferences": {
                    "connection": "e389a7bf-dd36-4124-b002-7f5733c1f5af"
                }
            },
            {
                "name": "majorTransformation",
                "type": "TridentNotebook",
                "dependsOn": [
                    {
                        "activity": "Wait2",
                        "dependencyConditions": [
                            "Succeeded"
                        ]
                    }
                ],
                "policy": {
                    "timeout": "0.12:00:00",
                    "retry": 0,
                    "retryIntervalInSeconds": 30,
                    "secureOutput": false,
                    "secureInput": false
                },
                "typeProperties": {
                    "notebookId": "3791be6d-2f4c-435c-ae43-063d931cd736",
                    "workspaceId": "4b342d94-0249-4527-bcaa-5e7a49ec0bb7"
                },
                "externalReferences": {
                    "connection": "e389a7bf-dd36-4124-b002-7f5733c1f5af"
                }
            },
            {
                "name": "ML-kmeans",
                "type": "TridentNotebook",
                "dependsOn": [
                    {
                        "activity": "Wait1",
                        "dependencyConditions": [
                            "Succeeded"
                        ]
                    }
                ],
                "policy": {
                    "timeout": "0.12:00:00",
                    "retry": 0,
                    "retryIntervalInSeconds": 30,
                    "secureOutput": false,
                    "secureInput": false
                },
                "typeProperties": {
                    "notebookId": "f6d43337-0a04-40df-bbe7-4f7072d4dec6",
                    "workspaceId": "4b342d94-0249-4527-bcaa-5e7a49ec0bb7"
                },
                "externalReferences": {
                    "connection": "e389a7bf-dd36-4124-b002-7f5733c1f5af"
                }
            },
            {
                "name": "Wait1",
                "type": "Wait",
                "dependsOn": [
                    {
                        "activity": "majorTransformation",
                        "dependencyConditions": [
                            "Succeeded"
                        ]
                    }
                ],
                "typeProperties": {
                    "waitTimeInSeconds": 40
                }
            },
            {
                "name": "Wait2",
                "type": "Wait",
                "dependsOn": [
                    {
                        "activity": "minorTransformation",
                        "dependencyConditions": [
                            "Succeeded"
                        ]
                    }
                ],
                "typeProperties": {
                    "waitTimeInSeconds": 120
                }
            },
            {
                "name": "Copy data1",
                "type": "Copy",
                "dependsOn": [],
                "policy": {
                    "timeout": "0.12:00:00",
                    "retry": 0,
                    "retryIntervalInSeconds": 30,
                    "secureOutput": false,
                    "secureInput": false
                },
                "typeProperties": {
                    "source": {
                        "type": "DelimitedTextSource",
                        "storeSettings": {
                            "type": "HttpReadSettings",
                            "requestMethod": "GET"
                        },
                        "formatSettings": {
                            "type": "DelimitedTextReadSettings"
                        },
                        "datasetSettings": {
                            "annotations": [],
                            "type": "DelimitedText",
                            "typeProperties": {
                                "location": {
                                    "type": "HttpServerLocation",
                                    "relativeUrl": "siddharthpal18/Dataset/main/customers2.csv"
                                },
                                "columnDelimiter": ",",
                                "escapeChar": "\\",
                                "firstRowAsHeader": true,
                                "quoteChar": "\""
                            },
                            "schema": [],
                            "externalReferences": {
                                "connection": "7324fb70-2f24-44a7-8262-eef29d97fda3"
                            }
                        }
                    },
                    "sink": {
                        "type": "ParquetSink",
                        "storeSettings": {
                            "type": "AzureBlobStorageWriteSettings"
                        },
                        "formatSettings": {
                            "type": "ParquetWriteSettings",
                            "enableVertiParquet": true
                        },
                        "datasetSettings": {
                            "annotations": [],
                            "connectionSettings": {
                                "name": "Ecommerce_Data",
                                "properties": {
                                    "annotations": [],
                                    "type": "Lakehouse",
                                    "typeProperties": {
                                        "workspaceId": "4b342d94-0249-4527-bcaa-5e7a49ec0bb7",
                                        "artifactId": "41ebc24d-a955-4459-bf47-450d310623b9",
                                        "rootFolder": "Files"
                                    },
                                    "externalReferences": {
                                        "connection": "33502b3b-fafd-4967-a4e4-4a831e99abad"
                                    }
                                }
                            },
                            "type": "Parquet",
                            "typeProperties": {
                                "location": {
                                    "type": "LakehouseLocation",
                                    "folderPath": "bronze"
                                },
                                "compressionCodec": "snappy"
                            },
                            "schema": []
                        }
                    },
                    "enableStaging": false,
                    "translator": {
                        "type": "TabularTranslator",
                        "typeConversion": true,
                        "typeConversionSettings": {
                            "allowDataTruncation": true,
                            "treatBooleanAsNumber": false
                        }
                    }
                }
            },
            {
                "name": "Copy_Data_Orders",
                "type": "Copy",
                "dependsOn": [],
                "policy": {
                    "timeout": "0.12:00:00",
                    "retry": 0,
                    "retryIntervalInSeconds": 30,
                    "secureOutput": false,
                    "secureInput": false
                },
                "typeProperties": {
                    "source": {
                        "type": "DelimitedTextSource",
                        "storeSettings": {
                            "type": "HttpReadSettings",
                            "requestMethod": "GET"
                        },
                        "formatSettings": {
                            "type": "DelimitedTextReadSettings"
                        },
                        "datasetSettings": {
                            "annotations": [],
                            "type": "DelimitedText",
                            "typeProperties": {
                                "location": {
                                    "type": "HttpServerLocation",
                                    "relativeUrl": "siddharthpal18/Dataset/main/synthetic_orders.csv"
                                },
                                "columnDelimiter": ",",
                                "escapeChar": "\\",
                                "firstRowAsHeader": true,
                                "quoteChar": "\""
                            },
                            "schema": [],
                            "externalReferences": {
                                "connection": "7324fb70-2f24-44a7-8262-eef29d97fda3"
                            }
                        }
                    },
                    "sink": {
                        "type": "ParquetSink",
                        "storeSettings": {
                            "type": "AzureBlobStorageWriteSettings"
                        },
                        "formatSettings": {
                            "type": "ParquetWriteSettings",
                            "enableVertiParquet": true
                        },
                        "datasetSettings": {
                            "annotations": [],
                            "connectionSettings": {
                                "name": "Ecommerce_Data",
                                "properties": {
                                    "annotations": [],
                                    "type": "Lakehouse",
                                    "typeProperties": {
                                        "workspaceId": "4b342d94-0249-4527-bcaa-5e7a49ec0bb7",
                                        "artifactId": "41ebc24d-a955-4459-bf47-450d310623b9",
                                        "rootFolder": "Files"
                                    },
                                    "externalReferences": {
                                        "connection": "33502b3b-fafd-4967-a4e4-4a831e99abad"
                                    }
                                }
                            },
                            "type": "Parquet",
                            "typeProperties": {
                                "location": {
                                    "type": "LakehouseLocation",
                                    "folderPath": "bronze"
                                },
                                "compressionCodec": "snappy"
                            },
                            "schema": []
                        }
                    },
                    "enableStaging": false,
                    "translator": {
                        "type": "TabularTranslator",
                        "typeConversion": true,
                        "typeConversionSettings": {
                            "allowDataTruncation": true,
                            "treatBooleanAsNumber": false
                        }
                    }
                }
            }
        ],
        "lastModifiedByObjectId": "42d87c1a-25c2-4d74-bb92-02fabb0283b3",
        "lastPublishTime": "2026-05-20T03:14:16Z"
    }
}