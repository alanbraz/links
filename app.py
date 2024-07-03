import os, yaml, requests
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, HTMLResponse

app = FastAPI()
# Cache variable shared across all endpoints
app.cache = {}
print(len(app.cache))
def load_links(app):
    try:
        links_file = os.environ.get("LINKS_FILE", "links.yaml")
        print("links_file", links_file)
        if links_file.startswith("http"):
            response = requests.get(links_file)
            if response.status_code == 200:
                print("loading from web")
                app.cache = yaml.safe_load(response.text)["links"]
            else:
                raise Exception('Failed to load links file from {}: {}'.format(links_file, response.status_code))
        else:
            print("loading local file")
            with open(links_file, "r") as f:
                app.cache = yaml.safe_load(f)["links"]
    except Exception as e:
        print(e)

load_links(app)

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html>
        <head>
            <title>Short links redirect</title>
            <link type="text/css" rel="stylesheet" href="https://pullrecast.dev/css/main.bundle.min.ef8f612642e6e6308e9f3937d74b8c560ee3e4b12e3d1bbae2b5321f50dd7a5ea488fa18eb67a14e941875cb38828e4933df6ecdfd6a8eb97585248eae5adb1d.css">
        </head>
        <body class="flex flex-col h-screen px-6 m-auto text-lg leading-7 bg-neutral max-w-7xl text-neutral-900 dark:bg-neutral-800 dark:text-white sm:px-14 md:px-24 lg:px-32">
            <h1>Lista de links curtos:</h1>
            <ul>{}</ul>
        </body>
    </html>
    """.format("".join(["<li><a href='/{}' target='_blank'>{}</a>{}{}</li>".format(l, l, " - <b>"+app.cache[l]["name"]+"</b>" if "name" in app.cache[l] else "", ": "+app.cache[l]["desc"] if "desc" in app.cache[l] else "") for l in app.cache]))
    
@app.get("/{alias}")
def redirect(alias):
    if alias not in app.cache:
        print("{} not found. Reloading links...".format(alias))
        load_links(app)
    return RedirectResponse(app.cache[alias] if type(app.cache[alias]) == str else app.cache[alias]["url"])