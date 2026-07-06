import sqlite3
import os
from datetime import datetime

DB_FILE = 'study_prep.db'

def get_connection(db_path=DB_FILE):
    """Establishes connection to the SQLite database."""
    return sqlite3.connect(db_path)

def init_db(db_path=DB_FILE):
    """Initializes the database with decks, quiz_history, and revision_sheets tables."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        # Create decks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_text TEXT
            )
        """)
        
        # Create quiz_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                is_correct INTEGER NOT NULL, -- 0 or 1
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                deck_id INTEGER REFERENCES decks(id) ON DELETE CASCADE
            )
        """)
        
        # Create revision_sheets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS revision_sheets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_id INTEGER REFERENCES decks(id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Schema migration: Add deck_id if missing
        cursor.execute("PRAGMA table_info(quiz_history)")
        columns = [col[1] for col in cursor.fetchall()]
        if "deck_id" not in columns:
            cursor.execute("ALTER TABLE quiz_history ADD COLUMN deck_id INTEGER REFERENCES decks(id) ON DELETE CASCADE")
            
        conn.commit()
    except Exception as e:
        print(f"Error during DB initialization: {e}")
    finally:
        conn.close()

def log_answer(topic: str, is_correct: bool, db_path=DB_FILE, deck_id: int = None):
    """Logs an individual question's answer result into quiz_history, optionally linked to a deck."""
    import datetime
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        val = 1 if is_correct else 0
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO quiz_history (topic, is_correct, deck_id, timestamp) VALUES (?, ?, ?, ?)",
            (topic, val, deck_id, timestamp_str)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_weak_topics(threshold: float = 0.6, db_path=DB_FILE, deck_id: int = None) -> list[str]:
    """
    Returns topics where historical accuracy is below the threshold,
    ordered by weakest first, optionally filtered by deck.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    weak_topics = []
    try:
        if deck_id is not None:
            cursor.execute("""
                SELECT topic, CAST(SUM(is_correct) AS FLOAT) / COUNT(*) as accuracy
                FROM quiz_history
                WHERE deck_id = ?
                GROUP BY topic
                HAVING accuracy < ?
                ORDER BY accuracy ASC
            """, (deck_id, threshold))
        else:
            cursor.execute("""
                SELECT topic, CAST(SUM(is_correct) AS FLOAT) / COUNT(*) as accuracy
                FROM quiz_history
                GROUP BY topic
                HAVING accuracy < ?
                ORDER BY accuracy ASC
            """, (threshold,))
        rows = cursor.fetchall()
        weak_topics = [row[0] for row in rows]
    except Exception as e:
        print(f"Error fetching weak topics: {e}")
    finally:
        conn.close()
    return weak_topics

def get_topic_stats(db_path=DB_FILE, deck_id: int = None) -> list[dict]:
    """
    Returns accuracy statistics per topic for the dashboard,
    containing total, correct, incorrect, and accuracy percentage, optionally filtered by deck.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    stats = []
    try:
        if deck_id is not None:
            cursor.execute("""
                SELECT topic, COUNT(*), SUM(is_correct)
                FROM quiz_history
                WHERE deck_id = ?
                GROUP BY topic
            """, (deck_id,))
        else:
            cursor.execute("""
                SELECT topic, COUNT(*), SUM(is_correct)
                FROM quiz_history
                GROUP BY topic
            """)
        rows = cursor.fetchall()
        for row in rows:
            topic, total, correct = row
            correct = correct or 0
            incorrect = total - correct
            accuracy = round((correct / total) * 100, 1) if total > 0 else 0.0
            stats.append({
                "topic": topic,
                "total": total,
                "correct": correct,
                "incorrect": incorrect,
                "accuracy": accuracy
            })
    except Exception as e:
        print(f"Error fetching topic stats: {e}")
    finally:
        conn.close()
    return stats

def get_performance_summary(db_path=DB_FILE, deck_id: int = None) -> dict:
    """Calculates overall metrics from quiz_history, optionally filtered by deck."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    summary = {
        "total_questions": 0,
        "total_correct": 0,
        "average_score_pct": 0.0,
        "strongest_topics": [],
        "weakest_topics": []
    }
    try:
        if deck_id is not None:
            cursor.execute("SELECT COUNT(*), SUM(is_correct) FROM quiz_history WHERE deck_id = ?", (deck_id,))
        else:
            cursor.execute("SELECT COUNT(*), SUM(is_correct) FROM quiz_history")
            
        total, correct = cursor.fetchone()
        summary["total_questions"] = total or 0
        summary["total_correct"] = correct or 0
        
        if total and total > 0:
            summary["average_score_pct"] = round((correct / total) * 100, 1)
            
            # Fetch topic accuracy sorted
            if deck_id is not None:
                cursor.execute("""
                    SELECT topic, CAST(SUM(is_correct) AS FLOAT) / COUNT(*) as accuracy
                    FROM quiz_history
                    WHERE deck_id = ?
                    GROUP BY topic
                """, (deck_id,))
            else:
                cursor.execute("""
                    SELECT topic, CAST(SUM(is_correct) AS FLOAT) / COUNT(*) as accuracy
                    FROM quiz_history
                    GROUP BY topic
                """)
            topic_accs = cursor.fetchall()
            if topic_accs:
                # Sort topics by accuracy
                topic_accs.sort(key=lambda x: x[1])
                summary["weakest_topics"] = [t[0] for t in topic_accs[:3] if t[1] < 0.7]
                summary["strongest_topics"] = [t[0] for t in reversed(topic_accs[-3:]) if t[1] >= 0.7]
    except Exception as e:
        print(f"Error getting performance summary: {e}")
    finally:
        conn.close()
    return summary

def get_accuracy_over_time(db_path=DB_FILE, deck_id: int = None) -> list[dict]:
    """Retrieves answer counts aggregated chronologically by date/time, optionally filtered by deck."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    timeline = []
    try:
        if deck_id is not None:
            cursor.execute("SELECT timestamp, is_correct FROM quiz_history WHERE deck_id = ? ORDER BY timestamp ASC", (deck_id,))
        else:
            cursor.execute("SELECT timestamp, is_correct FROM quiz_history ORDER BY timestamp ASC")
        rows = cursor.fetchall()
        
        # We can construct a rolling accuracy over time
        total = 0
        correct = 0
        for idx, row in enumerate(rows):
            ts, is_corr = row
            total += 1
            if is_corr:
                correct += 1
            pct = round((correct / total) * 100, 1)
            timeline.append({
                "timestamp": ts,
                "accuracy": pct,
                "question_num": total
            })
    except Exception as e:
        print(f"Error fetching accuracy over time: {e}")
    finally:
        conn.close()
    return timeline

def get_recent_history(limit=20, db_path=DB_FILE, deck_id: int = None) -> list[dict]:
    """Retrieves recent answers logged, optionally filtered by deck."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    history = []
    try:
        if deck_id is not None:
            cursor.execute("""
                SELECT id, topic, is_correct, timestamp 
                FROM quiz_history 
                WHERE deck_id = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (deck_id, limit))
        else:
            cursor.execute("""
                SELECT id, topic, is_correct, timestamp 
                FROM quiz_history 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
        rows = cursor.fetchall()
        for row in rows:
            history.append({
                "id": row[0],
                "topic": row[1],
                "is_correct": bool(row[2]),
                "timestamp": row[3]
            })
    except Exception as e:
        print(f"Error fetching history: {e}")
    finally:
        conn.close()
    return history

def get_streak(db_path=DB_FILE, deck_id: int = None) -> int:
    """Queries recent answers and counts the consecutive correct answers (streak), optionally filtered by deck."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        if deck_id is not None:
            cursor.execute("SELECT is_correct FROM quiz_history WHERE deck_id = ? ORDER BY timestamp DESC", (deck_id,))
        else:
            cursor.execute("SELECT is_correct FROM quiz_history ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        streak = 0
        for row in rows:
            if row[0] == 1:
                streak += 1
            else:
                break
        return streak
    except Exception as e:
        print(f"Error fetching streak: {e}")
        return 0
    finally:
        conn.close()

def get_best_topic(db_path=DB_FILE, deck_id: int = None) -> tuple[str, float] or None:
    """Finds the topic with the highest accuracy rate. Needs at least 2 answers if possible, optionally filtered by deck."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        # First query for topics with >= 2 answers to avoid skewing
        if deck_id is not None:
            cursor.execute("""
                SELECT topic, CAST(SUM(is_correct) AS FLOAT) / COUNT(*) as accuracy
                FROM quiz_history
                WHERE deck_id = ?
                GROUP BY topic
                HAVING COUNT(*) >= 2
                ORDER BY accuracy DESC, COUNT(*) DESC
                LIMIT 1
            """, (deck_id,))
        else:
            cursor.execute("""
                SELECT topic, CAST(SUM(is_correct) AS FLOAT) / COUNT(*) as accuracy
                FROM quiz_history
                GROUP BY topic
                HAVING COUNT(*) >= 2
                ORDER BY accuracy DESC, COUNT(*) DESC
                LIMIT 1
            """)
        row = cursor.fetchone()
        if row:
            return row[0], round(row[1] * 100, 1)
            
        # Fallback to any topic if none have >= 2 answers
        if deck_id is not None:
            cursor.execute("""
                SELECT topic, CAST(SUM(is_correct) AS FLOAT) / COUNT(*) as accuracy
                FROM quiz_history
                WHERE deck_id = ?
                GROUP BY topic
                ORDER BY accuracy DESC
                LIMIT 1
            """, (deck_id,))
        else:
            cursor.execute("""
                SELECT topic, CAST(SUM(is_correct) AS FLOAT) / COUNT(*) as accuracy
                FROM quiz_history
                GROUP BY topic
                ORDER BY accuracy DESC
                LIMIT 1
            """)
        row = cursor.fetchone()
        if row:
            return row[0], round(row[1] * 100, 1)
    except Exception as e:
        print(f"Error fetching best topic: {e}")
    finally:
        conn.close()
    return None

def get_most_improved_topic(db_path=DB_FILE, deck_id: int = None) -> tuple[str, float] or None:
    """
    Compares the accuracy of the last 5 answers for each topic against its overall accuracy.
    Returns the topic with the greatest positive improvement, optionally filtered by deck.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        if deck_id is not None:
            cursor.execute("SELECT DISTINCT topic FROM quiz_history WHERE deck_id = ?", (deck_id,))
        else:
            cursor.execute("SELECT DISTINCT topic FROM quiz_history")
        topics = [r[0] for r in cursor.fetchall()]
        
        most_improved = None
        max_improvement = -999.0
        
        for topic in topics:
            # Overall accuracy (needs at least 3 attempts to assess improvement fairly)
            if deck_id is not None:
                cursor.execute("SELECT COUNT(*), SUM(is_correct) FROM quiz_history WHERE topic = ? AND deck_id = ?", (topic, deck_id))
            else:
                cursor.execute("SELECT COUNT(*), SUM(is_correct) FROM quiz_history WHERE topic = ?", (topic,))
            tot_count, tot_correct = cursor.fetchone()
            if not tot_count or tot_count < 3:
                continue
            overall_acc = tot_correct / tot_count
            
            # Last 5 answers accuracy (needs at least 3 attempts in the last 5)
            if deck_id is not None:
                cursor.execute("SELECT is_correct FROM quiz_history WHERE topic = ? AND deck_id = ? ORDER BY timestamp DESC LIMIT 5", (topic, deck_id))
            else:
                cursor.execute("SELECT is_correct FROM quiz_history WHERE topic = ? ORDER BY timestamp DESC LIMIT 5", (topic,))
            last_rows = cursor.fetchall()
            last_count = len(last_rows)
            if last_count < 3:
                continue
            last_correct = sum(r[0] for r in last_rows)
            last_acc = last_correct / last_count
            
            improvement = last_acc - overall_acc
            # Check for positive improvement
            if improvement > max_improvement and improvement > 0.0:
                max_improvement = improvement
                most_improved = (topic, round(improvement * 100, 1))
                
        return most_improved
    except Exception as e:
        print(f"Error fetching most improved topic: {e}")
    finally:
        conn.close()
    return None

def get_topic_difficulty(topic: str, db_path=DB_FILE, deck_id: int = None) -> str:
    """
    Determines the target difficulty level for a topic based on performance logs:
    - Returns 'hard' if the user has a current streak of 3+ correct answers for this topic.
    - Returns 'easy' if the user's most recent answer for this topic was incorrect.
    - Otherwise, returns 'medium'.
    Optionally filtered by deck.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        if deck_id is not None:
            cursor.execute("""
                SELECT is_correct FROM quiz_history 
                WHERE topic = ? AND deck_id = ?
                ORDER BY timestamp DESC 
                LIMIT 5
            """, (topic, deck_id))
        else:
            cursor.execute("""
                SELECT is_correct FROM quiz_history 
                WHERE topic = ? 
                ORDER BY timestamp DESC 
                LIMIT 5
            """, (topic,))
        rows = cursor.fetchall()
        if not rows:
            return "medium"
            
        recent_results = [row[0] for row in rows]
        
        # Check streak of correct answers starting from the most recent
        streak = 0
        for res in recent_results:
            if res == 1:
                streak += 1
            else:
                break
                
        # Check if the most recent answer was incorrect
        most_recent_incorrect = (recent_results[0] == 0)
        
        if streak >= 3:
            return "hard"
        elif most_recent_incorrect:
            return "easy"
        else:
            return "medium"
    except Exception as e:
        print(f"Error determining topic difficulty: {e}")
        return "medium"
    finally:
        conn.close()

def get_accuracy_over_time_for_topic(topic: str, db_path=DB_FILE, deck_id: int = None) -> list[dict]:
    """Retrieves rolling answer accuracy aggregated chronologically for a specific topic, optionally filtered by deck."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    timeline = []
    try:
        if deck_id is not None:
            cursor.execute("SELECT timestamp, is_correct FROM quiz_history WHERE topic = ? AND deck_id = ? ORDER BY timestamp ASC", (topic, deck_id))
        else:
            cursor.execute("SELECT timestamp, is_correct FROM quiz_history WHERE topic = ? ORDER BY timestamp ASC", (topic,))
        rows = cursor.fetchall()
        
        total = 0
        correct = 0
        for idx, row in enumerate(rows):
            ts, is_corr = row
            total += 1
            if is_corr:
                correct += 1
            pct = round((correct / total) * 100, 1)
            timeline.append({
                "timestamp": ts,
                "accuracy": pct,
                "question_num": total
            })
    except Exception as e:
        print(f"Error fetching accuracy over time for topic {topic}: {e}")
    finally:
        conn.close()
    return timeline

def create_deck(name: str, source_text: str, db_path=DB_FILE) -> int:
    """Creates a new deck and returns its auto-incremented ID."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO decks (name, source_text) VALUES (?, ?)",
            (name, source_text)
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_all_decks(db_path=DB_FILE) -> list[dict]:
    """Retrieves all decks from the database."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    decks = []
    try:
        cursor.execute("SELECT id, name, created_at, source_text FROM decks ORDER BY name ASC")
        rows = cursor.fetchall()
        for row in rows:
            decks.append({
                "id": row[0],
                "name": row[1],
                "created_at": row[2],
                "source_text": row[3]
            })
    except Exception as e:
        print(f"Error fetching all decks: {e}")
    finally:
        conn.close()
    return decks

def get_deck(deck_id: int, db_path=DB_FILE) -> dict or None:
    """Retrieves a single deck by its ID."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, created_at, source_text FROM decks WHERE id = ?", (deck_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "created_at": row[2],
                "source_text": row[3]
            }
    except Exception as e:
        print(f"Error fetching deck {deck_id}: {e}")
    finally:
        conn.close()
    return None

def delete_deck(deck_id: int, db_path=DB_FILE):
    """Deletes a deck and cascades to delete all its associated history."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        # Enforce foreign key constraints for cascade delete
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("DELETE FROM decks WHERE id = ?", (deck_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def save_revision_sheet(deck_id: int, content: str, db_path=DB_FILE) -> int:
    """Saves a generated revision sheet to the database."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO revision_sheets (deck_id, content) VALUES (?, ?)",
            (deck_id, content)
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_revision_sheets(deck_id: int = None, db_path=DB_FILE) -> list[dict]:
    """Retrieves revision sheets, optionally filtered by deck, ordered newest first."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    sheets = []
    try:
        if deck_id is not None:
            cursor.execute("""
                SELECT rs.id, rs.deck_id, d.name as deck_name, rs.content, rs.created_at
                FROM revision_sheets rs
                JOIN decks d ON rs.deck_id = d.id
                WHERE rs.deck_id = ?
                ORDER BY rs.created_at DESC
            """, (deck_id,))
        else:
            cursor.execute("""
                SELECT rs.id, rs.deck_id, d.name as deck_name, rs.content, rs.created_at
                FROM revision_sheets rs
                JOIN decks d ON rs.deck_id = d.id
                ORDER BY rs.created_at DESC
            """)
        rows = cursor.fetchall()
        for row in rows:
            sheets.append({
                "id": row[0],
                "deck_id": row[1],
                "deck_name": row[2],
                "content": row[3],
                "created_at": row[4]
            })
    except Exception as e:
        print(f"Error fetching revision sheets: {e}")
    finally:
        conn.close()
    return sheets

def get_revision_sheet(sheet_id: int, db_path=DB_FILE) -> dict or None:
    """Retrieves a single revision sheet by ID."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT rs.id, rs.deck_id, d.name as deck_name, rs.content, rs.created_at
            FROM revision_sheets rs
            JOIN decks d ON rs.deck_id = d.id
            WHERE rs.id = ?
        """, (sheet_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "deck_id": row[1],
                "deck_name": row[2],
                "content": row[3],
                "created_at": row[4]
            }
    except Exception as e:
        print(f"Error fetching sheet {sheet_id}: {e}")
    finally:
        conn.close()
    return None

def delete_revision_sheet(sheet_id: int, db_path=DB_FILE):
    """Deletes a revision sheet by ID."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM revision_sheets WHERE id = ?", (sheet_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_all_decks_with_stats(db_path=DB_FILE) -> list[dict]:
    """Retrieves all decks with associated answer count, accuracy percentage, and last studied timestamp."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    decks_stats = []
    try:
        cursor.execute("SELECT id, name, created_at, source_text FROM decks ORDER BY name ASC")
        decks = cursor.fetchall()
        for d in decks:
            d_id, name, created_at, source_text = d
            
            cursor.execute("SELECT COUNT(*), SUM(is_correct), MAX(timestamp) FROM quiz_history WHERE deck_id = ?", (d_id,))
            total, correct, max_ts = cursor.fetchone()
            
            total = total or 0
            correct = correct or 0
            accuracy = round((correct / total) * 100, 1) if total > 0 else 0.0
            
            decks_stats.append({
                "id": d_id,
                "name": name,
                "created_at": created_at,
                "source_text": source_text,
                "total_questions": total,
                "accuracy": accuracy,
                "last_studied": max_ts if max_ts else created_at
            })
    except Exception as e:
        print(f"Error fetching decks with stats: {e}")
    finally:
        conn.close()
    return decks_stats

def get_achievements(db_path=DB_FILE) -> dict:
    """Calculates user badges based on historical quiz_history logs."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    achievements = {
        "streak_7_day": {"earned": False, "detail": "Log study attempts on 7 consecutive days."},
        "topic_master": {"earned": False, "detail": "Reach 90%+ accuracy on any topic with 5+ questions asked."},
        "comeback_kid": {"earned": False, "detail": "Improve a topic from <40% accuracy (first 3 attempts) to >70% accuracy (last 3 attempts)."}
    }
    try:
        import datetime
        
        # 1. 7-Day Streak
        cursor.execute("SELECT DISTINCT date(timestamp) FROM quiz_history ORDER BY date(timestamp) ASC")
        dates = [datetime.datetime.strptime(r[0], "%Y-%m-%d").date() for r in cursor.fetchall() if r[0]]
        
        max_run = 0
        current_run = 0
        prev_date = None
        for d in dates:
            if prev_date is None:
                current_run = 1
            elif (d - prev_date).days == 1:
                current_run += 1
            elif (d - prev_date).days > 1:
                current_run = 1
            prev_date = d
            if current_run > max_run:
                max_run = current_run
                
        if max_run >= 7:
            achievements["streak_7_day"]["earned"] = True
            achievements["streak_7_day"]["detail"] = f"Unlocked! You achieved a consecutive study run of {max_run} days."
            
        # 2. Topic Master
        cursor.execute("""
            SELECT topic, COUNT(*), SUM(is_correct)
            FROM quiz_history
            GROUP BY topic
        """)
        masters = []
        for row in cursor.fetchall():
            topic, total, correct = row
            correct = correct or 0
            acc = correct / total if total > 0 else 0.0
            if total >= 5 and acc >= 0.9:
                masters.append(f"{topic} ({round(acc*100)}% accuracy, {total} questions)")
                
        if masters:
            achievements["topic_master"]["earned"] = True
            achievements["topic_master"]["detail"] = f"Unlocked! Mastered topics: {', '.join(masters)}"
            
        # 3. Comeback Kid
        cursor.execute("SELECT DISTINCT topic FROM quiz_history")
        topics = [r[0] for r in cursor.fetchall()]
        comebacks = []
        for t in topics:
            cursor.execute("SELECT is_correct FROM quiz_history WHERE topic = ? ORDER BY timestamp ASC", (t,))
            results = [r[0] for r in cursor.fetchall()]
            if len(results) >= 6:
                first_window = results[:3]
                first_acc = sum(first_window) / len(first_window)
                
                last_window = results[-3:]
                last_acc = sum(last_window) / len(last_window)
                
                if first_acc < 0.4 and last_acc > 0.7:
                    comebacks.append(t)
                    
        if comebacks:
            achievements["comeback_kid"]["earned"] = True
            achievements["comeback_kid"]["detail"] = f"Unlocked! Improved from failure to mastery on: {', '.join(comebacks)}"
            
    except Exception as e:
        print(f"Error calculating achievements: {e}")
    finally:
        conn.close()
    return achievements
