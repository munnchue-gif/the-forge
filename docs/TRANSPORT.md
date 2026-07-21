# TRANSPORT — Cloudflare Tunnel for App↔Forge (Phase B)

Per COLLAB decision T1: Cloudflare Tunnel + Access service token. Bridge listens on
127.0.0.1:8787 (see forge/bridge/server.py) — the tunnel is the only way in.

## 1. Install + login (on the Forge PC, Pop!_OS)

```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cloudflared.deb
sudo dpkg -i cloudflared.deb
cloudflared tunnel login
```

## 2. Create the tunnel + DNS

```bash
cloudflared tunnel create forge-bridge
cloudflared tunnel route dns forge-bridge forge.<yourdomain>.com
```

## 3. Config — ~/.cloudflared/config.yml

```yaml
tunnel: forge-bridge
credentials-file: /home/<user>/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: forge.<yourdomain>.com
    service: http://127.0.0.1:8787
    originRequest:
      noHappyEyeballs: true
      disableChunkedEncoding: false   # keep SSE /feed streaming
  - service: http_status:404
```

## 4. Lock it behind Access (transport identity — B3)

Cloudflare Zero Trust dashboard → Access → Applications → Self-hosted:
- Application domain: forge.<yourdomain>.com
- Policy: **Service Auth** → create a **Service Token** (name: `the-app`)
- Copy the Client ID + Client Secret into the App's Bridge Settings
  (stored only in the operator's browser — never in the cloud DB).

The App sends `CF-Access-Client-Id` / `CF-Access-Client-Secret` on every request,
including the SSE feed (fetch-stream, not EventSource).

## 5. Run as a service

```bash
sudo cloudflared service install
sudo systemctl enable --now cloudflared
cloudflared tunnel info forge-bridge
```

## 6. Verify end to end

```bash
curl -H "CF-Access-Client-Id: <ID>" -H "CF-Access-Client-Secret: <SECRET>" \
  https://forge.<yourdomain>.com/health
```

Expect `{"contract_version":"0.1.0","booted":true,...}`. Then paste the URL + token
pair into the App → Forge Link → settings.

> Never bind the bridge to a public interface. 127.0.0.1 + tunnel only.
