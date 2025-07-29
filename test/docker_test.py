import os
import docker
import atexit

client = docker.from_env()

DATABASE_CONTAINER_NAME = os.getenv("DOCKER_CONTAINER_NAME", "automated-video-editor")
DATABASE_CONTAINER_PORT = os.getenv("DOCKER_CONTAINER_PORT", 27017)
DATABASE_IMAGE_NAME = os.getenv("DOCKER_IMAGE_NAME", "mongodb/mongodb-community-server:6.0")
DATABASE_CONTAINER_BASE_PATH = os.getenv("DOCKER_CONTAINER_BASE_PATH", "database")

def start_container():
    try:
        container = client.containers.get(DATABASE_CONTAINER_NAME)
        if container.status != "running":
            print(f"Starting container {DATABASE_CONTAINER_NAME}...")
            container.start()
        else:
            print(f"Container {DATABASE_CONTAINER_NAME} is already running.")
    except docker.errors.NotFound:
        print(f"Container {DATABASE_CONTAINER_NAME} not found. Creating and starting a new container...")
        client.containers.run(
            DATABASE_IMAGE_NAME,
            name=DATABASE_CONTAINER_NAME,
            ports={f"{DATABASE_CONTAINER_PORT}/tcp": DATABASE_CONTAINER_PORT},
            detach=True,
            volumes={os.path.join(os.getcwd(), DATABASE_CONTAINER_BASE_PATH): {'bind': '/data/db', 'mode': 'rw'}}
        )
        print(f"Container {DATABASE_CONTAINER_NAME} started successfully.")

def stop_container():
    try:
        container = client.containers.get(DATABASE_CONTAINER_NAME)
        if container.status == "running":
            print(f"Stopping container {DATABASE_CONTAINER_NAME}...")
            container.stop()
            print(f"Container {DATABASE_CONTAINER_NAME} stopped successfully.")
    except docker.errors.NotFound:
        print(f"Container {DATABASE_CONTAINER_NAME} not found. No action taken.")

if __name__ == "__main__":
    start_container()
    atexit.register(stop_container)
    print("MongoDB Docker container is managed. Press Ctrl+C to stop and cleanup.")
    try:
        while True:
            pass  # Keep the script running
    except KeyboardInterrupt:
        print("Exiting...")


import docker
