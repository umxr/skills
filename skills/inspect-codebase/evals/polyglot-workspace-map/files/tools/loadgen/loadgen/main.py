import os
import httpx

GATEWAY = os.environ.get("GATEWAY_URL", "http://localhost:8080")


def run() -> None:
    with httpx.Client() as c:
        for i in range(1000):
            c.post(f"{GATEWAY}/relay/topic-{i % 8}", content=b"x" * 256,
                   headers={"Authorization": "Bearer dev"})


if __name__ == "__main__":
    run()
