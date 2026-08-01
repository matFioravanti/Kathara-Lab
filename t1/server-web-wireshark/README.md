# Client, Web Server, and Wireshark Lab

This Kathara teaching lab demonstrates a plain HTTP exchange. The `client`
requests a minimal page from an Apache `server`, while the device named
`wireshark` records the request and response in a Wireshark-readable packet
capture. The page visibly contains only the word `hello`.

## Topology

```text
                         transparent bridge
 client eth0 ── client_capture ── eth0 [ wireshark ] eth1 ── capture_server ── eth0 server
 10.10.0.2/24                         br0 10.10.0.4/24                         10.10.0.3/24
```

| Device | Interface | Address | Function |
|---|---|---|---|
| `client` | `eth0` | `10.10.0.2/24` | HTTP client |
| `wireshark` | `br0` over `eth0` and `eth1` | `10.10.0.4/24` | Transparent bridge and packet capture |
| `server` | `eth0` | `10.10.0.3/24` | Apache HTTP server |

The reference `.Server web` image was not stored with the lab files. The
three requested logical devices and their roles are preserved. The capture
device is placed inline as a transparent bridge so that it reliably observes
unicast client/server traffic even when the underlying virtual collision
domains perform switching.

## Prerequisites

- Kathara with a working container manager
- The `kathara/core:latest` and `kathara/apache:latest` images
- Wireshark on the host to inspect the graphical capture, or `tcpdump` for a
  command-line inspection

From this directory, check the local environment:

```sh
kathara check
```

## Start the lab

Run:

```sh
kathara lstart
```

The startup files assign all addresses, create the transparent bridge, start
Apache with `systemctl`, and start a background `tcpdump` process. The capture
filter records ARP plus TCP port 80 traffic.

Inspect the running devices with:

```sh
kathara linfo
```

## Request the page

Open a client shell:

```sh
kathara connect client
```

Then run:

```sh
curl -i http://10.10.0.3/
```

Alternatively, run the request without opening an interactive shell:

```sh
kathara exec client -- curl -i http://10.10.0.3/
```

The expected result is HTTP status `200`, an HTML content type, and an HTML
document whose visible body is:

```text
hello
```

A compact body-only check is:

```sh
kathara exec client -- curl -fsS http://10.10.0.3/
```

## Inspect the capture

The capture starts automatically and is written to:

```text
shared/http.pcap
```

Before opening the file, stop and flush the capture cleanly:

```sh
kathara exec wireshark -- /usr/local/bin/stop-http-capture
```

Open `shared/http.pcap` in the host Wireshark application and apply:

```text
http
```

Select the `GET /` request or the `HTTP/1.1 200 OK` response, then use
**Follow → TCP Stream** to view the complete exchange and the `hello` page.

For a command-line inspection inside the capture device, run:

```sh
kathara exec wireshark -- tcpdump -nn -A -r /shared/http.pcap
```

To replace the old capture and begin a new one:

```sh
kathara exec wireshark -- /usr/local/bin/start-http-capture
```

That command deliberately replaces `shared/http.pcap`; copy an earlier capture
elsewhere before restarting if it must be retained.

## Quick validation

Run these checks separately:

```sh
kathara exec client -- ping -c 2 10.10.0.3
```

```sh
kathara exec client -- curl -fsS -o /tmp/index.html -w '%{http_code}\n' http://10.10.0.3/
```

```sh
kathara exec client -- sed -n 's:.*<body>\\(.*\\)</body>.*:\\1:p' /tmp/index.html
```

The last two commands should print `200` and `hello`. After stopping the
capture, verify that it contains port 80 packets:

```sh
kathara exec wireshark -- tcpdump -nn -r /shared/http.pcap 'tcp port 80'
```

## Stop and clean up

Flush the capture first if it should be retained, then clean up the lab:

```sh
kathara exec wireshark -- /usr/local/bin/stop-http-capture
```

```sh
kathara lclean
```

## Troubleshooting

- **The client cannot ping the server:** inspect `ip addr show` on all devices
  and `ip link show master br0` on `wireshark`. Both `eth0` and `eth1` must be
  bridge ports.
- **The page is unavailable:** run
  `kathara exec server -- systemctl status apache2` and confirm that
  `/var/www/html/index.html` exists.
- **The capture is empty:** make a new client request after the lab is fully
  started, then stop the capture before reading it. Inspect
  `/var/log/http-capture.log` on `wireshark` for `tcpdump` errors.
- **Only ARP appears:** verify that the client requested `10.10.0.3` on TCP port
  80 and that traffic crosses the inline bridge rather than another host path.
- **The capture file does not appear on the host:** confirm that the lab's
  `shared/` directory is mounted at `/shared` in the devices and inspect the
  same path from `wireshark`.
