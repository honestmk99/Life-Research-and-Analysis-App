## Debug info

### FastApi Doc (not working)

This is how the FastApi doc say to debug

    import uvicorn
    from app import app

    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")

This does not work with motor, async mongo. 
You will receive `Future attached to a different loop` error.


### Solution

[https://github.com/fastapi-users/fastapi-users/discussions/663]()

    import uvicorn
    
    if __name__ == "__main__":
        uvicorn.run("app:app", host="0.0.0.0", port=5000, log_level="info")

Theory according to the above linked discussion:

- When we import app from the app module, it automatically loads the AsyncIOMotorClient instance, which is binded to the default asyncio loop.
- When Uvicorn starts, it automatically creates a new loop and set it as the new default.
- Problem: Motor was already instantiated with another loop; hence the error.

When we let Uvicorn import the app by itself (with the "app:app" argument), it also creates a new loop and set it by default; but it imports Motor after, so they are binded to the same loop.

Another solution is to prevent Uvicorn to setup the loop by itself using the loop argument, but I don't know what could be the potential gotchas around this:

    import uvicorn
    from app import app
    
    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info", loop="none")