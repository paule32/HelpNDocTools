from bs4 import BeautifulSoup
import json

html = ""
with open("index.toc", "r", encoding="utf-8") as f:
    html = f.read()
    f.close()

# BeautifulSoup zum Parsen
soup = BeautifulSoup(html, 'html.parser')

# Alle <a> Tags extrahieren
links = []
for a in soup.find_all('a', href=True):
    href = a['href'].split('#')[0]  # Anker entfernen
    text = a.get_text(strip=True)
    links.append({'text': text, 'href': href})

# Hilfsfunktion zum Einfügen nach Nummerierung
def insert_node(tree, id_parts, title, href):
    if tree is None:
        tree = []  # Sicherstellen, dass tree eine Liste ist
    if not id_parts:
        return
    part = id_parts[0]

    # Suche, ob schon vorhanden
    node = next((n for n in tree if n['id'] == part), None)
    if node is None:
        node = {
            'id': part,
            'title': title if len(id_parts) == 1 else '',
            'children': [] if len(id_parts) > 1 else None,
            'href': href if len(id_parts) == 1 else None
        }
        tree.append(node)

    # Rekursiv für Kinder
    if len(id_parts) > 1:
        if node.get('children') is None:
            node['children'] = []
        insert_node(node['children'], id_parts[1:], title, href)

tocData = []

for link in links:
    # Prüfen, ob Text mit Nummer beginnt, z.B. 1., 1.1., 1.3.1.
    parts = link['text'].split(' ', 1)
    if len(parts) == 2 and parts[0][0].isdigit():
        id_str = parts[0].rstrip('.')
        id_parts = id_str.split('.')
        insert_node(tocData, id_parts, parts[1], link['href'])
    else:
        # Nummerierung fehlt => oberste Ebene, id="0", kann angepasst werden
        tocData.append({'id':'0', 'title':link['text'], 'href':link['href']})

# Optional: leere 'children':[] entfernen, wenn None
def clean_children(nodes):
    for n in nodes:
        if n.get('children') == []: n.pop('children')
        elif n.get('children'): clean_children(n['children'])

clean_children(tocData)
text_html = """
<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>CHM-ähnlicher Themenbaum (TOC)</title>
<style>
:root{
--sidebar-width:320px;
--bg:#f3f4f6;
--panel:#ffffff;
--accent:#0b5cff;
--muted:#6b7280;
--folder:#e6f0ff;
}
html,body{height:100%;margin:0;font-family:Inter, Roboto, Arial, sans-serif;background:var(--bg);color:#111;display:flex}
.sidebar{width:var(--sidebar-width);min-width:240px;background:linear-gradient(180deg,#f8fafc,#ffffff);border-right:1px solid #e6e9ee;display:flex;flex-direction:column;height:100vh}
.sidebar .header{padding:12px 14px;border-bottom:1px solid #eee;display:flex;gap:8px;align-items:center}
.sidebar h1{font-size:15px;margin:0}
.controls{display:flex;gap:6px;margin-left:auto}
.btn{background:#fff;border:1px solid #e6e9ee;padding:6px 8px;border-radius:6px;font-size:13px;cursor:pointer}
.search{padding:8px 12px;border-bottom:1px solid #eee}
.search input{width:100%;padding:8px;border:1px solid #e6e9ee;border-radius:6px;font-size:14px}

.splitter{width:6px;background:#ddd;cursor:col-resize;flex-shrink:0;}
.tree-wrap{overflow:auto;padding:8px;flex:1}
.tree{list-style:none;margin:0;padding:0}
.node{display:block;padding:6px 8px;border-radius:6px;margin:2px 0;cursor:pointer;user-select:none}
.node:hover{background:#f1f5f9}
.node[aria-expanded="true"]>.node-label>.caret{transform:rotate(90deg)}


.node-label{display:flex;align-items:center;gap:8px}
.caret{transition:transform .15s ease}
.icon-folder{width:18px;height:14px;border-radius:2px;background:linear-gradient(180deg,#fff,#f0f7ff);display:inline-block;border:1px solid #d6e3ff}
.title{flex:1}


.children{list-style:none;margin:6px 0 0 18px;padding:0;display:none}
.node[aria-expanded="true"]>.children{display:block}


.node[aria-selected="true"]{background:var(--folder);border:1px solid #dbe9ff}


.content{flex:1;padding:16px;overflow:auto}
.loading{font-size:14px;color:var(--muted)}


@media (max-width:700px){
.sidebar{position:fixed;left:0;top:0;bottom:0;z-index:40;transform:translateX(0);box-shadow:0 6px 18px rgba(2,6,23,0.12)}
}
</style>
</head>
<body>
<aside class="sidebar" role="navigation" aria-label="Themenbaum">
<div class="header">
<h1>Inhaltsverzeichnis</h1>
<div class="controls">
<button class="btn" id="expandAll" title="Alle aufklappen">⯈ Alle</button>
<button class="btn" id="collapseAll" title="Alle zuklappen">⯈ Zu</button>
</div>
</div>
<div class="search">
<input id="filter" placeholder="Suche... (z. B. Stichwort oder Titel)" aria-label="Suche im Inhaltsverzeichnis">
</div>
<div class="tree-wrap">
<ul class="tree" id="toc" role="tree"></ul>
</div>
</aside>
<div class="splitter"></div>
<div class="content" id="content">Wähle ein Thema aus...</div>
<script>
const tocData = """
text_js    = json.dumps(tocData, ensure_ascii=False, indent=2) + ';'
text_html += text_js
text_html += """
const tocEl = document.getElementById('toc');
}


container.appendChild(li);
});
}


function selectNode(node, parentPath){
document.querySelectorAll('.node[aria-selected=true]').forEach(n=>n.removeAttribute('aria-selected'));
const selected = document.querySelector(`.node[data-id="${node.id}"]`);
if(selected) selected.setAttribute('aria-selected','true');


if(typeof onNodeSelect === 'function'){
const fullPath = parentPath.concat(node);
onNodeSelect(node, fullPath);
}
}


function escapeHtml(s){
return String(s).replace(/[&<>"']/g, (c)=>({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"})[c]);
}


function filterTree(q){
q = q.trim().toLowerCase();
document.querySelectorAll('#toc .node').forEach(nodeEl=>{
const title = nodeEl.querySelector('.title').textContent.toLowerCase();
if(!q){ nodeEl.style.display=''; return; }
if(title.includes(q)){
nodeEl.style.display='';
let parent = nodeEl.parentElement.closest('.node');
while(parent){ parent.style.display=''; parent.setAttribute('aria-expanded','true'); parent = parent.parentElement.closest('.node'); }
} else {
nodeEl.style.display='none';
}
});
}


filterInput.addEventListener('input',(e)=> filterTree(e.target.value));


document.getElementById('expandAll').addEventListener('click', ()=>{
document.querySelectorAll('#toc .node').forEach(n=>{ if(n.querySelector('.children')) n.setAttribute('aria-expanded','true'); });
});
document.getElementById('collapseAll').addEventListener('click', ()=>{
document.querySelectorAll('#toc .node').forEach(n=>{ if(n.querySelector('.children')) n.setAttribute('aria-expanded','false'); });
});

// Callback-Funktion mit Fetch
function onNodeSelect(node, fullPath){
if(node.href){
contentEl.innerHTML = '<p class="loading">Lade Inhalt...</p>';
fetch(node.href)
.then(res => {
if(!res.ok) throw new Error('Fehler beim Laden: '+res.status);
return res.text();
})
.then(html => {
contentEl.innerHTML = html;
})
.catch(err => {
contentEl.innerHTML = '<p style="color:red">'+err.message+'</p>';
});
}
}

const tocEl = document.getElementById('toc');
buildTree(tocData, tocEl);

// Splitter Drag-Funktion
const sidebar = document.querySelector('.sidebar');
const splitter = document.querySelector('.splitter');
let isDragging = false;

splitter.addEventListener('mousedown', () => {
  isDragging = true;
  document.body.style.cursor = 'col-resize';
});

document.addEventListener('mousemove', e => {
  if(!isDragging) return;
  let newWidth = e.clientX;
  if(newWidth < 150) newWidth = 150;
  if(newWidth > 600) newWidth = 600;
  sidebar.style.width = newWidth + 'px';
});

document.addEventListener('mouseup', () => {
  isDragging = false;
  document.body.style.cursor = 'default';
});
</script>

</body>
</html>
"""
with open("index.json", "w", encoding="utf-8") as f:
    f.write('const tocData =' + text_js)
    f.close()

with open("index.html", "w", encoding="utf-8") as f:
    f.write(text_html)
    f.close()
