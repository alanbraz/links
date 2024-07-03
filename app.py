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
            <!-- <link rel="stylesheet" href="//unpkg.com/carbon-components@9.90.0/css/carbon-components.min.css"> -->
        </head>
        <body>
            <main>
                <h1>Lista de links curtos:</h1>
                <ul>{}</ul>
                <cds-button><a href='/reload'>Recarregar links</a></cds-button>
            </main>
        </body>
    </html>
    """.format("".join(["<li><a href='/{}' target='_blank'>{}</a>{}{}</li>".format(l, l, " - <b>"+app.cache[l]["name"]+"</b>" if "name" in app.cache[l] else "", ": "+app.cache[l]["desc"] if "desc" in app.cache[l] else "") for l in app.cache]))
    
@app.get("/reload")
def reload():
    load_links(app)
    print("{} links carregados".format(len(app.cache)))
    return RedirectResponse("/")

@app.get("/{alias}")
def redirect(alias):
    if alias not in app.cache:
        print("{} not found. Reloading links...".format(alias))
        load_links(app)
    return RedirectResponse(app.cache[alias] if type(app.cache[alias]) == str else app.cache[alias]["url"])

