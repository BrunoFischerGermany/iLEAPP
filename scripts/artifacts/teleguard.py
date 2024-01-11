import sqlite3
import json
import plistlib
import os
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, media_to_html

def get_teleguard(files_found, report_folder, seeker, wrap_text, time_offset):
    
    #datos =  seeker.search('**/*com.apple.mobile_container_manager.metadata.plist')
    for file_foundm in files_found:
        if file_foundm.endswith('.com.apple.mobile_container_manager.metadata.plist'):
            with open(file_foundm, 'rb') as f:
                pl = plistlib.load(f)
                if pl['MCMMetadataIdentifier'] == 'ch.swisscows.messenger.teleguardapp':
                    fulldir = (os.path.dirname(file_foundm))
                    identifier = (os.path.basename(fulldir))
                    mediafilepaths = seeker.search(f'*/{identifier}/Library/Caches/images/**')
                    break
                    
    for file_found in files_found:
        if file_found.endswith('teleguard_database.db'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
                SELECT
                datetime(createDate/1000, 'unixepoch'),
                datetime(userTime/1000, 'unixepoch'),
                type,
                sender,
                receiver,
                content,
                metadata,
                status,
                isEdited
                from messages
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Teleguard Messages')
                report.start_artifact_report(report_folder, 'Teleguard Messages')
                report.add_script()
                data_headers = ('Timestamp', 'User Time', 'Type', 'Sender','Receiver','Content','Media','Status','Is Edited?')
                data_list = []
                for row in all_rows:
                    if row[2] == 'MEDIA':
                        mediainfo = row[6]
                        mediainfo = json.loads(mediainfo)
                        mediafiles = mediainfo.get('files','')
                        if mediafiles != '':
                            thumb = ''
                            for key, values in mediafiles.items():
                                #print(key,values)
                                thumb = thumb + media_to_html(key, mediafilepaths, report_folder)
                                thumb = thumb + f'<br>{values}</br><br></br>'
                        else:
                            thumb = ''
                    else:
                        thumb = row[6]
                            
                    
                    
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], thumb, row[7], row[8]))
        
                report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                report.end_artifact_report()
                
                tsvname = f'Teleguard Messages'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'Teleguard Messages'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Teleguard Messages data available')
    
    #db.close()

__artifacts__ = {
        "Teleguard": (
                "Teleguard",
                ('*/Shared/AppGroup/*/Library/teleguard_database.db*','*/.com.apple.mobile_container_manager.metadata.plist'),
                get_teleguard)
}