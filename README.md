# Ocean Uploader Backend

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
  - [📜 GetHistory](#gethistory)
- [🔐 Uploader Private API Endpoints (Used by Microservices)](#uploader-private-api-endpoints-used-by-microservices)
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

The Ocean Uploader Backend service is a django-based solution the acts as a proxy for calling the different Uploader microservices. The initial specifications are [explained here](https://github.com/oceanprotocol/uploader_backend/issues/1).

### Features:
- User content uploads.
- Payment handling.
- Pushing content to decentralized storage.
- Returning the storage object for DDO.

### Architecture:

1. **Uploader Backend:**
    - Exposes public API for frontend operations.
    - Exposes private API for microservices (through a private network).
    - Proxies requests to microservices.
    - Manages IPFS temporary storage.
2. **1-N Uploader MicroServices:** Each microservice can handle different storage types.

## Usage

If you wish to use the Ocean Uploader Backend in your project we recommend implementing it using the [Uploader.js library](https://www.npmjs.com/package/@oceanprotocol/uploader). You will also require the following information:

This server is currently deployed at: `https://dbs.oceanprotocol.com`

The account is: `0x5F8396D1BfDa5259Ee89196F892E4401BF3B596d`

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
- Get History: `/getHistory`


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

### GetHistory

**Description**: Gets history quotes for a certain user

**Path**: `GET /getHistory?userAddress=xxx&nonce=1&signature=0xXXXXX&page=1&pageSize=25`

**Input:**
- `userAddress`: wallet address
- `nonce`: timestamp (has to be higher than previous stored nonce for this user)
- `signature`: user signed hash of SHA256('' + nonce)
- *(Optional)*`page`: page number for user history, set default to 1
- *(Optional)*`pageSize`: page size, set default to 25

**Returns:**

```
[
    [{  
        "type": 'arweave',
        "quoteId": "23",
        "chainId": 80001,
        "tokenAddress": "0x222",
        "tokenAmount": "999999999",
        "approveAddress": "0x1234",
        "requestId": "xxxx"
    }],
    [{
        "type": 'filecoin',
        "quoteId": "23",
        "status": 400,
        "chainId": 80001,
        "tokenAddress": "0x222",
        "tokenAmount": "999999999",
        "approveAddress": "0x1234",
        "transactionHash": "xxxx"
    }]
]
```

Reference: [Ocean Protocol DID DDO](https://docs.oceanprotocol.com/core-concepts/did-ddo#files) 

## Uploader Private API Endpoints (Used by Microservices)

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

![image](https://github.com/oceanprotocol/uploader_backend/assets/50501033/2c34321d-f809-40c1-911d-64a7727821f1)


![image](https://github.com/oceanprotocol/uploader_backend/assets/50501033/42200343-38c2-4d61-a939-32212ed8217e)



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

This project is fully open-source, backed by the OCEAN community and is open for contributions.

The first version has been implemented following the TDD strategy, so please first familiarize yourself with the test suite, which can be run using the `./manage.py test` command, directly from the root of your server in the context of your virtual environment.

## Authors and acknowledgment

Thanks to the OCEAN community for the funding and the OCEAN core team for the technical support and insights.

## License

Released under the Apache License.

## Associated Projects

- [Uploader Filecoin microservice](https://github.com/oceanprotocol/uploader_filecoin)
- [Uploader Arweave microservice](https://github.com/oceanprotocol/Uploader_arweave)
