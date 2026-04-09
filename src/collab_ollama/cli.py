import argparse
import platform
import subprocess
import shutil
import re
import sys

try:
    from rich import print
except ImportError:
    pass

DEFAULT_MODEL = "phi3:mini"

def run_sh(command: str, bg: bool = False):
    kwargs = {"shell": True, "check": True}
    if bg:
        kwargs["stdout"] = subprocess.DEVNULL
        kwargs["stderr"] = subprocess.DEVNULL
    process = subprocess.run(command, **kwargs)
    assert process.returncode == 0


def ensure_linux():
    if platform.system() != "Linux":
        print(f"Error: collab-ollama only supports Linux. Detected: {platform.system()}")
        sys.exit(1)


def install_system_packages(packages: list[str]):
    if shutil.which("apt-get"):
        run_sh(f"apt-get install -y -qq {' '.join(packages)}", bg=True)
    elif shutil.which("dnf"):
        run_sh(f"dnf install -y -q {' '.join(packages)}", bg=True)
    elif shutil.which("pacman"):
        run_sh(f"pacman -S --noconfirm --needed {' '.join(packages)}", bg=True)
    else:
        print(f"Warning: Could not detect package manager. Please install manually: {', '.join(packages)}")


def install_ollama():
    if not shutil.which("ollama"):
        print("Installing Ollama...")
        install_system_packages(["pciutils", "lshw", "zstd"])
        run_sh("curl -fsSL https://ollama.com/install.sh | sh")


def install_cloudflared():
    if not shutil.which("cloudflared"):
        print("Installing Cloudflared...")
        if shutil.which("apt-get"):
            run_sh(
                "wget -q -nc https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && sudo dpkg -i ./cloudflared-linux-amd64.deb",
                bg=True,
            )
        elif shutil.which("dnf"):
            run_sh(
                "wget -q -nc https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-x86_64.rpm && sudo rpm -i ./cloudflared-linux-x86_64.rpm",
                bg=True,
            )
        elif shutil.which("pacman"):
            run_sh("pacman -S --noconfirm cloudflared", bg=True)
        else:
            print("Error: Could not detect package manager. Please install cloudflared manually.")
            sys.exit(1)


def serve_ollama():
    subprocess.run("OLLAMA_ORIGINS=* nohup ollama serve &", shell=True)


def pull_model(model: str):
    print(f"Pulling model '{model}'...")
    run_sh(f"ollama pull {model}")


def expose_ollama_with_cloudflared(model: str, port: int = 11434):
    cmd = f'cloudflared tunnel --url http://localhost:{port} --http-host-header="localhost:{port}"'
    try:
        with subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        ) as process:
            for line in process.stdout:
                if ".trycloudflare.com" in line:
                    domain = re.search(r"https://[^ ]+\.trycloudflare\.com", line)
                    if domain:
                        tunnel_url = domain.group(0)
                        print("\nSetup is complete!\n")
                        print(f"  Base URL : {tunnel_url}/v1/")
                        print(f"  API Key  : No key required — leave it blank or use any string")
                        print(f"  Model    : {model}")
                        print()
            process.wait()
    except subprocess.CalledProcessError as e:
        print(f"Command '{cmd}' failed with return code {e.returncode}")
    except Exception as e:
        print(f"An error occurred: {e}")


def parse_args():
    parser = argparse.ArgumentParser(
        prog="collab-ollama",
        description="Expose Ollama models to the internet on a remote server via tunneling",
    )
    parser.add_argument(
        "-m", "--model",
        default=DEFAULT_MODEL,
        help=f"Model to pull and serve (default: {DEFAULT_MODEL})",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    ensure_linux()
    install_ollama()
    install_cloudflared()
    serve_ollama()
    pull_model(args.model)
    expose_ollama_with_cloudflared(model=args.model)


if __name__ == "__main__":
    main()
