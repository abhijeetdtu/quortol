"""
Base64 Encoding Script for West Africa Historical Impact Charts
Converts PNG charts to base64 data URIs for embedding in HTML, Markdown, or JSON
"""

import base64
from pathlib import Path
import json

FIGURES = Path("figures")

def encode_png_to_base64(filename):
    """Encode PNG to base64 data URI"""
    png_path = FIGURES / filename
    
    if not png_path.exists():
        print(f"[ERROR] {filename} not found!")
        return None
    
    encoded = base64.b64encode(png_path.read_bytes()).decode("utf-8")
    data_uri = f"data:image/png;base64,{encoded}"
    
    return {
        "filename": filename,
        "data_uri": data_uri,
        "raw_base64": encoded,
        "mime_type": "image/png"
    }


def encode_all_charts():
    """Encode all 8 charts"""
    charts = [
        "slave_trade_routes.png",
        "gold_trade_volume.png",
        "slave_trade_volume.png",
        "domesticated_crops.png",
        "principal_routes.png",
        "influence_chains.png",
        "statistical_analysis.png",
        "total_exports.png",
    ]
    
    encoded_charts = []
    for chart in charts:
        result = encode_png_to_base64(chart)
        if result:
            encoded_charts.append(result)
            print(f"[OK] {chart} encoded ({len(result['raw_base64'])} chars)")
    
    return encoded_charts


def save_json_payload(encoded_charts, filename="charts_base64.json"):
    """Save encoded charts as JSON payload"""
    payload = {
        "version": "1.0",
        "created": "2026-05-15",
        "charts": encoded_charts,
        "total_charts": len(encoded_charts)
    }
    
    output_path = Path("docs") / filename
    output_path.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8"
    )
    
    print(f"\n[SAVED] JSON payload: {output_path}")
    return output_path


def save_markdown_embed(encoded_charts, filename="charts_embedded.md"):
    """Save charts as Markdown with embedded base64 images"""
    markdown_content = "# West Africa Historical Impact - Embedded Charts\n\n"
    
    for chart in encoded_charts:
        chart_filename = chart["filename"]
        data_uri = chart["data_uri"]
        
        # Extract chart name from filename
        chart_name = chart_filename.replace(".png", "").replace("_", " ").title()
        
        markdown_content += f"## {chart_name}\n\n"
        markdown_content += f"![{chart_name}]({data_uri})\n\n"
        markdown_content += "---\n\n"
    
    output_path = Path("docs") / filename
    output_path.write_text(markdown_content, encoding="utf-8")
    
    print(f"[SAVED] Markdown embed: {output_path}")
    return output_path


def save_html_embed(encoded_charts, filename="charts_embedded.html"):
    """Save charts as HTML with embedded base64 images"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>West Africa Historical Impact - Embedded Charts</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #F5F5F5;
        }
        .chart-section {
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .chart-section h2 {
            color: #1B5E20;
            margin-bottom: 10px;
        }
        img {
            max-width: 100%;
            height: auto;
        }
        .caption {
            font-size: 12px;
            color: #777;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <h1 style="color: #1B5E20; text-align: center;">West Africa Historical Impact</h1>
"""
    
    for chart in encoded_charts:
        chart_filename = chart["filename"]
        data_uri = chart["data_uri"]
        chart_name = chart_filename.replace(".png", "").replace("_", " ").title()
        
        html_content += f"""
    <div class="chart-section">
        <h2>{chart_name}</h2>
        <img src="{data_uri}" alt="{chart_name}" />
        <p class="caption">Quortol | Source: Historical Data Archives</p>
    </div>
"""
    
    html_content += """
</body>
</html>
"""
    
    output_path = Path("docs") / filename
    output_path.write_text(html_content, encoding="utf-8")
    
    print(f"[SAVED] HTML embed: {output_path}")
    return output_path


if __name__ == "__main__":
    print("Encoding West Africa historical impact charts to base64...\n")
    
    encoded_charts = encode_all_charts()
    
    print(f"\nTotal charts encoded: {len(encoded_charts)}\n")
    
    # Save different formats
    save_json_payload(encoded_charts)
    save_markdown_embed(encoded_charts)
    save_html_embed(encoded_charts)
    
    print("\n[COMPLETE] All encoding formats saved to docs/")
