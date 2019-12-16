## API Overview
--------------
### 1 - Queues
#### 1.1 - Create a new pool

| Method | URI |
| :--- | :--- |
| `POST` | `/api/pools` |

**Request body**
```json
{
    "name":"my-pool"
}
```

**Response example**
```json
{
	"msg": "Created pool [my-pool]"
}
```
#### 1.2 - Retrieves a list of all pools

| Method | URI |
| :--- | :--- |
| `GET` | `/api/pools` |

**Response example**
```json
{
    "my-pool": {
        "name": "my-pool",
        "nodes": {
	        "1ddc5e78-0d6b-45e3-9dcd-fb7347ed76f9" : {
                "type":"loose",
                "state": "provisioning",
                "ip":"10.30.5.10"
            },
            "cff3d7c3-a708-4458-badb-fb1d8643137a" : {
                "type":"loose",
                "state": "failed",
                "ip":"10.30.5.50"
            },
            "04ad57a3-a1a7-41df-879d-70e78ad9ff4b" : {
                "type":"requested",
                "state": "ready",
                "spec":{
                    "name":"worker-node-1",
                    "memory":2,
                    "vCPU":2,
                    "disk":10,
                    "imageId":"f4ab9873-ad53-4968-ad16-01b919ba9c48"
                },
                "ip": "10.30.5.1"
            },
            "4426efaa-dd28-4117-aeea-c8b8930217f2" : {
                "type":"requested",
                "state": "provisioning",
                "spec":{
                    "name":"worker-node-2",
                    "memory":2,
                    "vCPU":2,
                    "disk":10,
                    "imageId":"f4ab9873-ad53-4968-ad16-01b919ba9c48"
                },
                "ip":"10.30.5.30"
            },
            "8f8736d4-d5e8-4f63-bb3f-c252a202acb3" : {
                "type":"requested",
                "state": "created",
                "spec":{
                    "name":"worker-node-3",
                    "memory":2,
                    "vCPU":2,
                    "disk":10,
                    "imageId":"f4ab9873-ad53-4968-ad16-01b919ba9c48"
                }
            }
        }
    }
}

```

#### 1.3 - Retrieves a pool by it id

| Method | URI |
| :--- | :--- |
| `GET` | `/api/pools/{pool_id}` |

**Response example**
```json
{
    "name": "my-pool",
    "nodes": {
        "1ddc5e78-0d6b-45e3-9dcd-fb7347ed76f9" : {
            "type":"loose",
            "state": "provisioning",
            "ip":"10.30.5.10"
        },
        "cff3d7c3-a708-4458-badb-fb1d8643137a" : {
            "type":"loose",
            "state": "failed",
            "ip":"10.30.5.50"
        },
        "04ad57a3-a1a7-41df-879d-70e78ad9ff4b" : {
            "type":"requested",
            "state": "ready",
            "spec":{
                "name":"worker-node-1",
                "memory":2,
                "vCPU":2,
                "disk":10,
                "imageId":"f4ab9873-ad53-4968-ad16-01b919ba9c48"
            },
            "ip": "10.30.5.1"
        },
        "4426efaa-dd28-4117-aeea-c8b8930217f2" : {
            "type":"requested",
            "state": "provisioning",
            "spec":{
                "name":"worker-node-2",
                "memory":2,
                "vCPU":2,
                "disk":10,
                "imageId":"f4ab9873-ad53-4968-ad16-01b919ba9c48"
            },
            "ip":"10.30.5.30"
        },
        "8f8736d4-d5e8-4f63-bb3f-c252a202acb3" : {
            "type":"requested",
            "state": "created",
            "spec":{
                "name":"worker-node-3",
                "memory":2,
                "vCPU":2,
                "disk":10,
                "imageId":"f4ab9873-ad53-4968-ad16-01b919ba9c48"
            }
        }
    }
}
```
#### 1.4 - Adds a loose node to a given pool
| Method | URI |
| :--- | :--- |
| `POST` | `/api/pools/{pool_id}/nodes` |

**Request Body**
```json
{
    "type":"loose",
    "ip":"10.30.5.10"
}
```
**Response example**
```json
{
	"id": "1ddc5e78-0d6b-45e3-9dcd-fb7347ed76f9"
}
```

#### 1.5 - Adds a requested node to a given pool
| Method | URI |
| :--- | :--- |
| `POST` | `/api/pools/{pool_id}/nodes` |

**Request Body**
```json
{
    "type":"requested",
    "spec":{
		"name":"worker-node",
		"memory":2,
		"vCPU":2,
		"disk":10,
		"imageId":"f4ab9873-ad53-4968-ad16-01b919ba9c48"
    }
}
```
**Response example**
```json
{
	"id": "438d5c6b-ea01-4ae5-ae3d-5954ccd9551a"
}
```

### 2 - Public Key

#### 2.1 - Get Service Public Key
| Method | URI |
| :--- | :--- |
| `GET` | `/api/publicKey` |

**Response example**:
```json
{
    "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDhokU/C8O03gSlyYzup8lq/kCbttz4oL4rI7hEwJN/P6wzeq8YHGMKO5zOtDZ4GIKSQ1S7tbwB2CmIUiFbUdOtI+9st7gfVGlK/3CLaV7Scuh9thN5wj8yRrCn9P/zLUat5mAjmXkfKm/MT+vuF+3hBRwPHCHWh1iRLL5cT3wdIgUamjeUuKMQdOdV0zxMOexxRpH7uLHIPUY1GhRE8HUVcvaVSNf/juUy+y3VZMgQujpuritQ0iUny19b04/P/wl7AbG/4hsnNcPygJC1LIZEPbV71VMl7jGwv+uacF3oSY/7HV8j7Q57HFznwljBX/KhrazIqh3S6hlaNzAqZY0h pool.provider@lsd.ufcg.edu.br"
}
```

## Responses

Many API endpoints return the JSON representation of the resources created or edited. However, if an invalid request is submitted, or some other error occurs, service must returns a JSON response in the following format:

```javascript
{
  "message" : string  
}
```

The `message` attribute contains a message commonly used to indicate errors.


## Status Codes

The service returns the following status codes in its API:

| Status Code | Description |
| :--- | :--- |
| 200 | `OK` |
| 201 | `CREATED` |
| 400 | `BAD REQUEST` |
| 404 | `NOT FOUND` |
| 500 | `INTERNAL SERVER ERROR` |
