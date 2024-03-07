# Service

## Infrastructure

Writeme is hosted as a Docker container behind the Caddy web server using a reverse proxy.

The production service is hosted on a DigitalOcean droplet and backups are achieved by enabling droplet backups.

## Deployment

Deployment is performed using an Ansible playbook located in the 'ansible' directory. This is automated using GitHub Actions and Environments. Environments are configured to expose the following details:

- Secrets
     - `ANSIBLE_BECOME_PASS`
     - `ANSIBLE_SSH_KEY`
- Variables
     - `SERVICE_DEPLOYMENT_GROUP`–one of 'staging' or 'production'
     - `SERVICE_ADDRESS`

There are currently two environments configured: 'staging' and 'production'.

## Logs

View the service logs on the server:

```bash
sudo journalctl -u writeme-service
```

Tail the logs:

```bash
sudo journalctl -u writeme-service -f
```

## Development

### Installing Dependencies

Writeme uses a shared script for installing and managing dependencies. Follow the instructions [here](/README.markdown#installing-dependencies).

### Running Locally

```bash
cd service
docker compose up --build
```

The database is exposed to the local machine as 'postgresql://hello_flask:hello_flask@localhost:54320/hello_flask_dev'.

### Tests

Tests can be run as follows:

```bash
scripts/tests-service.sh
```

This will install the tests' Python dependencies. Note that the tests expect the service to be running on localhost.

If you wish to build, run, and test, you can use the `build-service.sh` script:

```bash
scripts/build-service.sh --test
```

Sometimes, it can be quite useful to run individual unit tests. This can be done as follows:

```bash
cd service/tests
pipenv run python test_api.py --verbose TestAPI.test_index
```

The necessary environment variables that tell the tests where to find the service and database are stored in 'service/tests/.env'

### Command-line

It can sometimes be useful to make requests directly from the command-line during development. `curl` can be useful for this. For example,

```bash
curl --header "Content-Type: application/json" \
     --request POST \
     --data '{"token":"123456789"}' \
     http://127.0.0.1:9449/api/v3/device/
```

