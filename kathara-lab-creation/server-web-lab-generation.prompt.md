# Prompt: Generate a Client–Web Server–Wireshark Lab

Act as a senior network-lab author with practical experience in Kathara, Linux
networking, HTTP services, and packet capture.

## Goal

Generate a complete, self-contained lab based on the reference image named
`.Server web`. The lab must contain exactly these three logical devices:

1. `client`
2. `server`
3. `wireshark`

The client must reach an HTTP service on the server. The server must return an
HTML page whose visible body says exactly:

```text
hello
```

The Wireshark device or capture component must be able to observe and record the
HTTP exchange between the client and server.

## Reference-image rules

- Treat the `.Server web` image as the visual source of truth for device names,
  device roles, links, relative layout, and any addresses or interface labels
  that are legible in it.
- Preserve the reference topology unless a small technical adjustment is
  required to make packet capture work.
- Do not add routers, switches represented as managed devices, services, or
  unrelated hosts that are not required by the reference or by functional
  packet capture.
- If a label in the image is unreadable or a necessary value is absent, use the
  defaults in this prompt.
- If a textual requirement here conflicts with a purely decorative detail in
  the image, prioritize functional correctness and document the deviation in
  the lab README.

## Default topology and addressing

Use these values when the reference image does not specify alternatives:

| Device | Interface | IPv4 address | Role |
|---|---|---:|---|
| `client` | `eth0` | `10.10.0.2/24` | HTTP client |
| `server` | `eth0` | `10.10.0.3/24` | HTTP server |
| `wireshark` | `eth0` or capture-facing interfaces | `10.10.0.4/24` if an address is needed | Packet observer |

The client and server must have direct IP connectivity without requiring
Internet access. A default route is unnecessary unless the reference topology
requires one.

Prefer a single shared collision domain if it allows the Wireshark component to
see the complete unicast exchange. Do not merely assume that promiscuous mode is
enough on a switched virtual network: verify that the capture contains both the
client request and server response. If the lab platform does not expose unicast
traffic to a third passive interface, use the least intrusive supported
solution, such as port mirroring or an inline transparent capture bridge. Keep
the same three logical devices and explain the implementation briefly in the
README.

## Web-server requirements

- Use the server/web image indicated by `.Server web`. Preserve its exact image
  name or tag when it is visible in the reference.
- If the reference does not provide an image name, select a stable image already
  appropriate for the lab platform and containing the required web service.
- Do not download packages during lab startup.
- Serve plain HTTP on TCP port `80`.
- Start the web service automatically and idempotently when the lab starts.
- Ensure the service remains running after the startup script finishes.
- Provide a valid minimal HTML5 document.
- The rendered page must visibly contain only the lower-case word `hello`
  (surrounding HTML structure and insignificant whitespace are allowed).
- A request to `http://10.10.0.3/` must return HTTP status `200`.
- The response should use an HTML content type.
- Do not add JavaScript, external assets, analytics, or unnecessary styling.

A suitable page is semantically equivalent to:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Hello</title>
  </head>
  <body>hello</body>
</html>
```

Place the file in the actual document root used by the chosen server image.
Do not assume a document root without checking the image/service convention.

## Client requirements

- Configure the client address automatically at lab startup.
- Provide at least one available command for testing the site, preferably
  `curl`; `wget` is acceptable if that is what the selected image includes.
- Include the exact manual verification command in the README.
- Do not make continuous traffic generation mandatory.
- If a one-time automatic HTTP request is used to seed the capture, wait until
  the server is ready, use a bounded retry loop, and write useful failure output.

## Wireshark and capture requirements

- Configure the capture interface or interfaces automatically.
- Enable promiscuous mode where relevant.
- Use Wireshark CLI tooling such as `tshark` or `dumpcap` when available.
  `tcpdump` may be used as a compatibility fallback, but the resulting file
  must be a standard `.pcap` or `.pcapng` file readable by Wireshark.
- Capture at least ARP and the HTTP traffic on TCP port `80`; a capture filter
  limited to `arp or tcp port 80` is appropriate.
- Start long-running capture commands in the background so startup completes.
- Save the runtime capture with a clear name such as `http.pcap` or
  `http.pcapng`.
- Store the capture in a host-accessible/persistent lab location when the
  platform supports it. Otherwise, document the exact command needed to copy or
  open it.
- Do not commit a fabricated or pre-recorded packet capture. The capture must be
  produced by the running lab.
- Confirm during validation that the capture contains:
  - the TCP connection between client and server;
  - an HTTP request for `/`; and
  - the server response carrying the `hello` page.

If a graphical Wireshark session is not practical inside the container, use
headless capture and explain how to open the resulting file in the host
Wireshark application. The absence of an in-container GUI must not prevent the
lab from meeting its capture objective.

## Files to generate

Create one new, clearly named lab directory, for example:

```text
server-web-wireshark/
```

Within it, generate only the files required by the selected lab platform. For a
Kathara lab, this normally includes:

```text
server-web-wireshark/
├── lab.conf
├── client.startup
├── server.startup
├── wireshark.startup
├── server/
│   └── ... web document-root path .../
│       └── index.html
├── captures/
│   └── .gitkeep
└── README.md
```

Adjust the overlay path and capture directory only when required by the chosen
images or Kathara mount behavior. Keep configuration simple and readable.

All shell startup files must:

- use POSIX-compatible syntax unless the selected image explicitly provides a
  different shell;
- be safe to run more than once;
- fail meaningfully for critical setup errors;
- avoid interactive prompts;
- avoid package installation and Internet dependencies; and
- avoid leaving a required service in a blocking foreground command.

The lab configuration must explicitly define every device, interface attachment,
and non-default image required for reproducible startup.

## README requirements

Write a concise but complete `README.md` containing:

1. the purpose of the lab;
2. a small topology diagram, preferably Mermaid or ASCII;
3. an addressing table;
4. prerequisites, including the tested lab platform;
5. exact start and stop/cleanup commands;
6. the command to open a shell on the client;
7. the exact command to request the page;
8. the expected HTTP status and body;
9. how capture starts and where its output is saved;
10. how to stop/flush the capture safely before opening it;
11. how to inspect the HTTP request and response in Wireshark or `tshark`;
12. any justified difference from the `.Server web` reference image; and
13. a short troubleshooting section for failed connectivity, a stopped web
    service, an empty capture, or missing unicast packets.

## Validation

After generating the files, perform an end-to-end validation rather than only a
static review:

1. Validate the lab configuration and startup-script syntax.
2. Start the lab with the platform's normal command.
3. Wait for startup with a finite timeout.
4. From `client`, ping the server address.
5. From `client`, make an HTTP request to `http://10.10.0.3/`.
6. Verify HTTP status `200`.
7. Verify that the normalized response body is exactly `hello`.
8. Stop or flush the capture cleanly.
9. Read the capture with `tshark` or another non-interactive parser.
10. Verify it includes the request for `/` and the corresponding server
    response, not merely ARP or ping traffic.
11. Stop and clean up the lab.

If the runtime is unavailable, still complete all static checks and clearly
label the runtime checks as unperformed. Do not claim a test passed without
evidence.

## Quality constraints

- Keep the result minimal, deterministic, and suitable for a teaching lab.
- Prefer explicit static configuration over hidden defaults.
- Do not hard-code timing with a single fragile sleep when a bounded readiness
  check can be used.
- Do not expose services beyond what the lab needs.
- Do not use HTTPS, DNS, DHCP, routing daemons, or extra protocols unless they
  are visibly required by the reference image.
- Do not modify existing labs or unrelated workspace files.
- Do not overwrite user work.
- Report the generated directory, key implementation choices, commands/tests
  run, and any remaining limitations when finished.

## Acceptance criteria

The result is complete only when all of the following are true:

- The lab starts without interactive setup.
- Exactly three logical devices exist: `client`, `server`, and `wireshark`.
- The client reaches the server using the configured IPv4 address.
- `GET /` returns status `200` and an HTML page visibly saying `hello`.
- The capture is readable by Wireshark and contains both sides of that HTTP
  exchange.
- Startup scripts terminate successfully while required background services
  continue running.
- The README allows another user to start, test, inspect, and clean up the lab
  without guessing.
