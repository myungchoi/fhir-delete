import requests as requests

g_url = 'https://heat.icl.gtri.org/hapi-fhir-public/fhir'
basic_user = 'user'
basic_password = 'password'


def collect_resource_ids(entry):
    ids = []
    for item in entry:
        resource = item['resource']
        ids.append(resource['id'])

    return ids


def search_fhir(url):
    ids = []
    headers = {'Content-Type': 'application/json'}
    r = requests.get(url, headers=headers, auth=(basic_user, basic_password))
    if r.status_code != 200:
        print('Search Failed with URL = {}'.format(url))
        return ids

    bundle = r.json()
    if bundle.get('link') is not None:
        for link in bundle['link']:
            if link['relation'] == 'next':
                ids.extend(search_fhir(link['url']))

    if bundle.get('entry') is not None:
        ids.extend(collect_resource_ids(bundle['entry']))

    return ids


def delete_resource(url):
    r = requests.delete(url, auth=(basic_user, basic_password))
    print ('Delete {} with status {}'.format(url, r.status_code))


if __name__ == '__main__':
    system = 'http://hospital.smarthealthit.org'
    value = '139c7815-7842-419a-9f97-f406a66c06df'
    search_url = '{}/Patient?identifier={}|{}'.format(g_url, system, value)
    patients = search_fhir(search_url)

    print('Patients found:')
    print(patients)

    # observations and service requests
    observations = []
    service_requests = []
    for id in patients:
        search_url = '{}/Observation?subject=Patient/{}'.format(g_url, id)
        observations.extend(search_fhir(search_url))
        search_url = '{}/ServiceRequest?subject=Patient/{}'.format(g_url,id)
        service_requests.extend(search_fhir(search_url))

    print('Observations found:')
    print(observations)

    # ServiceRequest
    print('ServiceRequests found:')
    print(service_requests)

    tasks = []
    for id in service_requests:
        url = '{}/Task?focus=ServiceRequest/{}'.format(g_url, id)
        tasks.extend(search_fhir(url))

    print('Tasks found:')
    print(tasks)

    message_headers = []
    for id in tasks:
        url = '{}/MessageHeader?focus=Task/{}'.format(g_url, id)
        message_headers.extend(search_fhir(url))

    print('MessageHeaders found:')
    print(message_headers)

    message_bundles = []
    for id in message_headers:
        url = '{}/Bundle?message=MessageHeader/{}'.format(g_url, id)
        message_bundles.extend(search_fhir(url))

    print('Message Bundles found:')
    print(message_bundles)

    # Deletes
    # Delete observations
    for id in observations:
        delete_url = '{}/Observation/{}'.format(g_url, id)
        delete_resource(delete_url)

    for id in message_bundles:
        delete_url = '{}/Bundle/{}'.format(g_url, id)
        delete_resource(delete_url)

    for id in message_headers:
        delete_url = '{}/MessageHeader/{}'.format(g_url, id)
        delete_resource(delete_url)

    for id in tasks:
        delete_url = '{}/Task/{}'.format(g_url, id)
        delete_resource(delete_url)

    for id in service_requests:
        delete_url = '{}/ServiceRequest/{}'.format(g_url, id)
        delete_resource(delete_url)

    for id in patients:
        delete_url = '{}/Patient/{}'.format(g_url, id)
        delete_resource(delete_url)

