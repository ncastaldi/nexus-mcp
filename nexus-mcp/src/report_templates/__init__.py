"""report_templates — multi-format rendering for Nexus output reports.

Usage
-----
from report_templates import ReportFormat, render

# Markdown (default — no extra deps)
md_str   = render(markdown, ReportFormat.MD,   title="My Report")

# HTML (requires: pip install markdown)
html_str = render(markdown, ReportFormat.HTML, title="My Report")

# PDF  (requires: pip install weasyprint markdown)
#       On Windows: also install GTK3 runtime DLLs
#       https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows
pdf_bytes = render(markdown, ReportFormat.PDF, title="My Report")

# DOCX (requires: pip install python-docx)
docx_bytes = render(markdown, ReportFormat.DOCX, title="My Report")

Install all at once
-------------------
pip install "nexus-mcp[report]"
"""

from ._renderer import ReportFormat, render

__all__ = ["ReportFormat", "render"]
