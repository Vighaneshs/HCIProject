import requests

# Simple client to call the backend API
def send_to_backend(filename: str, task: str):
    url = "http://127.0.0.1:8000/api/analyze"

    # Read the image file and send it as multipart/form-data
    # The `files` mapping uses the form: field_name: (filename, fileobj, content_type)
    with open(filename, "rb") as f:
        files = {"image": (filename, f, "image/png")}
        data = {"task": task}
        try:
            # Timeout after 60 seconds
            r = requests.post(url, files=files, data=data, timeout=60)

            # Raise for HTTP errors
            r.raise_for_status()

            # Parse JSON response
            j = r.json()

            # Expecting {"status":"ok","reply":"..."} or {"status":"error","message":"..."}
            if j.get("status") == "ok":
                return True, j["reply"]
            else:
                return False, j.get("message", "unknown error")
        except Exception as e:
            return False, str(e)