"""Server-side, allow-listed model downloads for the ComfyUI web interface."""

import asyncio
import json
import os
import uuid
from pathlib import Path
from urllib.parse import urlparse

import aiohttp
from aiohttp import web
import folder_paths
from server import PromptServer

WEB_DIRECTORY = "./web"
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

routes = PromptServer.instance.routes
ALLOWED_HOST_SUFFIXES = ("huggingface.co", "hf.co", "civitai.com")
ALLOWED_FOLDERS = {"checkpoints", "loras", "vae", "text_encoders", "diffusion_models", "clip_vision", "controlnet", "upscale_models", "embeddings"}
ALLOWED_EXTENSIONS = {".safetensors", ".ckpt", ".pt", ".pth", ".bin"}
downloads = {}
download_queue = asyncio.Queue()
worker_started = False


def allowed_host(host):
    host = (host or "").lower()
    return any(host == suffix or host.endswith("." + suffix) for suffix in ALLOWED_HOST_SUFFIXES)


async def worker():
    while True:
        download_id, url, folder, filename = await download_queue.get()
        item = downloads[download_id]
        item["state"] = "running"
        try:
            target_dir = Path(folder_paths.get_folder_paths(folder)[0])
            target = (target_dir / filename).resolve()
            if target.parent != target_dir.resolve():
                raise ValueError("Invalid target path")
            if target.exists():
                item.update(state="complete", message="Already installed")
                continue
            temporary = target.with_suffix(target.suffix + ".part")
            timeout = aiohttp.ClientTimeout(total=None, sock_connect=30, sock_read=120)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, allow_redirects=True) as response:
                    if not allowed_host(urlparse(str(response.url)).hostname):
                        raise ValueError("Download redirected to a non-allowed host")
                    response.raise_for_status()
                    item["total"] = int(response.headers.get("Content-Length", 0))
                    with open(temporary, "wb") as handle:
                        async for chunk in response.content.iter_chunked(1024 * 1024):
                            handle.write(chunk)
                            item["received"] += len(chunk)
            os.replace(temporary, target)
            item.update(state="complete", message="Installed")
        except Exception as error:
            item.update(state="error", message=str(error))
        finally:
            download_queue.task_done()


@routes.post("/t0b121/model-installer/download")
async def download_model(request):
    global worker_started
    data = await request.json()
    url, folder = data.get("url", ""), data.get("folder", "")
    filename = Path(data.get("filename", "")).name
    if urlparse(url).scheme != "https" or not allowed_host(urlparse(url).hostname):
        return web.json_response({"error": "Only HTTPS downloads from Hugging Face or CivitAI are allowed."}, status=400)
    if folder not in ALLOWED_FOLDERS or Path(filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        return web.json_response({"error": "Invalid model folder or filename."}, status=400)
    download_id = str(uuid.uuid4())
    downloads[download_id] = {"state": "queued", "received": 0, "total": 0, "message": "Queued"}
    await download_queue.put((download_id, url, folder, filename))
    if not worker_started:
        worker_started = True
        asyncio.create_task(worker())
    return web.json_response({"id": download_id})


@routes.get("/t0b121/model-installer/status/{download_id}")
async def download_status(request):
    item = downloads.get(request.match_info["download_id"])
    if item is None:
        return web.json_response({"error": "Unknown download"}, status=404)
    return web.json_response(item)


@routes.get("/t0b121/model-installer/workflow-models")
async def workflow_models(_request):
    """Expose only model sources declared by ComfyUI's bundled templates."""
    sources = {}
    for blueprint in Path("/opt/comfyui/blueprints").glob("*.json"):
        try:
            data = json.loads(blueprint.read_text())
            for node in data.get("nodes", []):
                for model in node.get("properties", {}).get("models", []):
                    if model.get("directory") in ALLOWED_FOLDERS and model.get("name") and model.get("url"):
                        sources[model["name"]] = {"url": model["url"], "folder": model["directory"]}
            for graph in data.get("definitions", {}).get("subgraphs", []):
                for node in graph.get("nodes", []):
                    for model in node.get("properties", {}).get("models", []):
                        if model.get("directory") in ALLOWED_FOLDERS and model.get("name") and model.get("url"):
                            sources[model["name"]] = {"url": model["url"], "folder": model["directory"]}
        except (OSError, ValueError, TypeError):
            continue
    return web.json_response(sources)
