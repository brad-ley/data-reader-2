from pages.reader.tdms_handler import read
import redis
import json

# redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)
redis_client = redis.Redis(host="0.0.0.0", port=6379, decode_responses=True)


def redis_read():
    files = redis_client.hget("files", "files")
    if files:
        groups = []
        files = json.loads(files)

        for file in files:  # type: ignore
            groups.append(read(file))

        if not groups:
            raise Exception("No files currently set!")

        return groups


def main():
    redis_read()


if __name__ == "__main__":
    main()
