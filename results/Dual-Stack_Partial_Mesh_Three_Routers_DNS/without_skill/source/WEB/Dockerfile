FROM kathara/base
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y apache2 && rm -rf /var/lib/apt/lists/*
COPY var/www/html/index.html /var/www/html/index.html
RUN printf 'ServerName company.test\nListen 80\nListen [::]:80\n' > /etc/apache2/conf-available/company.conf && a2enconf company
