from pages.reader.tdms_handler import read
import redis
import json

redis_client = redis.Redis(
    host="redis://red-cs11kubtq21c73ekg21g:6379", decode_responses=True
)
# redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)
# redis_client = redis.Redis(host="0.0.0.0", port=6379, decode_responses=True)


def redis_read(write):
    files = redis_client.hget("files", "dict")
    if files:
        groups = []
        files = json.loads(files)

        for file, path in files.items():  # type: ignore
            groups.append(read(file, path, write=write))

        if not groups:
            raise Exception("No files currently set!")

        return groups


def main():
    redis_read(write=True)


if __name__ == "__main__":
    main()
