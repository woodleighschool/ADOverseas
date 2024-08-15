# ADOverseas

Start the container with docker-compose:

```yaml
services:
  adoverseas:
    image: ghcr.io/woodleighschool/adoverseas
    container_name: adoverseas
    environment:
      - PUID=1002
      - PGID=1002
      - TZ=Australia/Melbourne
      - AD_USERNAME=
      - AD_PASSWORD=
      - API_TOKEN=
    volumes:
      - path_to_appdata/config
    ports:
      - 3500:3500
    restart: unless-stopped
```

```bash
curl -X POST http://localhost:3500/schedule \
     -H "Authorization: Bearer supersecrettoken" \
     -H "Content-Type: application/json" \
     -d '{
          "username": "teststudent",
          "start_date": "2023-08-09 14:25:00",
          "end_date": "2023-08-09 14:26:00"
         }'
```

ensure to change start_date and end_date accordingly
