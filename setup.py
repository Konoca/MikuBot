import os
import json

files = {
    'profile': {
        'status': {},
        'status_history': []
    },
    'moderators': {
        'admins': [],
        'mods': []
    },
    'changelogs': [
        {
            'version': '',
            'date': '',
            'changes': []
        }
    ]
}


def create_file(file_name, file_contents):
    if os.path.exists(f'./data/{file_name}.json'):
        print(f'{file_name}.json already exists, skipping...')
        return

    with open(f'./data/{file_name}.json', 'w') as f:
        f.write(json.dumps(file_contents, indent=4))


def create_jsons():
    if not os.path.exists('./data'):
        os.mkdir('./data')

    for key, value in files.items():
        print(f'Creating {key}.json')
        create_file(key, value)


def create_env():
    if os.path.exists('./.env'):
        print('.env already exists, skipping...')
        return

    token = input('Bot token: ')
    prefix = input('Bot prefix: ')

    with open('./.env', 'w') as f:
        f.write(f'TOKEN={token}\n')
        f.write(f'PREFIX={prefix}\n')


def main():
    create_jsons()
    create_env()


if __name__ == '__main__':
    main()
