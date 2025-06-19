import sys
import os
import csv
from html.parser import HTMLParser

class UnnamedTableExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_caption = False
        self.in_row = False
        self.in_cell = False
        self.current_table = []
        self.current_row = []
        self.current_cell = ""
        self.tables = []
        self.has_caption = False

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.in_table = True
            self.has_caption = False
            self.current_table = []
        elif tag == "caption" and self.in_table:
            self.in_caption = True
        elif tag == "tr" and self.in_table and not self.in_caption:
            self.in_row = True
            self.current_row = []
        elif tag in ("td", "th") and self.in_table and self.in_row:
            self.in_cell = True
            self.current_cell = ""

    def handle_endtag(self, tag):
        if tag == "caption" and self.in_table:
            self.in_caption = False
            self.has_caption = True
        elif tag == "table" and self.in_table:
            if not self.has_caption and self.current_table:
                self.tables.append(self.current_table)
            self.in_table = False
            self.current_table = []
        elif tag == "tr" and self.in_table and self.in_row:
            self.in_row = False
            if self.current_row:
                self.current_table.append(self.current_row)
            self.current_row = []
        elif tag in ("td", "th") and self.in_table and self.in_row and self.in_cell:
            self.in_cell = False
            self.current_row.append(self.current_cell.strip())

    def handle_data(self, data):
        if self.in_cell and self.in_table and self.in_row:
            self.current_cell += data

def save_tables_to_csv(tables):
    for idx, table in enumerate(tables, 1):
        filename = f"unnamed_table_{idx}.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for row in table:
                writer.writerow(row)
        print(f"Extracted unnamed table #{idx} -> {filename}")

def main(html_file):
    if not os.path.isfile(html_file):
        print(f"File not found: {html_file}")
        sys.exit(1)
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    parser = UnnamedTableExtractor()
    parser.feed(html_content)
    if parser.tables:
        save_tables_to_csv(parser.tables)
    else:
        print("No unnamed tables found.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_unnamed_tables.py <misra_report.html>")
        sys.exit(1)
    main(sys.argv[1])


