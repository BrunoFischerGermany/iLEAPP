__artifacts_v2__ = {
    "get_sysdiag_account_devices": {
        "name": "Sysdiagnose - Account Devices",
        "description": "Parses the otctl_status.txt file from Sysdiagnose logs, to get informations about other devices connected to the same Apple-ID.",
        "author": "@C_Peter",
        "version": "0.1",
        "creation_date": "2025-05-22",
        "last_update_date": "2025-05-22",
        "requirements": "none",
        "category": "Sysdiagnose",
        "notes": "OCTL refers to the Octagon Account (iCloud Keychain)",
        "paths": ('*/otctl_status.txt','*/mobile/Library/Logs/CrashReporter/DiagnosticLogs/sysdiagnose/sysdiagnose_*.tar.gz'),
        "output_types": "standard",
        "artifact_icon": "smartphone"
    }
}

import json
import tarfile
import os
import scripts.builds_ids as builds_ids

from scripts.ilapfuncs import artifact_processor, get_file_path

@artifact_processor
def get_sysdiag_account_devices(files_found, report_folder, seeker, wrap_text, timezone_offset):

    data_list = []
    sources = []
    for file_found in files_found:
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        if filename == "otctl_status.txt":
            source_path = get_file_path(files_found, 'otctl_status.txt')
            print(f"File: {source_path} found.")
            with open(source_path, 'r', encoding='utf-8') as otctl:
                f = json.load(otctl)
        elif "sysdiagnose_" in filename and not "IN_PROGRESS_" in filename:
            print(f"File: {filename} found.")
            source_path = get_file_path(files_found, filename)
            tar = tarfile.open(source_path)
            root = tar.getmembers()[0].name.split('/')[0]
            try:
                tarf = tar.extractfile(f"{root}/otctl_status.txt")
                f = json.load(tarf)
            except:
                continue
        else:
            continue
        sources.append(source_path)
        opush = f["lastOctagonPush"]

        for elem in f["contextDump"]["peers"]:
            model = elem["permanentInfo"]["model_id"]
            m_name = builds_ids.device_id.get(model, model)
            os_bnum = elem["stableInfo"]["os_version"]
            os_build = os_bnum.split('(')[1].split(')')[0]
            os_ver = builds_ids.OS_build.get(os_build, os_build)
            serial = elem["stableInfo"]["serial_number"]
            if not any(serial in subliste for subliste in data_list):
                data_list.append((opush, model, m_name, os_bnum, os_ver, serial))
    source_list = "; ".join(s for s in sources)
    data_headers = (
        "lastOctagonPush", "Model", "Product", "OS Build", "OS Version", "Serial Number")
    return data_headers, data_list, source_list