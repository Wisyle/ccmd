"""Textual CSS — vibrant high-chroma theme."""

CSS = """
Screen {
    background: #0a0a0f;
    color: #e8e8f0;
}

#banner {
    color: #00ffc8;
    text-style: bold;
    padding: 0 1;
    height: auto;
}

#subtitle {
    color: #c84bff;
    padding: 0 2 0 2;
    height: 1;
}

#agent-bar {
    color: #e8e8f0;
    padding: 0 2 1 2;
    height: 1;
}

#path-bar {
    color: #e8e8f0;
    padding: 0 2 1 2;
    height: auto;
}

#filter {
    dock: top;
    margin: 0 1 1 1;
    background: #12121a;
    border: tall #2a2a40;
    color: #e8e8f0;
    padding: 0 1;
}

#filter:focus {
    border: tall #00ffc8;
}

#main {
    layout: horizontal;
    height: 1fr;
    padding: 0 1;
}

#projects-panel {
    width: 3fr;
    height: 1fr;
    border: round #2a2a40;
    background: #12121a;
    padding: 0 1;
}

#projects-panel:focus-within {
    border: round #00ffc8;
}

#detail-panel {
    width: 2fr;
    height: 1fr;
    border: round #2a2a40;
    background: #12121a;
    padding: 0 1;
    margin-left: 1;
}

.panel-title {
    color: #00ffc8;
    text-style: bold;
    padding: 0 0 1 0;
}

#project-list {
    height: 1fr;
    background: #12121a;
}

#project-list > .option-list--option-highlighted {
    background: #1a2a28;
    color: #00ffc8;
}

#detail {
    height: 1fr;
    color: #e8e8f0;
}

#footer-bar {
    dock: bottom;
    height: 1;
    background: #12121a;
    color: #6a6a80;
    padding: 0 2;
}

#status {
    color: #39ff14;
    padding: 0 1;
    height: 1;
}

#spinner-line {
    color: #c84bff;
    height: 1;
    padding: 0 2;
}

/* Agent screen */
#agent-grid {
    layout: grid;
    grid-size: 4;
    grid-gutter: 1 1;
    padding: 1;
    height: 1fr;
}

.agent-card {
    border: round #2a2a40;
    background: #12121a;
    height: 7;
    padding: 1;
    content-align: center middle;
}

.agent-card.-installed {
    border: round #39ff14;
}

.agent-card.-missing {
    border: round #6a6a80;
    color: #6a6a80;
}

.agent-card.-focus {
    border: round #00ffc8;
    background: #1a1a28;
}

/* Sessions */
#session-table {
    height: 1fr;
}

/* Generic */
Button {
    background: #1a1a28;
    color: #e8e8f0;
    border: none;
    margin: 0 1;
}

Button:hover {
    background: #00ffc8;
    color: #0a0a0f;
}

Input {
    background: #12121a;
    border: tall #2a2a40;
}

Input:focus {
    border: tall #00ffc8;
}

DataTable {
    background: #12121a;
}

DataTable > .datatable--cursor {
    background: #1a2a28;
    color: #00ffc8;
}
"""
