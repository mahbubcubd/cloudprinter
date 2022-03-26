import requests
import requests as rq
import os
import time
import cups

print("Connecting Printer...", end='')
conn = cups.Connection()
printers = conn.getPrinters()
printer_name = list(printers.keys())[0]
print(f'print {printer_name} CONNECTED')

host = 'http://192.168.0.101:5001/'

while True:
    print("Getting New documents from cloud documents queue...", end='')
    response = rq.get(host+'doc_to_print').json()
    print(f'found {len(response)} requests')

    if len(response) > 0:

        print("Processing cloud printing requests...")
        for data in response:
            src = data['src']
            splitter = src.split('/')
            dir_locs = '/'.join(splitter[2:-1])
            os.makedirs(dir_locs, exist_ok=True)
            file_name = splitter[-1]
            file_url = host + src
            os.system(f'wget {file_url} -O {"/".join(splitter[2:])}')

            # Set Print Options
            print_options = {"copies": str(data['copies'])}
            pages = data['pages']

            if pages != 'all':
                if pages in ['odd', 'even']:
                    print_options['page-set'] = pages
                else:
                    print_options['pages'] = pages

            print(f"SUMMERY\n~~~~~~~\nfilename: {file_name}\ncopies: {data['copies']}\npage rages: {data['pages']}")
            print_id = conn.printFile(
                printer_name,
                f'/home/pi/cloudprinter/{"/".join(splitter[2:])}',
                "", print_options)

            print(f'Printing file {file_name}...waiting to finish...', end='')
            while conn.getJobs().get(print_id, None) is not None:
                time.sleep(1)
            print('COMPLETED')
            print('Updating cloud print status...', end='')
            resp = requests.post(host+'print_success', json=dict(task_id=data['id']))
            if resp.status_code in [200, 201]:
                print('updated')
            else:
                print('failed')
    else:
        print('No Task to print')

    print('Taking 10 second rest')
    time.sleep(10)

