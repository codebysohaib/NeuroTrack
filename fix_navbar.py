import os, glob

css_file = r'NeuroTrack-Frontend/css/style.css'
with open(css_file, 'r', encoding='utf-8') as f:
    css = f.read()

old_auth = '''/* ── Auth Bar ── */
.auth-status-bar {
  background: var(--surface-2);
  border-bottom: 1px solid var(--border);
  padding: 8px 0;
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.auth-status-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--surface);
  padding: 4px 12px;
  border-radius: 20px;
  border: 1px solid var(--border);
}'''

new_auth = '''/* ── Auth Bar ── */
.auth-status-bar {
  background: var(--surface-2);
  border-bottom: 1px solid var(--border);
  padding: 10px 0;
  min-height: 48px;
  font-size: 0.8125rem;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
}

.auth-status-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.user-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--surface);
  padding: 6px 14px;
  border-radius: 20px;
  border: 1px solid var(--border);
  line-height: 1;
}

#authActionText {
  display: flex;
  align-items: center;
  line-height: 1;
}'''

css = css.replace(old_auth, new_auth)

old_media = '''.nav-links {
    position: fixed;
    top: 0;
    right: -100%;
    width: 80%;
    max-width: 300px;
    height: 100vh;
    background: var(--surface);
    flex-direction: column;
    padding: 100px 24px;
    box-shadow: -10px 0 30px rgba(0,0,0,0.1);
    gap: 16px;
  }
  
  .nav-links.show { right: 0; }'''

new_media = '''.nav-links {
    position: fixed;
    top: 0;
    right: -100%;
    width: 80%;
    max-width: 300px;
    height: 100vh;
    background: var(--surface);
    flex-direction: column;
    padding: 100px 24px;
    box-shadow: -10px 0 30px rgba(0,0,0,0.1);
    gap: 16px;
    visibility: hidden;
    transition: right 0.3s ease, visibility 0.3s;
  }
  
  .nav-links.show { 
    right: 0; 
    visibility: visible;
  }'''

css = css.replace(old_media, new_media)

with open(css_file, 'w', encoding='utf-8') as f:
    f.write(css)

print('CSS updated.')

html_files = glob.glob('NeuroTrack-Frontend/*.html')
for html_file in html_files:
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    html = html.replace("const navToggle = document.getElementById('navToggle');\n    const navLinks = document.getElementById('navLinks');", "")
    html = html.replace("navToggle.onclick = () => {\n      navLinks.classList.toggle('show');\n      navToggle.textContent = navLinks.classList.contains('show') ? '✕' : '☰';\n    };", "")
    html = html.replace("navToggle.addEventListener('click', () => {\n      navLinks.classList.toggle('show');\n      navToggle.textContent = navLinks.classList.contains('show') ? '✕' : '☰';\n    });", "")
    
    reliable_script = '''
  <script>
    document.addEventListener('DOMContentLoaded', () => {
      const navToggle = document.getElementById('navToggle');
      const navLinks = document.getElementById('navLinks');
      if(navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
          navLinks.classList.toggle('show');
          navToggle.textContent = navLinks.classList.contains('show') ? '✕' : '☰';
        });
        document.querySelectorAll('.nav-links a').forEach(link => {
          link.addEventListener('click', () => {
            navLinks.classList.remove('show');
            navToggle.textContent = '☰';
          });
        });
      }
    });
  </script>
</body>'''
    
    if 'id="navToggle"' in html and 'document.addEventListener(\'DOMContentLoaded\'' not in html:
        html = html.replace('</body>', reliable_script)
        
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)
        
print('HTML updated.')
