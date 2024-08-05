#!python3
r""" scrape.py - Initialize the database

Initialize the database schema
Parse the session data at https://ceol.io/sessions/austin/mueller
Populate the database with the parsed data

Dependencies
    py -m pip install requests
    py -m pip install bs4
    https://git-lfs.com/ - follow instructions to download and install
    cd %YOUR_CODE_ROOT% && git clone https://github.com/adactio/TheSession-data

"""
import argparse
import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import pathlib
import sys
import re
from datetime import datetime, time


re_session_url = re.compile(r'\d')
def ceol_session_info_tuples(ceol_url):
    """
    Yields information for each session url from https://ceol.io/sessions/austin/mueller/
    """
    # Define start and end times, these are hard coded for this set of sessions.
    location_id = 1
    start_time = time(19, 0)  # 7:00 PM
    end_time = time(22, 30)   # 10:30 PM
    session_description = "B.D.Riley Thursday Session at Mueller in Austin, Texas."

    response = requests.get(ceol_url)
    if response.status_code != 200:
        print(f"Failed to retrieve content from {ceol_url}. Status code: {response.status_code}")
        return
    soup = BeautifulSoup(response.content, 'html.parser')
    for a_tag in soup.find_all('a'):
        href = a_tag.get("href")
        try:
            session_date = datetime.strptime(href.split(".")[0], '%Y-%m-%d')
        except ValueError:
            continue
        session_url = ceol_url + href
        yield session_url, location_id, session_date, start_time, end_time, session_description


def ceol_tune_info_tuplets(session_url):
    """
    Yields tune information for each session at mueller https://ceol.io/sessions/austin/mueller/{session_date}.html
    """
    response = requests.get(session_url)
    if response.status_code != 200:
        print(f"Failed to retrieve content from {ceol_url}. Status code: {response.status_code}")
        return
    soup = BeautifulSoup(response.content, 'html.parser')
    set_index = 1
    for li in soup.find_all('li'):
        for a_tag in li.find_all('a'):
            tune_name = a_tag.text
            tune_url = a_tag.get("href")
            tune_id = tune_url.split("#")[0].split('/')[-1]
            set_index
            yield tune_name, tune_id, set_index, tune_url
        set_index += 1


def parse():
    current_script_path = pathlib.Path(__file__).resolve()
    repo_root = current_script_path.parent.parent.parent
    code_root = repo_root.parent
    #print(f"{current_script_path=}, {repo_root=} {code_root=}")
    parser = argparse.ArgumentParser(
        description="Extract URLs from <a> tags on a given HTML page.")
    parser.add_argument(
        "--url",
        type=str,
        default="https://ceol.io/sessions/austin/mueller/",
        help="URL of the HTML page to parse")
    parser.add_argument(
        "--db_file",
        type=pathlib.Path,
        default=repo_root / "mueller.db",
        help="The file of the database to write to")
    parser.add_argument(
        "--schema_file",
        type=pathlib.Path,
        default=repo_root / "init.sql",
        help="Filepath for a file containing the SQL commands that initialize the database")
    parser.add_argument(
        "--session_db",
        type=pathlib.Path,
        default=code_root / "TheSession-data" / "thesession.db",
        help="Filepath for a file containing the SQL commands that initialize the database")
    # newrel: consider validating these args or possibly making the output_dir
    # if it does not exist
    return parser.parse_args()


def main():
    args = parse()
    print(args)

    with sqlite3.connect(args.db_file) as conn:
        cursor = conn.cursor()

        # Read the schema file
        with open(args.schema_file, 'r') as f:
            schema = f.read()
            # Execute the SQL commands
            cursor.executescript(schema)

        with sqlite3.connect(args.session_db) as session_conn:
            session_cursor = session_conn.cursor()

            for session_url, location_id, session_date, start_time, end_time, session_description in ceol_session_info_tuples(args.url):
                print(f"{session_url=}, {location_id=}, {session_date=}, {start_time=}, {end_time=}, {session_description=}")
                cursor.execute(
                    "INSERT INTO Session (location_id, session_date, start_time, end_time, description) VALUES (?, date(?), ?, ?, ?)",
                    (
                        location_id,
                        session_date.strftime('%Y-%m-%d'),
                        start_time.strftime('%H:%M:%S'),
                        end_time.strftime('%H:%M:%S'),
                        session_description))
                session_id = cursor.lastrowid
                index = 1
                set_names = []
                set_tune_ids = []
                for tune_name, tune_id, set_index, tune_url in ceol_tune_info_tuplets(session_url):
                    if set_index != index:
                        index = set_index
                        set_description = ','.join(set_names)
                        cursor.execute('SELECT set_id FROM SetTable WHERE description = ?', (set_description,))
                        result = cursor.fetchone()
                        set_id = 0
                        if not result:
                            cursor.execute('INSERT INTO SetTable (description) VALUES (?)', (set_description,))
                            set_id = cursor.lastrowid
                        else:
                            set_id = result[0]

                        for i in range(len(set_tune_ids)):
                            cursor.execute('INSERT INTO TuneToSet (tune_id, set_id, tune_index) VALUES (?, ?, ?)', (set_tune_ids[i], set_id, i + 1))
                        cursor.execute('INSERT INTO SetToSession (session_id, set_id, set_index) VALUES (?, ?, ?)', (session_id, set_id, index))
                        set_names = []
                        set_tune_ids = []

                    abc = ""
                    tune_type = ""
                    tune_meter = ""
                    mode = ""

                    session_cursor.execute('SELECT abc, type, meter, mode  FROM tunes WHERE tune_id = ?', (tune_id,))
                    abc_result = session_cursor.fetchone()
                    if abc_result:
                        abc, tune_type, tune_meter, mode = abc_result

                    set_names.append(tune_name)
                    cursor.execute("SELECT tune_id FROM Tune WHERE name = ?", (tune_name,))
                    result = cursor.fetchone()
                    if result:
                        set_tune_ids.append(result[0])
                        continue

                    cursor.execute('INSERT INTO Tune (name, abc, tune_type, tune_mode, tune_meter, session_url) VALUES (?, ?, ?, ?, ?, ?)', 
                                   (tune_name, abc, tune_type, mode, tune_meter, tune_url))
                    set_tune_ids.append(cursor.lastrowid)
                set_description = ','.join(set_names)
                cursor.execute('SELECT set_id FROM SetTable WHERE description = ?', (set_description,))
                result = cursor.fetchone()
                set_id = 0
                if not result:
                    cursor.execute('INSERT INTO SetTable (description) VALUES (?)', (set_description,))
                    set_id = cursor.lastrowid
                else:
                    set_id = result[0]

                for i in range(len(set_tune_ids)):
                    cursor.execute('INSERT INTO TuneToSet (tune_id, set_id, tune_index) VALUES (?, ?, ?)', (set_tune_ids[i], set_id, i + 1))
                cursor.execute('INSERT INTO SetToSession (session_id, set_id, set_index) VALUES (?, ?, ?)', (session_id, set_id, index))


                break


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
