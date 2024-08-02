import argparse
import requests
from bs4 import BeautifulSoup
import sqlite3
import os

def get_sessions(url, c):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        for a_tag in soup.find_all('a'):
            url = a_tag.get('href')
            if "thesession" not in url and "bd" not in url:
                time_7pm = "19:00:00"  # 7:00 PM in HH:MM:SS format
                time_1030pm = "22:30:00"  # 10:30 PM in HH:MM:SS format
                date_today = url.split(".")[0]
                timestamp_7pm = f"{date_today} {time_7pm}"
                timestamp_1030pm = f"{date_today} {time_1030pm}"
                c.execute("INSERT INTO Session (location_id, session_date, start_time, end_time, description) VALUES (1, date(?), ?, ?, '')", 
                          (date_today, timestamp_7pm, timestamp_1030pm))
    else:
        print(f"Failed to retrieve content from {url}. Status code: {response.status_code}")

def get_tunes(url,output_dir, c):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        for li in soup.find_all('li'):
            set_song_names = []
            set_song_ids = []
            for a_tag in li.find_all('a'):
                name = a_tag.text
                set_song_names.append(name)
                c.execute("SELECT 1 FROM Tune WHERE name = ?", (name,))
                result = c.fetchone()
                if not result:
                    abc_path = os.path.join(output_dir, name.replace(' ', '').replace('\'', '').lower() + ".abc")
                    href_str = a_tag.get("href")
                    download_url = ""
                    if '#' in href_str:
                        setting = int(href_str.split("#setting")[-1])
                        tune_id = int(href_str.split("#")[0].split("/")[-1])
                        download_url = href_str.split("#")[0] + "/abc"
                        if setting != tune_id:
                            download_url += "/2"
                        else:
                            download_url += "/1"
                    else:
                        download_url = href_str + "/abc/1"
                    key = ""
                    download_file(download_url, abc_path)
                    with open(abc_path, 'r') as f:
                        abc_lines = f.readlines()
                        for line in abc_lines:
                            if "K:" in line:
                                key = line.split(" ")[-1]
                                break
                    c.execute('INSERT INTO Tune (name, abc_path, key) VALUES (?, ?, ?)', (name, abc_path, key))
                    c.execute("SELECT tune_id FROM Tune WHERE name = ?", (name,))
                    tune_id = c.fetchone()
                    set_song_ids.append(tune_id[0])
            set_description = ','.join(set_song_names)
            c.execute('INSERT INTO SetTable (description) VALUES (?)', (set_description,))
            c.execute('SELECT set_id FROM SetTable WHERE description = ?', (set_description,))
            set_id = c.fetchone()[0]
            for i in range(len(set_song_ids)):
               c.execute('INSERT INTO TuneToSet (tune_id, set_id, tune_index) VALUES (?, ?, ?)', (set_song_ids[i], set_id, i + 1)) 

    else:
        print(f"Failed to retrieve content from {url}. Status code: {response.status_code}")

def download_file(url, filepath):
    try:
        response = requests.get(url, stream=True)
        
        if response.status_code == 200:
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"File downloaded successfully: {filepath}")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract URLs from <a> tags on a given HTML page.")
    parser.add_argument("url", type=str, help="URL of the HTML page to parse")
    parser.add_argument("db_file", type=str, help="The file of the database to write to")
    parser.add_argument("output_dir", type=str, help="Where to download abc files to")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db_file)
    c = conn.cursor()
    #get_sessions(args.url, c)
    get_tunes(args.url + "2020-03-12.html",args.output_dir, c)
    conn.commit()
    conn.close()
