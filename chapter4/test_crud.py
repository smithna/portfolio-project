"""Testing SQLAlchemy Helper Functions"""
import pytest
from datetime import date

import crud
from database import SessionLocal

# use a test date of 4/1/1/2024 to test the min_last_changed_date.
test_date = date(2024,4,1)

@pytest.fixture(scope="function")
def db_session():
    """This starts a database ssession and closes it when done"""
    session = SessionLocal()
    yield session
    session.close()

def test_get_player(db_session):
    """Tests you can get the first player"""
    player = crud.get_player(db_session, player_id = 1001)
    assert player.player_id == 1001

def test_get_players(db_session):
    """Tests that the count of players in the database is what is expected"""
    players = crud.get_players(db_session, skip=0, limit = 100000, min_last_changed_date=test_date)
    assert len(players) == 1018

def test_get_players_by_name(db_session):
    """Tests that the count players in the database is what is expected"""
    players = crud.get_players(db_session, first_name="Bryce", last_name="Young")
    assert len(players) == 1
    assert players[0].player_id == 2009

def test_get_all_performances(db_session):
    """Tests that the count of performances in the database is what is expected - all performances"""
    performances = crud.get_performances(db_session, skip=0, limit=18000)
    assert len(performances) == 17306

def test_get_new_performances(db_session):
    """Tests that the count of performacnes int he database is what is expected"""
    performances = crud.get_performances(db_session, skip=0, limit=18000, min_last_changed_date=test_date)
    assert len(performances) == 2711

def test_getLeague(db_session):
    """Tests that you can get the first league"""
    league = crud.get_league(db_session, league_id = 5001)
    assert league.league_id == 5001

def test_get_leagues_by_name(db_session):
    """Tests that you can get a league by name"""
    leagues = crud.get_leagues(db_session, league_name="Pigskin Prodigal Fantasy League")
    assert len(leagues) == 1
    assert leagues[0].league_id == 5001

def test_get_teams(db_session):
    """Tests that the count of teams in the database is what is expected"""
    teams = crud.get_teams(db_session, skip=0, limit = 500)
    assert len(teams) == 20

#test the count functions
def test_get_player_counts(db_session):
    player_count = crud.get_player_count(db_session)
    assert player_count == 1018