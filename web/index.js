import { createServer } from "http";
import { readFileSync } from "fs";

const home = readFileSync('home.html', 'utf8');
const maintenance = readFileSync('maintenance.html', 'utf8');

const server = createServer((req, res) => {
  if (req.url === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(home);
  }
});

const [host, port] = process.env.AWS_LAMBDA_HTTP_ENDPOINT.split(':');

server.listen(port, host, () => {
  console.log(`Server running on ${host}:${port}`);
});
