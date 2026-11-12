import { createServer } from "http";
import { readFileSync } from "fs";
import { randomUUID } from "node:crypto";

const containerId = randomUUID();
const home = readFileSync('home.html', 'utf8');
const maintenance = readFileSync('maintenance.html', 'utf8');

const server = createServer((req, res) => {
  if (req.url === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(home);
  }

  else if (req.url === "/stream") {
    res.writeHead(200, {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache"
    });

    let count = 0;

    const interval = setInterval(() => {
      count++;

      res.write(`data: ${JSON.stringify({
        containerId,
        message: `Mensaje ${count}`,
        timestamp: new Date().toISOString()
      })}\n\n`);

      if (count === 5) {
        clearInterval(interval);
        res.end();
      }
    }, 1000);

    res.on("close", () => clearInterval(interval));
  }

  else {
    res.writeHead(404);
    res.end("Not found");
  }
});

const [host, port] = process.env.AWS_LAMBDA_HTTP_ENDPOINT.split(':');

server.listen(port, host, () => {
  console.log(`Server running on ${host}:${port}`);
});
