# WriteMe

Send doodles to my receipt printer

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
