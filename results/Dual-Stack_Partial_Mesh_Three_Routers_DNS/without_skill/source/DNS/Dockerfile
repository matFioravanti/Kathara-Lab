FROM kathara/base
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y bind9 && rm -rf /var/lib/apt/lists/*
COPY etc/bind/named.conf /etc/bind/named.conf
COPY etc/bind/db.company.test /etc/bind/db.company.test
