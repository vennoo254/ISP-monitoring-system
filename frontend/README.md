Simple static frontend demo page that shows monitored targets, three sample charts (latency, packet loss, jitter) and real-time alerts via WebSocket.

How to open
1. Ensure the node notifier service is running and listening on port 4000 (or edit the port in the page).
2. From the repository root run a simple static server in the frontend directory, for example:
   - python3 -m http.server 8080 --directory frontend
   or
   - npx http-server frontend
3. Open http://localhost:8080/index.html in your browser.

Notes
- The page connects to ws://<host>:4000/ to receive alert broadcasts from the node notification service included in the project. If you run the Node service in Docker Compose on the same machine, the page will reach ws://localhost:4000/.
- To test alerts quickly you can POST to the node notifier:
  curl -X POST http://localhost:4000/alert -H 'Content-Type: application/json' -d '{"target":"8.8.8.8","metric":"latency","value":250}'
- The charts shown are sample data (randomized) to illustrate interface layout. You can wire them to InfluxDB queries or a metrics websocket later.
