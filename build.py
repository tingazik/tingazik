import yaml
from glob import glob
from pathlib import Path
from jinja2 import Template
from collections import defaultdict
import hashlib
import re
import minify_html
import shutil
import json

out_dir = Path("out/")
debug_menu = "ddeebbuuggmmeennuuu"
path_mapping = {}

with open("stages.yaml") as f:
    data = yaml.load(f, Loader=yaml.SafeLoader)

def get_difficulties(curr_difficulty: str):
    difficulties = ["nohint", "1sample", "3samples",
                    "keywords", "solution", "answer"]

    difficulties = difficulties[:difficulties.index(curr_difficulty) + 1]
    difficulties = difficulties[:2] + ["startanswer"] + difficulties[2:]
    return difficulties

with open("templates/frame.html") as f:
    template = Template(f.read())

def sha1_str(source: str) -> str:
    sha1 = hashlib.sha1()
    sha1.update(source.encode())
    return sha1.hexdigest()[:8]

def page_hash(source: str) -> str:
    source = re.sub("[^a-fA-F0-9]", "", source)
    if len(source) % 2 != 0:
        source = source + "0"
    result = bytes.fromhex(source)
    md5 = hashlib.md5()
    md5.update(result)
    return md5.hexdigest()


def render(template: Template, stage: str, difficulty: str, name: str, filename: str) -> str:
    name = name.upper()
    print(f"rendering stage {stage} @ {difficulty} with {name} as {filename}")

    with open(f"data/{stage}/{difficulty}.html") as f:
        content = f.read()
    if difficulty == "1sample":
        with open(f"data/{stage}/nohint.html") as f:
            content = content + "\n<hr>\n" + f.read()
    
    footer = f"{name} {sha1_str(name)}".upper()

    result = template.render(content=content, footer=footer, title=name)
    result = minify_html.minify(result, minify_js=True, minify_css=True)
    new_hash = page_hash(result)

    p = out_dir / filename
    if not p.exists():
        p.mkdir(parents=True)
    with (p / "index.html").open("w") as f:
        f.write(result)
    
    global path_mapping
    path_mapping[filename.strip("/")] = f"{stage} {difficulty}"

    return new_hash


def render_index(p: Path, min_difficulty: str):
    if not p.exists():
        p.mkdir()
    with open("index.html") as f:
        index_template = Template(f.read())
        result = index_template.render(difficulty=min_difficulty)
        result = minify_html.minify(result, minify_js=True, minify_css=True)
        with (p / "index.html").open("w") as f:
            f.write(result)

    global path_mapping
    path_mapping[str(p.relative_to(out_dir)).strip("/")] = f"index {min_difficulty}"


def clean_up():
    paths = glob(f"{out_dir}/*", recursive=True)
    print(paths)
    for path in paths:
        p = Path(path)
        if p.is_dir():
            print("Remove dir", p)
            shutil.rmtree(p)
        else:
            print("Remove file", p)
            p.unlink()

def render_dummies(prefix: str = ""):
    for idx, name in enumerate(data["dummies"]):
        with open(f"data/dummies/{idx}.html") as f:
            content = f.read()
        footer = f"{name} {sha1_str(name)}".upper()

        result = template.render(content=content, footer=footer, title=name)
        result = minify_html.minify(result, minify_js=True, minify_css=True)

        filename = prefix + name
        p = out_dir / filename
        if not p.exists():
            p.mkdir(parents=True)
        with (p / "index.html").open("w") as f:
            f.write(result)
        
        global path_mapping
        path_mapping[filename.strip("/")] = f"dummy #{idx} {name}"

def render_difficulty(min_difficulty: str, prefix: str = ""):
    mapping = defaultdict(dict)

    last_answer = None
    difficulties = get_difficulties(min_difficulty)

    for i in data["stages"]:
        name = i["name"]
        answer = i["answer"]
        filename = last_answer

        if name.startswith("start_") or last_answer is None:
            filename = name
        
        path = Path(f"data/{name}")
        last_hash = None

        diff = difficulties[:]

        if "1sample" in diff and (path / f"1sample.html").exists():
            last_hash = render(template, name, "1sample",
                            f"{filename}_1sample", prefix + filename)
            mapping[name]["1sample"] = filename
        else:
            last_hash = render(template, name, "nohint", filename, prefix + filename)
            mapping[name]["nohint"] = filename

        if "1sample" in diff:
            diff = diff[2:]
        else:
            diff = diff[1:]

        for d in diff:
            if (path / f"{d}.html").exists():
                mapping[name][d] = last_hash
                last_hash = render(template, name, d, f"{filename}_{d}", prefix + last_hash)
            else:
                print((path / f"{d}.html"), "doesn’t exist.")

        last_answer = answer

    render_index(out_dir / prefix, min_difficulty)
    render_debug_menu(mapping, out_dir / prefix, difficulties)
    render_dummies(prefix)

## Render debug menu
def render_debug_menu(mapping, path, difficulties):
    table = "<table>\n"
    for i, im in mapping.items():
        table += f"<tr><th>{i}</th>"
        for j in difficulties:
            if j in im:
                table += f'<td><a href="../{im[j]}">{j}</a></td>'
            else:
                table += f'<td><del>{j}</del></td>'
        table += "</tr>\n"
    
    for idx, name in enumerate(data["dummies"]):
        table += f"<tr><th>dummy #{idx}</th>"
        for j in range(len(difficulties)):
            if j == 0:
                table += f'<td><a href="../{name}">{name}</a></td>'
            else:
                table += f'<td></td>'
        table += "</tr>\n"
    
    table += "</table>"

    title = "DEBUG MENU"

    result = template.render(content=table, footer=title.upper(), title=title)

    p = path / debug_menu
    if not p.exists():
        p.mkdir(parents=True)
    with (p / "index.html").open("w") as f:
        f.write(result)

    global path_mapping
    path_mapping[str(p.relative_to(out_dir)).strip("/")] = f"debug menu {difficulties[-1]}"


def render_difficulty_index():
    ## render difficulties index
    levels_list = "<ol>\n"
    for i in levels:
        levels_list += f'<li><a href="{i}">{i}</a></li>'
    levels_list += "</ol>"

    levels_list += """
    <p>注：测试模式输入答案要带难度前缀。如 nohint 难度的某一题答案是 <code>answer</code>，则下一关的网址是
    <code>https://wkopgtest.1a23.studio/<b>nohint</b>/<b>answer</b></code> 。
    """

    title = "DIFFICULTIES_MENU"

    result = template.render(content=levels_list, footer=title.upper(), title=title)

    with (out_dir / "index.html").open("w") as f:
        f.write(result)


if __name__ == "__main__":
    clean_up()
    # levels = ["nohint", "1sample", "3samples", "keywords", "solution", "answer"]
    # for i in levels:
    #     render_difficulty(i, f"{i}/")

    render_difficulty(data["difficulty"], "")

    ## render 404
    with (out_dir / "404.html").open("w") as f:
        f.write("<!DOCTYPE html><html><head><title>404 Not Found</title></head><body><h1>404 Not Found</h1><p>That’s probably a wrong answer.</p></body></html>")

    shutil.copyfile("templates/social.png", "out/social.png")
    shutil.copyfile("templates/robots.txt", "out/robots.txt")

    with open("mapping.json", "w") as f:
        json.dump(path_mapping, f)