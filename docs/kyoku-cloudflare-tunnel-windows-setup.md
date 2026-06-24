# Kyoku Cloudflare Tunnel Windows Setup

This document is stored in the `Stampede-Management` project as an operator reference for recreating the personal Kyoku
Cloudflare Tunnel setup on a Windows device.

It does not contain the tunnel credential JSON contents. Do not commit or share the actual credentials file.

## Existing Tunnel Details

| Field                   | Value                                                                      |
|-------------------------|----------------------------------------------------------------------------|
| Tunnel name             | `kyoku`                                                                    |
| Tunnel UUID             | `ba9c2d5f-9969-4708-914a-b4882c5330ec`                                     |
| Current public hostname | `kyoku-gateway.poulastaa.dev`                                              |
| Local service target    | `http://localhost:8080`                                                    |
| macOS config path       | `/Users/poulastaad/.cloudflared/config.yml`                                |
| macOS credentials path  | `/Users/poulastaad/.cloudflared/ba9c2d5f-9969-4708-914a-b4882c5330ec.json` |

Current macOS `config.yml`:

```yaml
tunnel: ba9c2d5f-9969-4708-914a-b4882c5330ec
credentials-file: /Users/poulastaad/.cloudflared/ba9c2d5f-9969-4708-914a-b4882c5330ec.json
ingress:
  - hostname: kyoku-gateway.poulastaa.dev
    service: http://localhost:8080
  - service: http_status:404
```

## Current macOS Finding

The Cloudflare tunnel exists, but it was not actively connected when checked.

The macOS service files existed at:

```text
/Users/poulastaad/Library/LaunchAgents/com.cloudflare.cloudflared.plist
/Library/LaunchDaemons/com.cloudflare.cloudflared.plist
```

Both service files launched only:

```text
/opt/homebrew/bin/cloudflared
```

That is not enough to start the named tunnel. `cloudflared` logs showed the expected fix:

```text
use `cloudflared tunnel run` to start tunnel ba9c2d5f-9969-4708-914a-b4882c5330ec
```

Manual macOS startup should be:

```sh
cloudflared tunnel run kyoku
```

or explicitly:

```sh
cloudflared tunnel --config /Users/poulastaad/.cloudflared/config.yml run kyoku
```

## Windows Target Layout

Use this layout on Windows:

```text
C:\Cloudflared\bin\cloudflared.exe
C:\Windows\System32\config\systemprofile\.cloudflared\config.yml
C:\Windows\System32\config\systemprofile\.cloudflared\ba9c2d5f-9969-4708-914a-b4882c5330ec.json
C:\Cloudflared\cloudflared.log
```

The `systemprofile` path matters because the Windows service runs as `LocalSystem`, not as the normal logged-in user.

## Install `cloudflared` on Windows

Open an Administrator Command Prompt.

Create the folders:

```bat
mkdir C:\Cloudflared\bin
mkdir C:\Windows\System32\config\systemprofile\.cloudflared
```

Download the Windows `cloudflared` executable from Cloudflare and place it at:

```text
C:\Cloudflared\bin\cloudflared.exe
```

Verify it:

```bat
C:\Cloudflared\bin\cloudflared.exe --version
```

## Authenticate

Run:

```bat
C:\Cloudflared\bin\cloudflared.exe login
```

This creates `cert.pem` in the current Windows user's profile. Copy it into the service profile:

```bat
copy C:\Users\%USERNAME%\.cloudflared\cert.pem C:\Windows\System32\config\systemprofile\.cloudflared\cert.pem
```

## Reuse the Existing Tunnel

To reuse the existing `kyoku` tunnel, privately copy this credentials file from macOS:

```text
/Users/poulastaad/.cloudflared/ba9c2d5f-9969-4708-914a-b4882c5330ec.json
```

Place it on Windows at:

```text
C:\Windows\System32\config\systemprofile\.cloudflared\ba9c2d5f-9969-4708-914a-b4882c5330ec.json
```

If it first lands in the normal user's `.cloudflared` folder, copy it:

```bat
copy C:\Users\%USERNAME%\.cloudflared\ba9c2d5f-9969-4708-914a-b4882c5330ec.json C:\Windows\System32\config\systemprofile\.cloudflared\ba9c2d5f-9969-4708-914a-b4882c5330ec.json
```

## Create the Windows Config

Create:

```text
C:\Windows\System32\config\systemprofile\.cloudflared\config.yml
```

Content:

```yaml
tunnel: ba9c2d5f-9969-4708-914a-b4882c5330ec
credentials-file: C:\Windows\System32\config\systemprofile\.cloudflared\ba9c2d5f-9969-4708-914a-b4882c5330ec.json
ingress:
  - hostname: kyoku-gateway.poulastaa.dev
    service: http://localhost:8080
  - service: http_status:404
logfile: C:\Cloudflared\cloudflared.log
```

## Validate the Config

Run:

```bat
C:\Cloudflared\bin\cloudflared.exe tunnel --config C:\Windows\System32\config\systemprofile\.cloudflared\config.yml ingress validate
```

Expected result:

```text
OK
```

Check the current hostname routing:

```bat
C:\Cloudflared\bin\cloudflared.exe tunnel --config C:\Windows\System32\config\systemprofile\.cloudflared\config.yml ingress rule https://kyoku-gateway.poulastaa.dev
```

Expected result:

```text
hostname: kyoku-gateway.poulastaa.dev
service: http://localhost:8080
```

## DNS Route Commands

The current hostname is:

```text
kyoku-gateway.poulastaa.dev
```

To create or repair the current DNS route:

```bat
C:\Cloudflared\bin\cloudflared.exe tunnel route dns kyoku kyoku-gateway.poulastaa.dev
```

Your proposed command is valid syntax:

```bat
cloudflared tunnel route dns kyoku kyoku.gateway.poulastaa.dev
```

But it creates this different hostname:

```text
kyoku.gateway.poulastaa.dev
```

That is not the same as:

```text
kyoku-gateway.poulastaa.dev
```

If you want the dotted hostname, add it to `ingress` before the catch-all rule:

```yaml
ingress:
  - hostname: kyoku-gateway.poulastaa.dev
    service: http://localhost:8080
  - hostname: kyoku.gateway.poulastaa.dev
    service: http://localhost:8080
  - service: http_status:404
```

Then create its DNS route:

```bat
C:\Cloudflared\bin\cloudflared.exe tunnel route dns kyoku kyoku.gateway.poulastaa.dev
```

Validate it:

```bat
C:\Cloudflared\bin\cloudflared.exe tunnel --config C:\Windows\System32\config\systemprofile\.cloudflared\config.yml ingress rule https://kyoku.gateway.poulastaa.dev
```

If Kyoku application config references `kyoku-gateway.poulastaa.dev`, update those references before switching to
`kyoku.gateway.poulastaa.dev`.

## Manual Tunnel Run

Use this for foreground testing:

```bat
C:\Cloudflared\bin\cloudflared.exe tunnel --config C:\Windows\System32\config\systemprofile\.cloudflared\config.yml run kyoku
```

This proposed command is valid only if the default config and credentials paths are correct for the current process
user:

```bat
cloudflared tunnel run kyoku
```

For Windows service usage, prefer the explicit `--config` command.

## Install as a Windows Service

Install the service:

```bat
C:\Cloudflared\bin\cloudflared.exe service install
```

Then verify the Windows service registry entry:

```text
Computer\HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Cloudflared
```

Set `ImagePath` to:

```text
C:\Cloudflared\bin\cloudflared.exe --config=C:\Windows\System32\config\systemprofile\.cloudflared\config.yml tunnel run
```

Start the service:

```bat
sc start cloudflared
```

Restart after config changes:

```bat
sc stop cloudflared
sc start cloudflared
```

Check status:

```bat
sc query cloudflared
```

## Local Kyoku Requirement

Cloudflare Tunnel only forwards traffic. The Kyoku gateway must already be running on Windows at `localhost:8080`.

Check locally:

```bat
curl http://localhost:8080
curl http://localhost:8080/actuator/health
```

If the tunnel connects but the gateway is down, public requests will fail with an origin connection error.

## Troubleshooting

If `cloudflared` says to use `cloudflared tunnel run`, the process was started without the `tunnel run` subcommand.

If `cloudflared tunnel info kyoku` shows no active connection, the tunnel process is not currently connected to
Cloudflare.

If DNS exists but the hostname returns `404`, the hostname is missing from the `ingress` rules or appears after the
catch-all rule.

If the tunnel works manually but not as a Windows service, verify the service can read these files:

```text
C:\Windows\System32\config\systemprofile\.cloudflared\config.yml
C:\Windows\System32\config\systemprofile\.cloudflared\cert.pem
C:\Windows\System32\config\systemprofile\.cloudflared\ba9c2d5f-9969-4708-914a-b4882c5330ec.json
```

If credentials cannot be found, verify that `credentials-file` in `config.yml` points to the exact JSON path visible to
the Windows service account.
