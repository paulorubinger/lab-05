#!/usr/bin/env python3
"""
Generate PDF from markdown report.
Usage: python3 scripts/generate_pdf.py
"""

import sys
import os
import re
import tempfile
import subprocess
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def check_dependencies():
    """Check if required packages are installed."""
    try:
        import markdown
        import weasyprint
        return True, "All dependencies available"
    except ImportError as e:
        return False, f"Missing dependency: {e}"

def generate_pdf_weasyprint(md_path, pdf_path):
    """
    Generate PDF from markdown using weasyprint + markdown libraries.
    This is the primary method (pure Python, no external tools needed).
    """
    import markdown
    from weasyprint import HTML, CSS
    from io import BytesIO
    
    print(f"📖 Reading markdown from: {md_path}")
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert relative image paths to absolute paths
    print("🔄 Converting image paths to absolute...")
    md_dir = Path(md_path).parent
    def convert_image_paths(content):
        # Match markdown image syntax: ![alt](path)
        def replace_path(match):
            alt = match.group(1)
            path = match.group(2)
            # If path is relative, convert to absolute
            if not path.startswith('http') and not path.startswith('/'):
                abs_path = md_dir / path
                return f"![{alt}](file://{abs_path})"
            return match.group(0)
        return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_path, content)
    
    md_content = convert_image_paths(md_content)
    
    print("🔄 Converting markdown to HTML...")
    html_content = markdown.markdown(md_content, extensions=['extra', 'toc', 'tables'])
    
    # Wrap with HTML/CSS for better formatting
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
                background: white;
            }}
            h1, h2, h3, h4, h5, h6 {{
                color: #1f4788;
                margin-top: 1.5em;
                margin-bottom: 0.5em;
            }}
            h1 {{
                border-bottom: 3px solid #1f4788;
                padding-bottom: 10px;
                font-size: 28px;
            }}
            h2 {{
                font-size: 22px;
                border-left: 4px solid #1f4788;
                padding-left: 10px;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 1.5em 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 10px;
                text-align: left;
            }}
            th {{
                background-color: #1f4788;
                color: white;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            code {{
                background-color: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
            }}
            pre {{
                background-color: #f4f4f4;
                padding: 12px;
                border-radius: 5px;
                overflow-x: auto;
                border-left: 3px solid #1f4788;
            }}
            pre code {{
                background: none;
                padding: 0;
            }}
            blockquote {{
                border-left: 4px solid #ddd;
                padding-left: 15px;
                margin-left: 0;
                color: #777;
                font-style: italic;
            }}
            a {{
                color: #1f4788;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            img {{
                max-width: 100%;
                height: auto;
                margin: 1em 0;
            }}
            .figure {{
                text-align: center;
                margin: 2em 0;
            }}
            .figure img {{
                max-width: 80%;
                height: auto;
            }}
            .figure-caption {{
                font-style: italic;
                color: #777;
                margin-top: 0.5em;
            }}
            .toc {{
                background-color: #f9f9f9;
                padding: 15px;
                border-radius: 5px;
                margin: 2em 0;
            }}
            .toc ul {{
                list-style-position: inside;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    print("🔄 Converting HTML to PDF...")
    try:
        HTML(string=styled_html, base_url=str(md_dir)).write_pdf(pdf_path)
        print(f"✅ PDF saved to: {pdf_path}")
        return True
    except Exception as e:
        print(f"❌ Error with weasyprint: {e}")
        return False

def generate_pdf_pandoc(md_path, pdf_path):
    """
    Generate PDF from markdown using pandoc.
    This is an alternative method with better typography.
    """
    import subprocess
    
    print(f"📖 Reading markdown from: {md_path}")
    
    # Read and convert relative image paths to absolute paths
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    md_dir = Path(md_path).parent
    print("🔄 Converting image paths to absolute...")
    def convert_image_paths(content):
        def replace_path(match):
            alt = match.group(1)
            path = match.group(2)
            if not path.startswith('http') and not path.startswith('/'):
                abs_path = md_dir / path
                return f"![{alt}]({abs_path})"
            return match.group(0)
        return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_path, content)
    
    md_content = convert_image_paths(md_content)
    
    # Write temporary markdown with absolute paths
    temp_dir = tempfile.gettempdir()
    temp_md = Path(temp_dir) / 'report_temp.md'
    with open(temp_md, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    try:
        print("🔄 Converting with pandoc...")
        result = subprocess.run([
            'pandoc',
            str(temp_md),
            '-o', str(pdf_path),
            '--from=markdown+smart',
            '--pdf-engine=pdflatex',
            '-V', 'mainfont=DejaVu Sans',
            '-V', 'documentclass=article',
            '-V', 'papersize=a4',
            '-V', 'geometry:margin=2cm',
            '--toc',
            '--toc-depth=2',
            '--number-sections',
        ], capture_output=True, text=True, check=True)
        
        print(f"✅ PDF saved to: {pdf_path}")
        temp_md.unlink()  # Clean up temp file
        return True
    except FileNotFoundError:
        print("⚠️  pandoc not found")
        temp_md.unlink()  # Clean up temp file
        return False
    except subprocess.CalledProcessError as e:
        print(f"⚠️  pandoc error: {e.stderr}")
        temp_md.unlink()  # Clean up temp file
        return False

def main():
    # Paths
    md_path = PROJECT_ROOT / 'report' / 'report.md'
    pdf_path = PROJECT_ROOT / 'report' / 'report.pdf'
    
    # Verify markdown exists
    if not md_path.exists():
        print(f"❌ Error: {md_path} not found")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print("📚 PDF Generator for Academic Report")
    print(f"{'='*60}\n")
    
    # Try pandoc first (better quality)
    if generate_pdf_pandoc(md_path, pdf_path):
        print(f"\n{'='*60}")
        print("✨ Done!")
        print(f"{'='*60}\n")
        return
    
    # Fallback to weasyprint (pure Python, no system dependencies)
    print("\n🔄 Falling back to weasyprint...\n")
    
    # Check dependencies
    has_deps, msg = check_dependencies()
    if not has_deps:
        print(f"❌ {msg}")
        print("\n📦 Install required packages:")
        print("   pip install markdown weasyprint")
        sys.exit(1)
    
    # Generate with weasyprint
    try:
        if generate_pdf_weasyprint(md_path, pdf_path):
            print(f"\n{'='*60}")
            print("✨ Done!")
            print(f"{'='*60}\n")
        else:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
