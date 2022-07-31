# python-buck
S3-Compatible Object Storage Server

## Installation
```sh
pip install .
```

## Usage
### Install AWS CLI
```sh
$ pip install awscli
Successfully installed awscli
```

### Build Docker Image
```sh
$ docker build -t buck .
Successfully built 792623fa2e9a
Successfully tagged buck
```

### Run Docker Container
```sh
$ docker run -p 8080:8080 buck
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

### Interact with S3 Server
#### List Buckets
```sh
$ aws --endpoint-url "http://localhost:8080/" s3 ls
2022-07-31 18:06:51 bucket
```

#### Upload Object
```sh
$ echo "test!" > file.txt
$ aws --endpoint-url "http://localhost:8080/" s3 file.txt s3://bucket/
upload: file.txt to s3://bucket/file.txt
```

#### Download Object
```sh
$ aws --endpoint-url "http://localhost:8080/" s3api get-object --bucket bucket --key file.txt object.txt
{
    "AcceptRanges": "bytes",
    "ContentLength": 6,
    "ContentType": "text/plain; charset=utf-8",
    "Metadata": {}
}
$ cat object.txt
test!
```