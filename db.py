import sqlite3

def init_db():
    conn = sqlite3.connect('articles.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

def save_article(url):
    conn = sqlite3.connect('articles.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO articles (url) VALUES (?)', (url,))
    conn.commit()
    conn.close()

def is_article_sent(url):
    conn = sqlite3.connect('articles.db')
    c = conn.cursor()
    c.execute('SELECT 1 FROM articles WHERE url = ?', (url,))
    result = c.fetchone()
    conn.close()
    return result is not None

def clear_db():
    conn = sqlite3.connect('articles.db')
    c = conn.cursor()
    c.execute('DELETE FROM articles')
    conn.commit()
    conn.close()

init_db()
