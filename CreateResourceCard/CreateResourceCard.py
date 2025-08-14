
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML Card Snippet Generator (Tkinter)
-------------------------------------
A small desktop GUI to generate an HTML <li> "resource-card" snippet with
customizable attributes (comment title, data-* attributes, i18n keys, and link).

How to run:
    python html_card_generator.py

Python stdlib only. Tested with Python 3.9+.
"""

import re
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from html import escape

APP_TITLE = "HTML Card Snippet Generator"

def slugify_for_i18n(s: str) -> str:
    """
    Convert a name to a lowercase, no-spaces, alphanumeric-only slug suitable
    for i18n keys, e.g. "Doja SDK" -> "dojasdk".
    """
    s = s.lower()
    # Remove any character that's not a-z / 0-9
    s = re.sub(r'[^a-z0-9]+', '', s)
    return s

def slugify_simple(s: str) -> str:
    """
    Slightly different slugifier for labels (category/tag) when used in i18n keys.
    This keeps letters and digits; removes everything else.
    Example: "Tools & Utilities" -> "toolsutilities"
    """
    return slugify_for_i18n(s)

def default_title_from_name(name: str) -> str:
    """
    A helpful default: return the name in Title Case.
    """
    if not name:
        return ""
    return " ".join(w.capitalize() for w in re.split(r'\s+', name.strip()))

def build_html(card_name: str,
               category: str,
               tags_csv: str,
               search_terms: str,
               visible_title: str,
               visible_desc: str,
               href: str,
               update_meta_pills: bool = True) -> str:
    """
    Build the HTML snippet string from the provided fields.
    """
    # Prepare slugs and labels
    name_slug = slugify_for_i18n(card_name)
    if not name_slug:
        raise ValueError("Card Name must contain at least one alphanumeric character.")

    cat = (category or "").strip()
    if not cat:
        raise ValueError("Category cannot be empty.")
    cat_slug = slugify_simple(cat)

    # Tags list (for attributes); also compute first tag for the pill
    raw_tags = [t.strip() for t in (tags_csv or "").split(",") if t.strip()]
    tags_attr = ",".join(raw_tags)
    first_tag = raw_tags[0] if raw_tags else ""
    first_tag_slug = slugify_simple(first_tag) if first_tag else ""

    # Labels for the visible pills (fallback text)
    cat_label = cat if cat else "Category"
    first_tag_label = first_tag if first_tag else "Tag"

    # Visible text fallback
    if not visible_title.strip():
        visible_title = default_title_from_name(card_name)
    if not visible_desc.strip():
        visible_desc = f"{default_title_from_name(card_name)} resource."

    # Escape visible text (content), not attributes for i18n keys
    v_title = escape(visible_title)
    v_desc  = escape(visible_desc)
    v_cat_label = escape(cat_label)
    v_first_tag_label = escape(first_tag_label)

    # Attributes
    data_category = escape(cat, quote=True)
    data_tags = escape(tags_attr, quote=True)
    data_search = escape((search_terms or "").strip(), quote=True)
    href_attr = escape((href or "").strip(), quote=True)

    # i18n keys for title/desc use the 'name_slug'
    title_i18n = f"resources.cards.{name_slug}.title"
    desc_i18n  = f"resources.cards.{name_slug}.desc"

    # i18n keys for pills (optional)
    if update_meta_pills and cat_slug:
        cat_i18n = f"resources.categories.{cat_slug}"
    else:
        cat_i18n = "resources.categories.tools"

    if update_meta_pills and first_tag_slug:
        tag_i18n = f"resources.tag.{first_tag_slug}"
    else:
        tag_i18n = "resources.tag.emulator"

    # Compose the HTML
    html = f"""<!-- Card: {escape(card_name)} -->
<li class="cs-li resource-card"
    data-category="{data_category}"
    data-tags="{data_tags}"
    data-search="{data_search}">
  <div class="cs-flex">
    <div>
      <h3 class="cs-h3" data-i18n="{title_i18n}">{v_title}</h3>
      <p class="cs-li-text" data-i18n="{desc_i18n}">
        {v_desc}
      </p>
      <div class="meta">
        <span class="pill" data-i18n="{cat_i18n}">{v_cat_label}</span>
        <span class="pill" data-i18n="{tag_i18n}">{v_first_tag_label}</span>
      </div>
      <div class="resource-actions">
        <a href="{href_attr}" target="_blank" rel="noopener" class="btn btn-primary" data-i18n="resources.open">Open</a>
      </div>
    </div>
  </div>
</li>"""
    return html

class CardGUI(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=(12, 12, 12, 12))
        self.master.title(APP_TITLE)

        # StringVars for fields
        self.card_name = tk.StringVar(value="Card Name")
        self.category = tk.StringVar(value="tools, docs, community, repos")
        self.tags = tk.StringVar(value="emulator,info,guide")
        self.search = tk.StringVar(value="SEARCH KEYWORD")
        self.visible_title = tk.StringVar(value="Visible Card Title")
        self.visible_desc = tk.StringVar(value="Visible Card Description")
        self.href = tk.StringVar(value="Link to resource website")
        self.update_pills = tk.BooleanVar(value=True)

        # Layout: grid
        self.columnconfigure(1, weight=1)

        row = 0
        self._add_labeled_entry("Card Name", self.card_name, row, help_="Used for comment and i18n key (no spaces).")
        row += 1

        self._add_labeled_entry("Category", self.category, row, help_='data-category and category pill (e.g., "tools").')
        row += 1

        self._add_labeled_entry("Tags (comma-separated)", self.tags, row, help_='data-tags. First tag becomes the tag pill.')
        row += 1

        self._add_labeled_entry("Search terms (space-separated)", self.search, row, help_='data-search (e.g., "doja emulator docomo").')
        row += 1

        self._add_labeled_entry("Visible Title", self.visible_title, row, help_="Fallback text inside <h3> if i18n missing.")
        row += 1

        self._add_labeled_entry("Visible Description", self.visible_desc, row, help_="Fallback text inside <p> if i18n missing.")
        row += 1

        self._add_labeled_entry("Link URL (href)", self.href, row, help_="Target for the 'Open' button.")
        row += 1

        # Update meta pills checkbox
        cb = ttk.Checkbutton(self, text="Update category/tag pill i18n keys from Category & first Tag",
                             variable=self.update_pills)
        cb.grid(row=row, column=0, columnspan=2, sticky="w", pady=(4, 8))
        row += 1

        # Buttons
        btns = ttk.Frame(self)
        btns.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        btns.columnconfigure(0, weight=1)
        btns.columnconfigure(1, weight=0)
        btns.columnconfigure(2, weight=0)

        gen_btn = ttk.Button(btns, text="Generate HTML", command=self.on_generate)
        gen_btn.grid(row=0, column=0, sticky="w")

        copy_btn = ttk.Button(btns, text="Copy to Clipboard", command=self.copy_to_clipboard)
        copy_btn.grid(row=0, column=1, padx=(8, 0))

        save_btn = ttk.Button(btns, text="Save to FileÅc", command=self.save_to_file)
        save_btn.grid(row=0, column=2, padx=(8, 0))

        # Output textbox
        self.output = tk.Text(self, height=20, wrap="word")
        self.output.grid(row=row+1, column=0, columnspan=2, sticky="nsew")
        self.rowconfigure(row+1, weight=1)

        # Initial generation
        self.on_generate()

    def _add_labeled_entry(self, label, var, row, help_=""):
        lbl = ttk.Label(self, text=label)
        lbl.grid(row=row, column=0, sticky="w", padx=(0, 8), pady=2)
        entry = ttk.Entry(self, textvariable=var)
        entry.grid(row=row, column=1, sticky="ew", pady=2)
        if help_:
            help_lbl = ttk.Label(self, text=help_, foreground="#666")
            help_lbl.grid(row=row+1, column=1, sticky="w", pady=(0, 6))

    def on_generate(self):
        try:
            html = build_html(
                card_name=self.card_name.get(),
                category=self.category.get(),
                tags_csv=self.tags.get(),
                search_terms=self.search.get(),
                visible_title=self.visible_title.get(),
                visible_desc=self.visible_desc.get(),
                href=self.href.get(),
                update_meta_pills=self.update_pills.get(),
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, html)

    def copy_to_clipboard(self):
        html = self.output.get("1.0", tk.END).strip()
        if not html:
            self.on_generate()
            html = self.output.get("1.0", tk.END).strip()
        self.clipboard_clear()
        self.clipboard_append(html)
        messagebox.showinfo("Copied", "The HTML snippet has been copied to the clipboard.")

    def save_to_file(self):
        html = self.output.get("1.0", tk.END).strip()
        if not html:
            self.on_generate()
            html = self.output.get("1.0", tk.END).strip()

        filename = filedialog.asksaveasfilename(
            title="Save HTML Snippet",
            defaultextension=".html",
            filetypes=[("HTML files", "*.html;*.htm"), ("All files", "*.*")],
            initialfile=f"{slugify_for_i18n(self.card_name.get()) or 'card'}.html",
        )
        if not filename:
            return
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html + "\n")
            messagebox.showinfo("Saved", f"Saved to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

def main():
    root = tk.Tk()
    # Ensure decent default sizing
    root.geometry("900x700")
    # Use ttk styling
    try:
        style = ttk.Style(root)
        # Use platform theme if available
        if sys.platform == "win32":
            style.theme_use("vista")
        elif sys.platform == "darwin":
            style.theme_use("aqua")
        else:
            style.theme_use("clam")
    except Exception:
        pass

    CardGUI(root).pack(fill="both", expand=True)
    root.mainloop()

if __name__ == "__main__":
    main()
