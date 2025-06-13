"""FastAPI program - Chapter 4"""
from fastapi import Depends, FastAPI, HTTPException, Query, Path
from sqlalchemy.orm import Session
from datetime import date

import crud, schemas
from database import SessionLocal

api_description = """
This API provides read-only access to info from the SportsWorldCentral (SWC) Fantasy Footabll API.
The endpoints are grouped intot he following categories:

## Analytics
Get information about the health of the API and counts of leagues, teams, and players.

## Player
You can get a list of NFL players, or search for individual player by player_id.

## Scoring
You can get a list of NFL player performances, including the fantasy points they scored using the SWC league scoring.

## Membership
Get information about all the SWC fantasy football leagues and the teams in them.
"""

app = FastAPI(
    description=api_description,
    title="Sports World Central (SWC) Fantasy Football API",
    version="0.1"
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", 
         summary="Verify that the API is up.",
         description="Returns 'API health check successful' if the API is up.",
         response_description="API status",
         operation_id="v0_get_api_health",
         tags=["analytics"])
async def root():
    return {"message": "API health check successful"}

@app.get("/v0/players/", 
         summary="Get a list of NFL players.",
         description="Get a list of players, optionally filtered by name or last changed date.",
         response_description="A list of NFL players.",
         response_model=list[schemas.Player], 
         operation_id="v0_get_players",
         tags=["player"])
def read_players(skip: int = Query(0, description="The number of items to skip at the beginning of API call."),
                 limit: int = Query(100, description="The number of records to return after the skipped records."),
                 minimum_last_changed_date: date = Query(None, description="The minimum date of change that you want to return records. Exclude any records changed before this."),
                 first_name: str = Query(None, description="The first name of the players to return."),
                 last_name: str = Query(None, description="The last name of the players to return."),
                 db: Session = Depends(get_db)
                 ):
    players = crud.get_players(db,
                skip=skip,
                limit=limit,
                min_last_changed_date=minimum_last_changed_date,
                first_name=first_name,
                last_name=last_name)
    return players

@app.get("/v0/players/{player_id}", 
         response_model=schemas.Player, 
         summary="Get one player using the Player ID, which is internal to SWC.",
         description="If you have an SWC Player ID of a player from another API call such as v0_get_players, you can call this API using the player ID",
         response_description="One NFL player",
         operation_id="v0_get_players_by_player_id",
         tags=["player"])
def read_player(player_id: int = Path(description="The SWC Player ID for the player that should be returned."),
                db: Session = Depends(get_db)):
    player = crud.get_player(db,
                player_id=player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@app.get("/v0/performances/", 
         response_model=list[schemas.Performance], 
         summary="Get performance statistics for NFL players",
         description="Get a list of player performances optionally filtered by the last changed date.",
         response_description="A list of performances",
         operation_id="v0_get_performances",
         tags=["scoring"])
def read_performances(skip: int = Query(0, description="The number of items to skip at the beginning of API call."),
                      limit: int = Query(100, description="The number of records to return after the skipped records."),
                      minimum_last_changed_date: date = Query(None, description="The minimum date of change that you want to return records. Exclude any records changed before this."),
                      db: Session = Depends(get_db)):
    performances = crud.get_performances(db,
                    skip=skip,
                    limit=limit,
                    min_last_changed_date=minimum_last_changed_date)
    return performances

@app.get("/v0/leagues/{league_id}", 
         response_model=schemas.League, 
         summary="Get one fantasy league using the League ID, which is internal to SWC.",
         description="If you have an SWC League ID of a league from another API call such as v0_get_leagues, you can call this API using the league ID",
         response_description="A league",
         operation_id="v0_get_league",
         tags=["membership"])
def read_league(league_id:int = Path(description="The SWC League ID for the league to be returned."), 
                db: Session = Depends(get_db)):
    league = crud.get_league(db, league_id = league_id)
    if league is None:
        raise HTTPException(status_code=404, detail="League not found")
    return league

@app.get("/v0/leagues", 
         response_model=list[schemas.League], 
         summary="Get fantasy leagues",
         description="Get a list of fantasy leagues, optionally filtered by league name or last changed date.",
         response_description="A list of leagues",
         operation_id="v0_get_leagues",
         tags=["membership"])
def read_leagues(skip: int = Query(0, description="The number of items to skip at the beginning of API call."),
                 limit: int = Query(100, description="The number of records to return after the skipped records."),
                 minimum_last_changed_date: date = Query(None, description="The minimum date of change that you want to return records. Exclude any records changed before this."),
                 league_name: str = Query(None, description="The name of the leagues to return"),
                 db: Session = Depends(get_db)):
    leagues = crud.get_leagues(db,
                skip=skip,
                limit=limit,
                min_last_changed_date=minimum_last_changed_date,
                league_name=league_name)
    return leagues

@app.get("/v0/teams/", 
         response_model=list[schemas.Team], 
         summary="Get fantasy teams.",
         description="Get a list of fantasy teams, optionally filtered by team name or SWC League ID",
         response_description="A list of teams",
         operation_id="v0_get_teams",
         tags=["membership"])
def read_teams(skip: int = Query(0, description="The number of items to skip at the beginning of API call."),
               limit: int = Query(100, description="The number of records to return after the skipped records."),
               minimum_last_changed_date: date = Query(None, description="The minimum date of change that you want to return records. Exclude any records changed before this."),
               team_name: str = Query(None, description="The name of the teams to return."),
               league_id: int = Query(None, description="The SWC League Id of the league for which to return teams."),
               db: Session = Depends(get_db)):
    teams = crud.get_teams(db,
                skip=skip,
                limit=limit,
                min_last_changed_date=minimum_last_changed_date,
                team_name=team_name,
                league_id=league_id)
    return teams

@app.get("/v0/counts", 
         response_model=schemas.Counts, 
         summary="Get counts.",
         description="Get the count of leagues, teams, and players.",
         response_description="System counts",
         operation_id="v0_get_counts",
         tags=["analytics"])
def get_count(db: Session = Depends(get_db)):
    counts = schemas.Counts(
        league_count = crud.get_league_count(db),
        team_count = crud.get_team_count(db),
        player_count = crud.get_player_count(db))
    return counts