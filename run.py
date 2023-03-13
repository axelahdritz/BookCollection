import csv
import os
import json
import pandas as pd
import scripts.InternetArchive as InternetArchive
import scripts.LitteraturBanken as LitteraturBanken
from pathlib import Path

with open('test.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    for row in reader:
        directory_name = '_'.join([row[6], row[7], row[8]])
        initial_directory = '/Users/axelahdritz/coding_projects/BookCollection/Books/{d}/'.format(d=directory_name)
        save_to_directory_swe = '/Users/axelahdritz/coding_projects/BookCollection/Books/{d}/swe/'.format(d=directory_name)
        save_to_directory_eng = '/Users/axelahdritz/coding_projects/BookCollection/Books/{d}/eng/'.format(d=directory_name)
        swedish_filename = save_to_directory_swe + row[7] + '.json'
        english_filename = save_to_directory_eng + row[8] + '.json'
        is_pdf_var = row[0].rsplit('/', 1)[-1]
        if is_pdf_var == 'etext':
            is_pdf = 0
        else:
            is_pdf = 1
        if not Path(initial_directory).exists():
            os.mkdir(initial_directory)
        if not Path(save_to_directory_swe).exists():
            os.mkdir(save_to_directory_swe)
        if not Path(save_to_directory_eng).exists():
            os.mkdir(save_to_directory_eng)

        print('STARTING ENGLISH FILE:')
        print(directory_name)
        print("==============================")
        # extract English text
        eng = InternetArchive.InternetArchiveBook(row[3],
                                                  int(row[4]), 
                                                  int(row[5]), 
                                                  int(row[9]),
                                                  int(row[10]),
                                                  int(row[11]))
        english_text = eng.main()

        json_list = json.dumps(english_text)

        with open(english_filename, 'w') as jsonfile:
            jsonfile.write(json_list)

        print('STARTING SWEDISH FILE:')
        print(directory_name)
        print("==============================")
        # extract Swedish text
        swe = LitteraturBanken.LitteraturBankenBook(row[0], 
                                                    int(row[1]), 
                                                    int(row[2]),
                                                    is_pdf)
        swedish_text = swe.main()

        json_list = json.dumps(swedish_text)

        with open(swedish_filename, 'w') as jsonfile:
            jsonfile.write(json_list)