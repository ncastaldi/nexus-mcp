You are given a well-formatted markdown file. Your task is to convert it into a modern, visually appealing HTML document. Follow these instructions:

1) Analyze the Markdown Structure:

- Identify all headings, lists, tables, code blocks, blockquotes, and other markdown elements.
- Note the hierarchy and indentation to inform the HTML structure and CSS styling.

2) Generate HTML

- Convert each markdown element to its semantic HTML equivalent (e.g., # to <h1>, ## to <h2>, - to <ul><li>, etc.).
- Convert Markdown image syntax (`![alt text](image_path)`) to HTML `<img>` tags, preserving the `src` and `alt` attributes, and apply modern styling (e.g., `max-width:100%; margin: 16px 0; border-radius: 4px;`).
- Preserve the document’s logical structure and sectioning.

3) Apply Modern CSS

- Use a clean, modern font (e.g., 'Segoe UI', Arial, sans-serif).
- Add a centered, card-like container with padding, rounded corners, and a subtle box-shadow.
- Style headings with distinct colors and spacing for hierarchy.
- Style lists, tables, and code blocks for clarity and readability.
- Ensure responsive design for mobile devices.
- Use the markdown’s own formatting (e.g., heading levels, list nesting, table presence) to influence spacing, font sizes, and section separation in the CSS.

4) Header Row

- At the top, include a header row with the document title (from the first heading) and a company logo (use a placeholder or provided URL).

5) Meta Information

- If the markdown includes frontmatter (YAML or similar), display all metadata fields found (not just title, description, version, author, date) in a styled block at the top. This ensures custom fields like `applies_to`, `issue`, or others are visible for KBAs/Guides.
- If a `logo` field is present in the frontmatter, use its value as the logo URL in the header row; otherwise, use the default logo URL.
- Use the YAML `title` as the main document title (`<h1>`). If both YAML and Markdown H1 exist, suppress the Markdown H1 in the HTML output to avoid duplicate titles.


6) Accessibility & Best Practices

- Use semantic HTML tags.
- Ensure sufficient color contrast and readable font sizes.
- Add alt text for images.
- If a blockquote starts with `Note:`, `Warning:`, or `Tip:`, add a CSS class and icon/color for visual distinction (e.g., blue for Note, yellow for Warning, green for Tip). This helps highlight important callouts in KBAs/Guides.
- If multiple H1s or inline HTML are detected, warn or normalize as needed to maintain clean output.


7) Output

- Return a complete HTML file with embedded CSS (in a <style> block in the <head>) in the "Documentation\HTML" folder.
- Name the new file using the `type` and `title`from the frontmatter. Replace spaces with underscores and appending `.html` (e.g., `SOP_Escalation_Procedures.html`).
- The HTML should be ready to use and visually modern, reflecting the structure and intent of the original markdown.
- Ensure:
  - The meta block displays all frontmatter fields present.
  - Only one H1 (from YAML title) is rendered at the top.
  - Blockquotes with callout keywords are visually distinct.
  - The logo is sourced from frontmatter if available.
  - Optionally, output a warning if multiple H1s or inline HTML are found in the source.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>[Document Title]</title>
  <style>
    /* Modern CSS based on markdown structure */
    body {
      font-family: 'Segoe UI', Arial, sans-serif;
      margin: 0;
      padding: 0;
        background-color: #f4f4f9;
        color: #333;
    }
    main {
      max-width: 800px;
      margin: 50px auto;
      padding: 20px;
        background: #fff;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .header-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }
    .header-row h1 {
      font-size: 28px;
      margin: 0;
      color: #0078d4;
    }
    .header-row img {
      max-height: 50px;
    }
    .meta {
      font-size: 14px;
      color: #666;
      margin-bottom: 20px;
    }
    h2, h3, h4 {
      color: #005a9e;
    }
    ul, ol {
      margin-left: 20px;
      margin-bottom: 20px;
    }
    code {
      font-family: 'Courier New', Courier, monospace;
      background-color: #eef;
      padding: 2px 4px;
      border-radius: 4px;
    }
    pre {
      background-color: #eef;
      padding: 10px;
      border-radius: 4px;
      overflow-x: auto;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 20px;
    }
    th, td {
      border: 1px solid #ddd;
      padding: 8px;
      text-align: left;
    }
    th {
      background-color: #0078d4;
      color: white;
    }
    blockquote {
      margin: 0;
      padding: 10px 20px;
      background-color: #f9f9f9;
      border-left: 5px solid #0078d4;
    }
    /* Responsive design */
    @media (max-width: 600px) {
      .header-row {
        flex-direction: column;
        align-items: flex-start;
      }
      .header-row h1 {
        font-size: 24px;
      }
      .meta {
        font-size: 12px;
      }
    }

  </style>
</head>
<body>
  <main>
    <div class="header-row">
      <h1>[Document Title]</h1>
      <img src="https://rwdn-uploads.s3.amazonaws.com/mcgl15001/production/54b7a8d305541296303508cec6e5dfb6.png" alt="Company Logo" style="height:60px; max-width:180px; object-fit:contain;">
    </div>
    <div class="meta">
      <strong>Description:</strong> ...<br>
      <strong>Version:</strong> ...<br>
      <strong>Author:</strong> ...<br>
      <strong>Date:</strong> ...
    </div>
    <!-- Converted markdown content here -->
  </main>
</body>
</html>
```
