"""
main.py

The backend flask backend server


"""

import atexit
import flask_cors
from flask import Flask, jsonify, request
from flask_restful import Api

import os
import sys
from dotenv import load_dotenv
from pathlib import Path

import docker

# load env from ../.env
load_dotenv("../.env")

# -------------------------------------------------------------------- #
# Flask app setup

app = Flask(__name__)
app.config["CORS_HEADERS"] = "Content-Type"
flask_cors.CORS(app)

api = Api(app)

# -------------------------------------------------------------------- #
# debug endpoints

@app.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint to verify if the server is running.
    :return: JSON response indicating server status.
    """
    return jsonify({"status": "ok", "message": "Server is running"})

# -------------------------------------------------------------------- #
# Import routes after app initialization to avoid circular imports

from routes import (
    filter_route,
    form_route,
    image_route,
)

# register routes
app.register_blueprint(filter_route.filter_blueprint, url_prefix="/filter")
app.register_blueprint(form_route.form_blueprint, url_prefix="/form")
# app.register_blueprint(image_route.image_blueprint, url_prefix="/image")

# -------------------------------------------------------------------- #
# start app 

if __name__ == "__main__":
    # # check if docker container is running
    # client = docker.from_env()

    # DATABASE_CONTAINER_NAME = os.getenv("DOCKER_CONTAINER_NAME", "automated-video-editor")
    # DATABASE_CONTAINER_PORT = os.getenv("DOCKER_CONTAINER_PORT", 27017)
    # DATABASE_IMAGE_NAME = os.getenv("DOCKER_IMAGE_NAME", "mongodb/mongodb-community-server:6.0")
    # DATABASE_CONTAINER_BASE_PATH = os.getenv("DOCKER_CONTAINER_BASE_PATH", "database")

    # # check if the container is running, if not, start it
    # try:
    #     container = client.containers.get(DATABASE_CONTAINER_NAME)
    #     if container.status != "running":
    #         print(f"Starting container {DATABASE_CONTAINER_NAME}...")
    #         container.start()
    #     else:
    #         print(f"Container {DATABASE_CONTAINER_NAME} is already running.")
    # except docker.errors.NotFound:
    #     print(f"Container {DATABASE_CONTAINER_NAME} not found. Creating and starting a new container...")
    #     client.containers.run(
    #         DATABASE_IMAGE_NAME,
    #         name=DATABASE_CONTAINER_NAME,
    #         ports={f"{DATABASE_CONTAINER_PORT}/tcp": DATABASE_CONTAINER_PORT},
    #         detach=True,
    #         volumes={os.path.join(os.getcwd(), DATABASE_CONTAINER_BASE_PATH): {'bind': '/data/db', 'mode': 'rw'}}
    #     )
    #     print(f"Container {DATABASE_CONTAINER_NAME} started successfully.")

    # # register cleanup function to stop the container on exit
    # def stop_container():
    #     try:
    #         container = client.containers.get(DATABASE_CONTAINER_NAME)
    #         if container.status == "running":
    #             print(f"Stopping container {DATABASE_CONTAINER_NAME}...")
    #             container.stop()
    #             print(f"Container {DATABASE_CONTAINER_NAME} stopped successfully.")
    #     except docker.errors.NotFound:
    #         print(f"Container {DATABASE_CONTAINER_NAME} not found. No action taken.")
    # atexit.register(stop_container)

    # [ALPHA] CACHE - setup flask global cache
    app.config["EDITING_INSTANCE"] = {
        "form": {
            "source_url": None,
            "width": 1080,
            "height": 1920,
            "audio_voice": "bm_george",
            "audio_language": "british",
            "video_title": "My Video",
            "video_description": "This is a test video description.",
            "intro_image": False,
            "background_video": None,
            "text_time_padding": 0,
            "framerate": 30
        },
        "segment_information": {},
        "duration": 0
    }

    # start the Flask app
    HOST_IP = os.getenv("BACKEND_SERVER_HOST", "0.0.0.0")
    PORT = int(os.getenv("BACKEND_SERVER_PORT", 5000))
    print(f"Starting server on {HOST_IP}:{PORT}")
    app.run(debug=True, host=HOST_IP, port=PORT)