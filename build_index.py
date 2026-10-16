import os
import re
import html

base_dir = os.path.dirname(os.path.abspath(__file__))

title_regex = re.compile(r'<title[^>]*>(.*?)</title>', re.IGNORECASE | re.DOTALL)

def get_html_title(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(4096)
            m = title_regex.search(content)
            if m:
                t = m.group(1).strip()
                t = re.sub(r'[\x00-\x1f\x7f-\x9f\ufffd]', ' ', t)
                t = re.sub(r'\s+', ' ', t).strip()
                return t
    except Exception:
        pass
    return ''

def format_size(bytes_size):
    if bytes_size is None:
        return '0 B'
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.2f} MB"

def get_category(folder_name):
    lower = folder_name.lower()
    # Check specific categories first
    if 'tel-protocol' in lower:
        return 'Protocol Handlers'
    elif any(k in lower for k in ['filepicker', 'download', 'fake-download', 'inconsistent-security', 'google-update']):
        return 'Download & File Spoofing'
    elif any(k in lower for k in ['audio', 'geolocation', 'permission', 'webusb', 'sanbox', 'origin']):
        return 'Origin & Permissions'
    elif any(k in lower for k in ['redressing', 'dragndrop', 'split-view', 'fullscreen', 'back-navigate', 'popup', 'install-dialog']):
        return 'UI Redressing & Interaction'
    elif any(k in lower for k in ['addressbar', 'blank-url', 'hide-omnibox', 'spoof', 'accounts-google']):
        return 'Address Bar & URL Spoofing'
    elif 'root' in lower:
        return 'Root PoCs & Exploits'
    else:
        return 'General & Other'

# Scan root files
root_files = []
for f in sorted(os.listdir(base_dir)):
    p = os.path.join(base_dir, f)
    if os.path.isfile(p):
        if f in ['desktop.ini', 'index.html', 'build_index.py', '.gitignore']:
            continue
        size = os.path.getsize(p)
        raw_title = get_html_title(p) if f.endswith('.html') else ''
        root_files.append({
            'name': f,
            'rel_path': f,
            'size': size,
            'size_formatted': format_size(size),
            'title': raw_title,
            'ext': os.path.splitext(f)[1]
        })

# Scan directories
directories = []
for root, dirs, files in os.walk(base_dir):
    if '.git' in root.split(os.sep):
        continue
    rel = os.path.relpath(root, base_dir).replace('\\', '/')
    if rel == '.':
        continue
    
    valid_files = [f for f in files if f not in ['desktop.ini', 'index.html']]
    has_index = 'index.html' in files
    
    # If no files and no index in this folder, skip
    if not valid_files and not has_index:
        continue
        
    folder_files = []
    folder_title = ''
    
    if has_index:
        idx_path = os.path.join(root, 'index.html')
        idx_size = os.path.getsize(idx_path)
        folder_title = get_html_title(idx_path)
        folder_files.append({
            'name': 'index.html (Main PoC)',
            'rel_path': f"{rel}/index.html",
            'size': idx_size,
            'size_formatted': format_size(idx_size),
            'title': folder_title,
            'is_main': True,
            'ext': '.html'
        })
    
    for vf in sorted(valid_files):
        p = os.path.join(root, vf)
        size = os.path.getsize(p)
        raw_title = get_html_title(p) if vf.endswith('.html') else ''
        folder_files.append({
            'name': vf,
            'rel_path': f"{rel}/{vf}",
            'size': size,
            'size_formatted': format_size(size),
            'title': raw_title,
            'is_main': False,
            'ext': os.path.splitext(vf)[1]
        })
        
    category = get_category(rel)
    directories.append({
        'dir_path': rel,
        'dir_name': os.path.basename(rel),
        'category': category,
        'title': folder_title,
        'has_main_index': has_index,
        'main_index_path': f"{rel}/index.html" if has_index else (folder_files[0]['rel_path'] if folder_files else rel),
        'files': folder_files
    })

# Sort directories by category then path
directories.sort(key=lambda d: (d['category'], d['dir_path']))

# Get stats
total_suites = len(directories)
total_files = sum(len(d['files']) for d in directories) + len(root_files)
categories_set = set(d['category'] for d in directories)
categories_order = [
    'Address Bar & URL Spoofing',
    'Download & File Spoofing',
    'Origin & Permissions',
    'Protocol Handlers',
    'UI Redressing & Interaction',
    'General & Other',
    'Root PoCs & Exploits'
]
categories = [c for c in categories_order if c in categories_set or (c == 'Root PoCs & Exploits' and root_files)]

html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Security PoC Directory & Navigator</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🛡️</text></svg>">
  <style>
    :root {{
      --bg: #090d16;
      --card-bg: #111827;
      --card-border: #1e293b;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #10b981;
      --accent-glow: rgba(16, 185, 129, 0.25);
      --accent-blue: #38bdf8;
      --accent-cyan: #06b6d4;
      --badge-bg: #1e293b;
      --border-color: #334155;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background: var(--bg);
      color: var(--text-main);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      line-height: 1.5;
      padding-bottom: 80px;
      min-height: 100vh;
    }}

    .bg-glow {{
      position: fixed;
      top: 0;
      left: 50%;
      transform: translateX(-50%);
      width: 1000px;
      height: 400px;
      background: radial-gradient(circle, rgba(16, 185, 129, 0.15) 0%, rgba(56, 189, 248, 0.06) 50%, transparent 75%);
      pointer-events: none;
      z-index: 0;
    }}

    .container {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 0 24px;
      position: relative;
      z-index: 1;
    }}

    /* Header */
    header {{
      padding: 44px 0 24px;
      border-bottom: 1px solid var(--card-border);
      margin-bottom: 28px;
    }}

    .header-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }}

    .brand {{
      display: flex;
      align-items: center;
      gap: 16px;
    }}

    .brand-icon {{
      font-size: 38px;
      background: rgba(16, 185, 129, 0.12);
      border: 1px solid rgba(16, 185, 129, 0.35);
      padding: 8px 12px;
      border-radius: 14px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 0 24px var(--accent-glow);
    }}

    .brand-text h1 {{
      font-size: 26px;
      font-weight: 800;
      letter-spacing: -0.5px;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .brand-text p {{
      font-size: 14px;
      color: var(--text-muted);
      margin-top: 3px;
    }}

    .header-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .repo-link {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: #1e293b;
      color: #e2e8f0;
      text-decoration: none;
      padding: 8px 16px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      border: 1px solid var(--border-color);
      transition: all 0.2s ease;
    }}

    .repo-link:hover {{
      background: #2d3b55;
      color: #fff;
      border-color: var(--accent);
      transform: translateY(-1px);
    }}

    /* Stats row */
    .stats-row {{
      display: flex;
      gap: 14px;
      margin-top: 24px;
      flex-wrap: wrap;
    }}

    .stat-badge {{
      background: rgba(17, 24, 39, 0.85);
      border: 1px solid var(--card-border);
      padding: 8px 16px;
      border-radius: 10px;
      font-size: 13px;
      display: flex;
      align-items: center;
      gap: 8px;
      backdrop-filter: blur(8px);
    }}

    .stat-value {{
      color: var(--accent-blue);
      font-weight: 700;
      font-size: 14px;
    }}

    /* Controls Panel */
    .controls-panel {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 20px;
      margin-bottom: 28px;
      box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    }}

    .search-bar {{
      display: flex;
      align-items: center;
      background: #090d16;
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 12px 16px;
      margin-bottom: 16px;
      transition: all 0.2s;
    }}

    .search-bar:focus-within {{
      border-color: var(--accent);
      box-shadow: 0 0 0 3px var(--accent-glow);
    }}

    .search-bar input {{
      background: transparent;
      border: none;
      outline: none;
      color: #fff;
      font-size: 15px;
      width: 100%;
      margin-left: 12px;
    }}

    .search-bar input::placeholder {{
      color: #64748b;
    }}

    .search-shortcut {{
      background: #1e293b;
      border: 1px solid #334155;
      color: #94a3b8;
      padding: 2px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-family: monospace;
      pointer-events: none;
    }}

    .filter-tags {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
    }}

    .filter-tag {{
      background: var(--badge-bg);
      color: var(--text-muted);
      border: 1px solid var(--border-color);
      padding: 7px 14px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
      user-select: none;
    }}

    .filter-tag:hover {{
      background: #283548;
      color: #fff;
    }}

    .filter-tag.active {{
      background: var(--accent);
      color: #052e16;
      border-color: var(--accent);
      font-weight: 700;
      box-shadow: 0 0 12px var(--accent-glow);
    }}

    /* Action bar */
    .action-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      font-size: 13px;
      color: var(--text-muted);
      padding: 0 4px;
    }}

    /* Category Section */
    .category-section {{
      margin-bottom: 36px;
    }}

    .category-title {{
      font-size: 18px;
      font-weight: 700;
      color: #f8fafc;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 10px;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--card-border);
    }}

    .category-title span.count {{
      font-size: 12px;
      background: #1e293b;
      color: var(--accent-blue);
      padding: 2px 10px;
      border-radius: 12px;
      font-weight: 600;
    }}

    /* Grid Layout */
    .poc-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(370px, 1fr));
      gap: 20px;
    }}

    .poc-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: all 0.25s ease;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }}

    .poc-card:hover {{
      transform: translateY(-3px);
      border-color: #38bdf888;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.45);
    }}

    .card-header {{
      padding: 16px 18px;
      border-bottom: 1px solid var(--card-border);
      background: rgba(255, 255, 255, 0.02);
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
    }}

    .card-title-group {{
      flex: 1;
      min-width: 0;
    }}

    .card-dir-name {{
      font-size: 15px;
      font-weight: 700;
      color: #ffffff;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .card-desc {{
      font-size: 12px;
      color: #94a3b8;
      margin-top: 4px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .card-header-action {{
      flex-shrink: 0;
    }}

    .btn-launch {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: var(--accent);
      color: #064e3b;
      text-decoration: none;
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 700;
      transition: all 0.2s;
      box-shadow: 0 0 12px var(--accent-glow);
    }}

    .btn-launch:hover {{
      background: #34d399;
      transform: scale(1.05);
      color: #022c22;
      box-shadow: 0 0 18px rgba(16, 185, 129, 0.5);
    }}

    /* Card File list */
    .card-files {{
      padding: 12px 16px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      flex: 1;
    }}

    .file-item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 7px 10px;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.02);
      font-size: 13px;
      transition: background 0.15s;
    }}

    .file-item:hover {{
      background: rgba(255, 255, 255, 0.07);
    }}

    .file-link {{
      display: flex;
      align-items: center;
      gap: 8px;
      color: #e2e8f0;
      text-decoration: none;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      flex: 1;
    }}

    .file-link:hover {{
      color: var(--accent-blue);
    }}

    .file-icon {{
      font-size: 15px;
      flex-shrink: 0;
    }}

    .file-name {{
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-weight: 500;
    }}

    .file-tag-main {{
      background: rgba(16, 185, 129, 0.15);
      color: var(--accent);
      border: 1px solid rgba(16, 185, 129, 0.35);
      font-size: 10px;
      padding: 1px 6px;
      border-radius: 4px;
      margin-left: 6px;
      flex-shrink: 0;
      font-weight: 600;
    }}

    .file-meta {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-shrink: 0;
      margin-left: 10px;
    }}

    .file-size {{
      font-size: 11px;
      color: #64748b;
      font-family: monospace;
    }}

    .file-btn {{
      color: #94a3b8;
      font-size: 13px;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      padding: 2px 6px;
      border-radius: 4px;
      transition: all 0.15s;
    }}

    .file-btn:hover {{
      color: #fff;
      background: #334155;
    }}

    /* Root Files Grid */
    .root-files-card {{
      grid-column: 1 / -1;
    }}

    .root-files-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
      gap: 12px;
      padding: 16px 20px;
    }}

    /* Empty state */
    .empty-state {{
      text-align: center;
      padding: 70px 20px;
      color: var(--text-muted);
      background: var(--card-bg);
      border: 1px dashed var(--card-border);
      border-radius: 16px;
      margin: 20px 0;
      display: none;
    }}

    .empty-state h3 {{
      color: #f1f5f9;
      font-size: 18px;
    }}

    .empty-state p {{
      margin-top: 8px;
      font-size: 14px;
    }}

    /* Footer */
    footer {{
      margin-top: 60px;
      padding-top: 28px;
      border-top: 1px solid var(--card-border);
      text-align: center;
      font-size: 13px;
      color: #64748b;
    }}

    footer a {{
      color: var(--accent);
      text-decoration: none;
    }}

    footer a:hover {{
      text-decoration: underline;
    }}

    @media (max-width: 640px) {{
      .poc-grid {{
        grid-template-columns: 1fr;
      }}
      .header-top {{
        flex-direction: column;
        align-items: flex-start;
      }}
      .brand-text h1 {{
        font-size: 22px;
      }}
    }}
  </style>
</head>
<body>
  <div class="bg-glow"></div>

  <div class="container">
    <header>
      <div class="header-top">
        <div class="brand">
          <div class="brand-icon">🛡️</div>
          <div class="brand-text">
            <h1>Security PoC Directory</h1>
            <p>Vulnerability demonstration index & exploit testbed navigation</p>
          </div>
        </div>
        <div class="header-actions">
          <a class="repo-link" href="https://github.com/nuribnuu/poc-security" target="_blank" rel="noopener">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
            </svg>
            nuribnuu/poc-security
          </a>
        </div>
      </div>

      <div class="stats-row">
        <div class="stat-badge">
          📁 Total PoC Suites: <span class="stat-value">{total_suites}</span>
        </div>
        <div class="stat-badge">
          📄 Total Files: <span class="stat-value">{total_files}</span>
        </div>
        <div class="stat-badge">
          🏷️ Categories: <span class="stat-value">{len(categories)}</span>
        </div>
        <div class="stat-badge">
          ⚡ Offline Ready: <span class="stat-value" style="color:var(--accent);">Active</span>
        </div>
      </div>
    </header>

    <div class="controls-panel">
      <div class="search-bar">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input type="text" id="searchInput" placeholder="Search PoC name, directory, payload or file (e.g. apk, addressbar, download, xss)..." autocomplete="off">
        <span class="search-shortcut">/</span>
      </div>

      <div class="filter-tags" id="categoryFilters">
        <button class="filter-tag active" data-cat="all">All PoCs</button>
"""

for cat in categories:
    html_code += f'        <button class="filter-tag" data-cat="{cat}">{cat}</button>\n'

html_code += f"""      </div>
    </div>

    <div class="action-bar">
      <span id="resultsCount">Showing all items</span>
    </div>

    <div class="empty-state" id="emptyState">
      <h3>🔍 No PoCs Found</h3>
      <p>No proof of concept matches your search filter. Try clearing the search or category.</p>
    </div>

    <div id="contentArea">
"""

# Render Root Files Section
if root_files:
    root_search_text = "root " + " ".join(f"{rf['name']} {rf['title']}" for rf in root_files).lower()
    html_code += f"""
      <div class="category-section" data-category="Root PoCs & Exploits">
        <div class="category-title">
          <span>⚡ Root PoCs & Individual Exploits</span>
          <span class="count">{len(root_files)} files</span>
        </div>
        <div class="poc-card root-files-card" data-category="Root PoCs & Exploits" data-search="{html.escape(root_search_text)}">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-dir-name">Root Directory Testcases</div>
              <div class="card-desc">Standalone XSS, CSRF, and Information Disclosure PoCs in repository root</div>
            </div>
          </div>
          <div class="root-files-grid">
"""
    for rf in root_files:
        icon = '🌐' if rf['ext'] == '.html' else '📄'
        title_attr = f' title="{html.escape(rf["title"])}"' if rf['title'] else ''
        title_disp = f' <span style="color:#94a3b8;font-size:11px;">({html.escape(rf["title"])})</span>' if rf['title'] else ''
        rf_search = f"{rf['name']} {rf['title']}".lower()
        html_code += f"""            <div class="file-item root-file-item" data-search="{html.escape(rf_search)}">
              <a class="file-link" href="./{rf['rel_path']}" target="_blank"{title_attr}>
                <span class="file-icon">{icon}</span>
                <span class="file-name">{rf['name']}{title_disp}</span>
              </a>
              <div class="file-meta">
                <span class="file-size">{rf['size_formatted']}</span>
                <a class="file-btn" href="./{rf['rel_path']}" target="_blank" title="Open in new tab">↗</a>
              </div>
            </div>\n"""
    html_code += """          </div>
        </div>
      </div>
"""

# Render Directory Categories
current_cat = None
for d in directories:
    if d['category'] != current_cat:
        if current_cat is not None:
            html_code += """        </div>
      </div>\n"""
        current_cat = d['category']
        cat_count = sum(1 for x in directories if x['category'] == current_cat)
        html_code += f"""
      <div class="category-section" data-category="{current_cat}">
        <div class="category-title">
          <span>📁 {current_cat}</span>
          <span class="count">{cat_count} suites</span>
        </div>
        <div class="poc-grid">\n"""

    search_meta = f"{d['dir_path']} {d['title']} {d['category']} " + " ".join(f['name'] for f in d['files'])
    clean_title = d['title'] if d['title'] else 'Proof of Concept suite'
    
    html_code += f"""          <div class="poc-card" data-category="{d['category']}" data-search="{html.escape(search_meta.lower())}">
            <div class="card-header">
              <div class="card-title-group">
                <div class="card-dir-name" title="{d['dir_path']}">
                  📂 {d['dir_path']}
                </div>
                <div class="card-desc" title="{html.escape(clean_title)}">
                  {html.escape(clean_title)}
                </div>
              </div>
              <div class="card-header-action">
                <a class="btn-launch" href="./{d['main_index_path']}" target="_blank" title="Launch PoC">
                  <span>Run</span> ↗
                </a>
              </div>
            </div>
            <div class="card-files">\n"""

    for f in d['files']:
        ext = f['ext'].lower()
        if ext in ['.apk', '.apks']:
            icon = '🤖'
        elif ext in ['.exe']:
            icon = '⚙️'
        elif ext in ['.png', '.jpg', '.jpeg']:
            icon = '🖼️'
        elif ext in ['.js', '.webmanifest']:
            icon = '📜'
        elif ext in ['.txt']:
            icon = '📄'
        else:
            icon = '🌐'

        main_badge = '<span class="file-tag-main">Main</span>' if f.get('is_main') else ''
        title_attr = f' title="{html.escape(f["title"])}"' if f['title'] else ''
        
        html_code += f"""              <div class="file-item">
                <a class="file-link" href="./{f['rel_path']}" target="_blank"{title_attr}>
                  <span class="file-icon">{icon}</span>
                  <span class="file-name">{f['name']}</span>
                  {main_badge}
                </a>
                <div class="file-meta">
                  <span class="file-size">{f['size_formatted']}</span>
                  <a class="file-btn" href="./{f['rel_path']}" target="_blank" title="Open file">↗</a>
                </div>
              </div>\n"""

    html_code += """            </div>
          </div>\n"""

if current_cat is not None:
    html_code += """        </div>
      </div>\n"""

html_code += """    </div>

    <footer>
      <p>Security Research & PoC Directory &bull; Sourced from <a href="https://github.com/nuribnuu/poc-security" target="_blank" rel="noopener">nuribnuu/poc-security</a></p>
      <p style="margin-top: 6px; font-size: 11px;">⚠️ For educational and authorized security research purposes only.</p>
    </footer>
  </div>

  <script>
    const searchInput = document.getElementById('searchInput');
    const filterButtons = document.querySelectorAll('.filter-tag');
    const sections = document.querySelectorAll('.category-section');
    const emptyState = document.getElementById('emptyState');
    const resultsCount = document.getElementById('resultsCount');

    let currentCategory = 'all';

    function filterItems() {
      const query = searchInput.value.toLowerCase().trim();
      let visibleSuitesCount = 0;

      sections.forEach(sec => {
        const secCat = sec.getAttribute('data-category');
        const isCatMatch = (currentCategory === 'all' || currentCategory === secCat);
        
        let secVisibleCount = 0;
        const secCards = sec.querySelectorAll('.poc-card');

        secCards.forEach(card => {
          const cardSearchData = (card.getAttribute('data-search') || '').toLowerCase();
          const matchesSearch = query === '' || cardSearchData.includes(query);
          const matchesCategory = isCatMatch || (currentCategory === card.getAttribute('data-category'));

          // If this is root-files-card, also filter individual root items
          if (card.classList.contains('root-files-card')) {
            const rootItems = card.querySelectorAll('.root-file-item');
            let matchingRootItems = 0;
            rootItems.forEach(item => {
              const itemSearch = (item.getAttribute('data-search') || '').toLowerCase();
              if (query === '' || itemSearch.includes(query)) {
                item.style.display = '';
                matchingRootItems++;
              } else {
                item.style.display = 'none';
              }
            });

            if (matchesCategory && (query === '' || matchingRootItems > 0)) {
              card.style.display = '';
              secVisibleCount++;
              visibleSuitesCount += matchingRootItems || 1;
            } else {
              card.style.display = 'none';
            }
          } else {
            if (matchesSearch && matchesCategory) {
              card.style.display = '';
              secVisibleCount++;
              visibleSuitesCount++;
            } else {
              card.style.display = 'none';
            }
          }
        });

        // Hide section if no cards inside match
        if (secVisibleCount > 0) {
          sec.style.display = '';
        } else {
          sec.style.display = 'none';
        }
      });

      if (visibleSuitesCount === 0) {
        emptyState.style.display = 'block';
        resultsCount.textContent = 'No matching items';
      } else {
        emptyState.style.display = 'none';
        resultsCount.textContent = `Showing ${visibleSuitesCount} matching item${visibleSuitesCount === 1 ? '' : 's'}`;
      }
    }

    searchInput.addEventListener('input', filterItems);

    filterButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        filterButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentCategory = btn.getAttribute('data-cat');
        filterItems();
      });
    });

    // Keyboard shortcut '/' to search
    window.addEventListener('keydown', (e) => {
      if (e.key === '/' && document.activeElement !== searchInput) {
        e.preventDefault();
        searchInput.focus();
      }
      if (e.key === 'Escape' && document.activeElement === searchInput) {
        searchInput.value = '';
        filterItems();
        searchInput.blur();
      }
    });
  </script>
</body>
</html>
"""

output_path = os.path.join(base_dir, 'index.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_code)

print(f"Generated {output_path} successfully ({len(html_code)} bytes).")
