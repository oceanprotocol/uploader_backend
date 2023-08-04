# OCEAN Decentralized Backend Storage

## 📖 Menu

- [📄 Description](#description)
  - [⭐ Features](#features)
  - [🏛 Architecture](#architecture)
- [💾 Installation](#installation)
- [🔌 API Endpoints](#api-endpoints)
  - [ℹ️ Info](#info)
  - [💵 GetQuote](#getquote)
  - [⬆️ Upload](#upload)
  - [🔄 GetStatus](#getstatus)
  - [🔗 GetLink](#getlink)
- [🔐 DBS Private API Endpoints (Used by Microservices)](#dbs-private-api-endpoints-used-by-microservices)
  - [✅ Register](#register)
- [💾 Storage Flow](#storage-flow)
- [⚙️ ENVS](#envs)
- [🐳 Docker Deployment](#docker-deployment)
- [🤝 Support](#support)
- [🗺 Roadmap](#roadmap)
- [🤖 Contributing](#contributing)
- [✍️ Authors and acknowledgment](#authors-and-acknowledgment)
- [📜 License](#license)
- [🔗 Associated Projects](#associated-projects)


## Description
Initial repository implementing a solution for the Ocean Decentralized Backend storage management service [explained here](https://github.com/oceanprotocol/decentralized_storage_backend/issues/1)

It is a django-based solution benefitting from django-rest-framework for the class based API Views implementation and drf-spectacular for the Swagger based auto documentation of the API usage. 

### Features:
- User content uploads.
- Payment handling.
- Pushing content to decentralized storage.
- Returning the storage object for DDO.

### Architecture:

1. **DBS:**
    - Exposes public API for frontend operations.
    - Exposes private API for microservices (through a private network).
    - Proxies requests to microservices.
    - Manages IPFS temporary storage.
2. **1-N Storage MicroServices:** Each microservice can handle different storage types.


## Installation

This is a server-side API based on Python and Django/DRF so first make sure you have python and pip installed.

First, clone this project in the appropriate location in your workspace.

Then, use virtualenv to isolate your development environment and setup the virtual env for this project: `python -m virtualenv venv`

The server can be run using the `./manage.py runserver` method from the `./server/` directory.

Tests can be launched using `./manage.py test`

You can create a superuser with `./manage.py createsuperuser` to be able to access the back-office on `http://localhost:8000/admin` by default or everything else you previously defined.

## API Endpoints

- Storage List: `/`
- Register Storage: `/register`
- Get Status: `/getStatus`
- Get Link: `/getLink`
- Get Quote: `/getQuote`
- Upload File: `/upload`


### Info
**Description:** Information about supported storage types & payments.

**Path:** `/`

**Arguments:** None

**Returns:**
```
[
    {
        "type": "filecoin",
        "description":  "File storage on FileCoin",
        "payment":
            [ 
                {
                    "chainId": 1,
                    "acceptedTokens": 
                        [ 
                            "OCEAN": "0xOCEAN_on_MAINNET",
                            "DAI": "0xDAI_ON_MAINNET"
                        ]
                },
                {
                    "chainId": "polygon_chain_id",
                    "acceptedTokens": 
                        [ 
                            "OCEAN": "0xOCEAN_on_POLYGON",
                            "DAI": "0xDAI_ON_POLYGON"
                        ]
                }
            ]
    },
    {
        "type": "arweave",
        "description":  "File storage on Arweave",
        "payment":
            [ 
                {
                    "chainId": 1,
                    "acceptedTokens": 
                        [ 
                            "OCEAN": "0xOCEAN_on_MAINNET",
                            "DAI": "0xDAI_ON_MAINNET"
                        ]
                },
                {
                    "chainId": "arweave_chain_id",
                    "acceptedTokens": 
                        [ 
                            "ARWEAVE": "0xARWEAVEtoken_on_arweaveChain"
                        ]
                }
            ]
    }
]    
```

### GetQuote
**Description:** Gets a quote in order to store some files on a specific storage.

**Path:** `POST /getQuote`

**Arguments:**
```
{
    "type": "filecoin",
    "files": [{"length":2343545}, {"length":2343545}],
    "duration": 4353545453,
    "payment": {
        "chainId": 1,
        "tokenAddress": "0xOCEAN_on_MAINNET"
    },
    "userAddress": "0x456"
}
```

**Returns:**
```
{
    "tokenAmount": 500,
    "approveAddress": "0x123",
    "chainId": 1,
    "tokenAddress": "0xOCEAN_on_MAINNET",
    "quoteId": "xxxx"
}
```

### Upload
**Description:** Upload files, according to the quote request.

**Path:** `POST /upload?quoteId=xxxx&nonce=1&signature=0xXXXXX`

**Input:**
- `quoteId`
- `nonce`: timestamp (has to be higher than previous stored nonce for this user)
- `signature`: user signed hash of SHA256(quoteID+nonce)

**Returns:** 200 OK if succeeded

### GetStatus

**Description:** Gets status for a job.

**Path:** `POST /getStatus?quoteId=xxx`

**Returns:**
{
    "status": 0
}
Where status can be:

- `0`: No such quote
- `1-99`: Waiting for files to be uploaded by the user
- `100-199`: Processing payment
- `200-299`: Processing payment failure modes
- `300-399`: Uploading files to storage
- `400`: Upload done
- `401-499`: Upload failure modes

### GetLink

**Description:** Gets DDO files object for a job.

**Path:** `POST /getLink?quoteId=xxx&nonce=1&signature=0xXXXXX`

**Input:**
- `quoteId`
- `nonce`: timestamp (has to be higher than previous stored nonce for this user)
- `signature`: user signed hash of SHA256(quoteID+nonce)

**Returns:**

```
[
    {
        "type": "filecoin",
        "CID": "xxxx",
        "dealIDs":["x" , "x2"]
    }
]
```

Reference: [Ocean Protocol DID DDO](https://docs.oceanprotocol.com/core-concepts/did-ddo#files) 

## DBS Private API Endpoints (Used by Microservices)

**Note:** These endpoints are utilized on a different port.

### Register

**Description:** Register a new microservice which handles a storage.

**Path:** `POST /register`

**Input:**

```
{
    "type": "filecoin",
    "description":  "File storage on FileCoin",
    "url": "http://microservice.url",
    "payment":
            [ 
                {
                    "chainId": 1,
                    "acceptedTokens": 
                        [ 
                            "OCEAN": "0xOCEAN_on_MAINNET",
                            "DAI": "0xDAI_ON_MAINNET"
                        ]
                },
                {
                    "chainId": "polygon_chain_id",
                    "acceptedTokens": 
                        [ 
                            "OCEAN": "0xOCEAN_on_POLYGON",
                            "DAI": "0xDAI_ON_POLYGON"
                        ]
                }
            ]
}  
```

**Returns:** 200 OK if accepted

**Additional Information:** Each microservice should call this endpoint every 10 minutes, otherwise the storage type will be removed from the main list.


## Storage Flow

### 1. Retrieving Storage Types & Payment Options

- **Frontend -> DBS:** Fetch storage types & payment options.
- **DBS -> Frontend:** Return storage types & payment options.

### 2. Getting Quote for File Storage

- **Frontend -> DBS:** Request quote for storing file on Filecoin.
- **DBS -> Filecoin microservice:** Request quote for storing file on Filecoin.
- **Filecoin microservice -> DBS:** Return payment details & quoteId.
- **DBS -> Frontend:** Return payment details & quoteId.

### 3. Uploading Files

- **Frontend -> DBS:** Upload files.
- **DBS -> IPFS:** Write files.
- **DBS -> Filecoin microservice:** Store data using upload endpoint.
- **Filecoin microservice -> IPFS:** Read files.
- **Filecoin microservice -> Filecoin microservice:** Store files on Filecoin.

### 4. Checking Upload Status

- **Frontend -> DBS:** Get Status.
- **DBS -> Filecoin microservice:** Get Status.
- **Filecoin microservice -> DBS:** Upload done.
- **DBS -> Frontend:** Confirm upload is done.

### 5. Retrieving File Link

- **Frontend -> DBS:** Get Link.
- **DBS -> Filecoin microservice:** Get Link.
- **Filecoin microservice -> DBS:** Return Filecoin object.
- **DBS -> Frontend:** Return Filecoin object.


## ENVS

Check .env.example for all of the required environmental variables. 

## Docker Deployment

1. **Initialize Submodules**:
   `git submodule init`
   `git submodule update`
2. **Build Docker Image**:
   `docker build -t ocean-dbs .`
3. **Configure Environment**: Copy contents of `.env.example` into `.env` and adjust necessary values.
4. **Run Docker Compose**:
   `docker compose up`

## Support

Please open issues on github if you need support of have any questions.

## Roadmap

Stay tuned for more integrations and services. Follow the issues on github to see the latest development plans.  


## Contributing

This project is fully open-source, backed by the $OCEAN community and is obviously open for contributions.

The first version has been implemented following the TDD strategy, so please first familiarize yourself with the test suite, which can be run using the `./manage.py test` command, directly from the root of your server in the context of your virtual environment.

## Authors and acknowledgment

Thanks to the $OCEAN community for the funding and the $OCEAN core team for the technical support and insights.

## License

Released under the Apache License.

## Associated Projects

- [DBS Filecoin microservice](https://github.com/oceanprotocol/dbs_filecoin)
- [DBS Arweave microservice](https://github.com/oceanprotocol/dbs_arweave)
