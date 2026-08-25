# WriteMe

Send doodles to my receipt printer

## Development

### Dependencies

Install dependencies:

```sh
scripts/install-dependencies.sh
```

Upgrade pinned Python dependencies:

```sh
scripts/upgrade-pinned-dependencies.sh
```

## Service

### Local Development

Build and run locally:

```bash
./scripts/build-service.sh -s
```

Hosted at [http://localhost:9449](http://localhost:9449).

Reset data:

```
docker container prune
docker volume rm writeme_writeme_data
```
