with open("backend/main.py", "r") as f:
    content = f.read()
if "routers import test_error" not in content:
    content = content.replace("from routers import auth, community", "from routers import auth, community, test_error")
    content = content.replace("app.include_router(auth.router)", "app.include_router(auth.router)\napp.include_router(test_error.router)")
    with open("backend/main.py", "w") as f:
        f.write(content)
