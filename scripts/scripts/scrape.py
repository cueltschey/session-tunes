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
import os
import pathlib
import sys
import re
from datetime import datetime, time
import SessionDataManager


re_session_url = re.compile(r'\d')
def ceol_session_info_tuples(ceol_url):
    """
    Yields information for each session url from https://ceol.io/sessions/austin/mueller/
    (session_url, location_id, session_date, start_time, end_time)
    """
    # Define start and end times, these are hard coded for this set of sessions.
    location_id = 1
    start_time = time(19, 0)  # 7:00 PM
    end_time = time(22, 30)   # 10:30 PM

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
        yield session_url, location_id, session_date, start_time, end_time


def ceol_set_info_tuplets(session_url):
    """
    Yields tune information for each session at mueller https://ceol.io/sessions/austin/mueller/{session_date}.html
    (set_index, tunes) where tunes is a list of (tune_name, tune_id, tune_url)
    """
    response = requests.get(session_url)
    if response.status_code != 200:
        print(f"Failed to retrieve content from {session_url}. Status code: {response.status_code}")
        return
    soup = BeautifulSoup(response.content, 'html.parser')
    # Note that we will yield 1 based indexes because that matches what SQL does
    set_index = 0
    for li in soup.find_all('li'):
        set_index += 1
        tunes = list()
        for a_tag in li.find_all('a'):
            tune_name = a_tag.text
            tune_url = a_tag.get("href")
            tune_id = tune_url.split("#")[0].split('/')[-1]
            tunes.append((tune_name, tune_id, tune_url))
        yield set_index, tunes


def parse():
    current_script_path = pathlib.Path(__file__).resolve()
    repo_root = current_script_path.parent.parent.parent
    code_root = repo_root.parent
    #print(f"{current_script_path=}, {repo_root=} {code_root=}")
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--url",
        type=str,
        default="https://ceol.io/sessions/austin/mueller/",
        help="URL of the HTML page to parse")
    parser.add_argument(
        "--session_db",
        type=pathlib.Path,
        default=code_root / "TheSession-data" / "thesession.db",
        help="Filepath for a file containing the SQL commands that initialize the database")
    parser.add_argument(
        '--initialize_db',
        default=False,
        action=argparse.BooleanOptionalAction)
    return parser.parse_args()


def main():
    args = parse()
    print(args)

    with SessionDataManager.SessionDataManager(args.session_db, args.initialize_db) as sdm:
        for session_url, location_id, session_date, start_time, end_time in ceol_session_info_tuples(args.url):
            print(f"Create session: {session_url=}, {location_id=}, {session_date=}, {start_time=}, {end_time=}")
            session_id = sdm.create_session(
                location_id,
                session_date.strftime('%Y-%m-%d'),
                start_time.strftime('%H:%M:%S'),
                end_time.strftime('%H:%M:%S'),
                "")

            #(set_index, tunes) where tunes is a list of (tune_name, the_session_tune_id, tune_url)
            for set_index, tunes in ceol_set_info_tuplets(session_url):
                set_description = ', '.join([tune_name for tune_name, the_session_tune_id, tune_url in tunes])
                set_id = sdm.read_or_create_set(set_description)
                sdm.create_set_to_session(session_id, set_id, set_index)

                tune_number_in_set = 0
                for tune_name, the_session_tune_id, tune_url in tunes:
                    tune_number_in_set += 1
                    abc, tune_type, tune_meter, tune_mode = sdm.get_tune_from_TheSession(the_session_tune_id)
                    our_tune_id = sdm.get_id_or_create_tune(the_session_tune_id, tune_name, abc, tune_type, tune_meter, tune_mode, tune_url)
                    sdm.create_tune_to_set(our_tune_id, set_id, tune_number_in_set)


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
