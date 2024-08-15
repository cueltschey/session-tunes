import SessionDataManager
import pathlib
import argparse
from audio import AudioManager
import sys

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
    parser.add_argument(
        "--soundfont_file",
        type=pathlib.Path,
        default=repo_root / "soundfonts" / "Tabla.sf2",
        help="The SoundFont File to create audio from ABC notation")
    return parser.parse_args()


def main():
    args = parse()
    print(args)

    with SessionDataManager.SessionDataManager(args.db_file, args.schema_file, args.session_db, initialize_db=False) as sdm:
        audio_manager = AudioManager()
        _, _, name, abc, tune_type, tune_meter, tune_mode, _ = sdm.read_tune(113)
        audio_manager.create_audio_converter(1, name, tune_meter, tune_mode, abc)
        audio_manager.write_wav("test.wav", str(args.soundfont_file))

if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
