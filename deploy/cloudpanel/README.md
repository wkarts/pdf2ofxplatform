# CloudPanel

Crie o domínio como **Reverse Proxy** e aponte para:

```text
http://127.0.0.1:8080
```

O SSL fica no CloudPanel. O gateway NGINX do Compose só aceita conexões no
loopback da VPS.

Ajustes recomendados no VHost:

```nginx
client_max_body_size 50M;
proxy_connect_timeout 30s;
proxy_send_timeout 120s;
proxy_read_timeout 120s;
proxy_buffering off;

proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

Não publique diretamente as portas do PostgreSQL, Redis ou FastAPI.
