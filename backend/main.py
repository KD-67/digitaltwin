# This is the file that must be run to start the server. It establishes all the paths to relevant files, makes sure the backend knows what
# port the frontend is running on, connects to the SQLite database, and store some important paths a app.state so they don't have to keep
# being imported every time they're needed.

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from backend.schema import schema

from backend.startup.database_logistics import init_db, sync_subjects, sync_markers, sync_measurements

BASE_DIR        = os.path.dirname(os.path.abspath(__file__))                           # resolves to: "c:\Users\kevin\proj\digitaltwin\backend"
REPO_ROOT       = os.path.dirname(BASE_DIR)                                            # resolves to: "c:\Users\kevin\proj\digitaltwin"
DATA_DIR        = os.path.join(REPO_ROOT, "data")                                      # resolves to: "c:\Users\kevin\proj\digitaltwin\data"
DB_PATH         = os.path.join(DATA_DIR, "HDT.db")                                     # resolves to: "c:\Users\kevin\proj\digitaltwin\data\HDT.db"
RAWDATA_ROOT    = os.path.join(DATA_DIR, "rawdata")                                    # resolves to: "c:\Users\kevin\proj\digitaltwin\data\rawdata"
UTILITIES_ROOT  = os.path.join(DATA_DIR, "utilities")                                  # resolves to: "c:\Users\kevin\proj\digitaltwin\data\utilities"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_context(request: Request) -> dict:
    return {
        "db_path":      request.app.state.db_path,
        "rawdata_root": request.app.state.rawdata_root,
    }

graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")


@app.on_event("startup")
def startup ():
    # sync data sources into database 
    init_db(DB_PATH)
    sync_subjects(DB_PATH, RAWDATA_ROOT)
    sync_markers(DB_PATH, UTILITIES_ROOT)
    sync_measurements(DB_PATH, RAWDATA_ROOT)

    #store shared paths and state on app.state
    app.state.db_path         = DB_PATH
    app.state.rawdata_root    = RAWDATA_ROOT