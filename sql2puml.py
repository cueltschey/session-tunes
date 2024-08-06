#!python3
r""" sql2puml.py - Convert SQL Schema to PlantUml Diagram


Dependencies

"""
import argparse
import pathlib
import sys
import requests

puml_template = """@startuml
!define table(x) class x << (T,#FFAAAA) >>
!define primary_key(x) <color:red>◆</color> x
!define foreign_key(x) <color:blue>◇</color> x

hide methods
hide stereotypes
skinparam classFontColor red
skinparam classAttributeIconSize 0
skinparam defaultFontName Courier

table(Session) {
    primary_key(session_id):  INTEGER
    foreign_key(location_id): INTEGER
    session_date:  DATE
    start_time:    TIMESTAMP
    end_time:      TIMESTAMP
    description:   TEXT
}

table(SetToSession) {
    foreign_key(session_id): INTEGER
    foreign_key(set_id):     INTEGER
    set_index:    INTEGER
}

table(Location) {
    primary_key(location_id): INTEGER
    description:   TEXT
    address:       VARCHAR_255
    url:           VARCHAR_255
}

table(SetTable) {
    primary_key(set_id):    INTEGER
    description: TEXT
}

table(TuneToSet) {
    foreign_key(tune_id): INTEGER
    foreign_key(set_id):  INTEGER
    tune_index:INTEGER
}

table(Tune) {
    primary_key(tune_id): INTEGER
    name:      VARCHAR_255
    abc_path:  VARCHAR_255
    key:       VARCHAR_255
}

Session::location_id --o Location::location_id
Session::session_id o- SetToSession::session_id
SetToSession::set_id -o SetTable::set_id
SetTable::set_id o- TuneToSet::set_id
TuneToSet::tune_id --o Tune::tune_id

@enduml
"""

def parse():
    current_script_path = pathlib.Path(__file__).resolve()
    current_script_dir = current_script_path.parent
    print(f"{current_script_path=}, {current_script_dir=}")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sql_file",
        type=pathlib.Path,
        default=current_script_dir / "init.sql",
        help="Filepath to the file containing the SQL commands that implement the database schema")
    parser.add_argument(
        "--puml_file",
        type=pathlib.Path,
        default=current_script_dir / "schema.puml",
        help="Filepath to the PlantUml that will be written")
    parser.add_argument(
        "--svg_file",
        type=pathlib.Path,
        default=current_script_dir / "schema.svg",
        help="Filepath to the SVG file that will be written")
    return parser.parse_args()


def main():
    args = parse()
    print(args)

    with args.puml_file.open('w', encoding='utf-8') as f:
        f.write(puml_template)


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
