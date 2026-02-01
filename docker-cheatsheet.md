# Running Mailpit
To run Mailpit using Podman you can use the following command:

```
    podman run -d \
    --name mailpit \
    -p 8025:8025 \
    -p 1025:1025 \
    axllent/mailpit
```

or with Docker:

```
    docker run -d \
    --name mailpit \
    -p 8025:8025 \
    -p 1025:1025 \
    axllent/mailpit
```