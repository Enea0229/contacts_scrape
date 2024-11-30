import re
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
from typing import List, Tuple


def setup_database(db_name: str = "contacts.db") -> None:
    """
    建立SQLite資料庫並創建資料表contacts.db（如果還沒建立）
    db_name: SQLite 資料庫檔案名稱。
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            iid INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            title TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()
    conn.close()


def save_to_database(contacts: List[Tuple[str, str, str]], db_name: str = "contacts.db") -> None:
    """
    把聯絡資訊聯絡資訊儲存到SQLite資料庫
    contacts:包含 (姓名,職稱,Email)的tuple list
    db_name:SQLite資料庫檔案名稱
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    for contact in contacts:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO contacts (name, title, email)
                VALUES (?, ?, ?)
            """, contact)
        except sqlite3.IntegrityError:
            continue
    conn.commit()
    conn.close()


def parse_contacts(html: str) -> List[Tuple[str, str, str]]:
    """
    使用正規表達式從html中parse出聯絡資訊
    html:html之網頁內容
    return:包含 (姓名,職稱,Email)的tuple list
    """
    contacts = []
    name_pattern = r"Name:\s*(.+?)<"
    title_pattern = r"Title:\s*(.+?)<"
    email_pattern = r"Email:\s*([\w\.-]+@[\w\.-]+)"
    names = re.findall(name_pattern, html)
    titles = re.findall(title_pattern, html)
    emails = re.findall(email_pattern, html)

    for name, title, email in zip(names, titles, emails):
        contacts.append((name.strip(), title.strip(), email.strip()))
    return contacts


def scrape_contacts(url: str) -> List[Tuple[str, str, str]]:
    """
    從使用者輸入的url中抓取聯絡資訊
    url:使用者輸入之url
    return:包含 (姓名,職稱,Email)的tuple list
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return parse_contacts(response.text)
    except requests.RequestException as e:
        messagebox.showerror("錯誤", f"無法抓取資料: {e}")
        return []


def display_contacts(contacts: List[Tuple[str, str, str]], text_widget: scrolledtext.ScrolledText) -> None:
    """
    在文字框中顯示聯絡資訊
    contacts:包含 (姓名,職稱,Email)的tuple list
    text_widget:Tkinter的ScrolledText元件
    """
    text_widget.delete(1.0, tk.END)
    for contact in contacts:
        text_widget.insert(tk.END, f"Name: {contact[0]}\n")
        text_widget.insert(tk.END, f"Title: {contact[1]}\n")
        text_widget.insert(tk.END, f"Email: {contact[2]}\n")
        text_widget.insert(tk.END, "-" * 40 + "\n")


def main():
    def on_scrape():
        url = url_entry.get().strip()
        if not url:
            messagebox.showerror("錯誤", "請輸入網址")
            return
        contacts = scrape_contacts(url)
        if contacts:
            save_to_database(contacts)
            display_contacts(contacts, output_text)

    root = tk.Tk()
    root.title("聯絡資訊爬蟲")
    root.geometry("640x480")

    ttk.Label(root, text="URL:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    url_entry = ttk.Entry(root, width=50)
    url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
    scrape_button = ttk.Button(root, text="抓取", command=on_scrape)
    scrape_button.grid(row=0, column=2, padx=10, pady=10)

    output_text = scrolledtext.ScrolledText(root, width=70, height=25)
    output_text.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

    root.mainloop()


if __name__ == "__main__":
    setup_database()
    main()
