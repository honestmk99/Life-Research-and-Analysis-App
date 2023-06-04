import uvicorn

# See the DEBUG.md file for why this is done this way.
# This is the function you should attach to the debugger.
if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="0.0.0.0", port=8000, log_level="debug")