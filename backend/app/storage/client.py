from io import BytesIO

from minio import Minio

from app import config

client = Minio(
    config.MINIO_ENDPOINT,
    access_key=config.MINIO_ACCESS_KEY,
    secret_key=config.MINIO_SECRET_KEY,
    secure=False,
)


def init_storage():
    if not client.bucket_exists(config.MINIO_BUCKET):
        client.make_bucket(config.MINIO_BUCKET)


def upload(key: str, data: bytes) -> None:
    client.put_object(
        config.MINIO_BUCKET,
        key,
        BytesIO(data),
        length=len(data),
    )


def download(key: str) -> bytes:
    with client.get_object(config.MINIO_BUCKET, key) as response:
        return response.read()


def delete_prefix(prefix: str) -> None:
    objects = client.list_objects(config.MINIO_BUCKET, prefix=prefix, recursive=True)
    for obj in objects:
        if obj.object_name:
            client.remove_object(config.MINIO_BUCKET, obj.object_name)
