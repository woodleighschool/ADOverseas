# ADOverseas

Install the dependencies, and start the server with `python3 server.py`, then send a test with curl:

```
curl -X POST http://localhost:5000/schedule \
     -H "Authorization: Bearer supersecrettoken" \
     -H "Content-Type: application/json" \
     -d '{
          "username": "teststudent",
          "start_date": "2023-08-09 14:25:00",
          "end_date": "2023-08-09 14:26:00"
         }'
```

ensure to change start_date and end_date accordingly
