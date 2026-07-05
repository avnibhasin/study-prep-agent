import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError, ResourceExhausted

# Load environment variables
load_dotenv()

# Custom Exception Class
class GeminiAPIError(Exception):
    """Custom exception to deliver user-friendly error messages from Gemini API calls."""
    pass

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Clean system prompts
SYSTEM_PROMPT_TOPICS = (
    "You are a helpful study preparation agent. Your task is to extract key topics and concepts from the provided text.\n"
    "You must return ONLY a valid JSON list of strings (between 4 and 8 topics/concepts).\n"
    "Do not include any markdown styling, code block backticks (like ```json ... ```), explanation, or HTML. "
    "Output must be a raw JSON list of strings. E.g.: [\"Topic 1\", \"Topic 2\", \"Topic 3\", \"Topic 4\"]"
)

SYSTEM_PROMPT_QUIZ = (
    "You are an expert educator. You generate quizzes based on a list of study topics.\n"
    "Your output must be a valid JSON array of objects. Each object must have these exact fields:\n"
    "- 'question': (string) the question text\n"
    "- 'type': (string) either 'mcq' (for multiple choice) or 'short' (for short answer/fill in the blank)\n"
    "- 'options': (list of 4 strings) ONLY if type is 'mcq'. If type is 'short', this must be an empty list [] or null.\n"
    "- 'correct_answer': (string) the correct answer. For MCQ, this must match one of the options exactly (case-sensitive). For short answer, keep the correct answer concise (1-5 words).\n"
    "- 'topic': (string) the topic from the provided list that this question covers.\n"
    "- 'difficulty': (string) the difficulty level of this question. Must be exactly 'easy', 'medium', or 'hard'.\n\n"
    "Do not include any markdown styling, code block backticks, explanations, or HTML. Return ONLY the raw JSON output."
)

def clean_json_string(raw_str: str) -> str:
    """Removes markdown code block backticks and extra spacing from AI output."""
    cleaned = raw_str.strip()
    if cleaned.startswith("```"):
        # Remove first line if it's a block header e.g. ```json
        lines = cleaned.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned

def _fallback_keyword_extraction(text: str) -> list[str]:
    """Fallback keyword-based topic extraction if Gemini API is missing or fails."""
    import re
    from collections import Counter
    stopwords = {
        'the', 'and', 'of', 'to', 'in', 'is', 'that', 'it', 'for', 'on', 'with', 'as', 
        'this', 'by', 'an', 'be', 'are', 'from', 'at', 'or', 'was', 'your', 'from', 
        'about', 'how', 'what', 'which', 'who', 'will', 'with'
    }
    # Find all words of length 4 to 15
    words = re.findall(r'\b[a-zA-Z]{4,15}\b', text.lower())
    filtered_words = [w for w in words if w not in stopwords]
    common = Counter(filtered_words).most_common(6)
    topics = [w[0].capitalize() for w in common]
    if not topics:
        topics = ["General Study", "Key Concepts", "Key Terms"]
    return topics

def _fallback_dummy_quiz(topics: list[str], num_questions: int) -> list[dict]:
    """Generates standard questions for testing/fallback if Gemini fails."""
    import random
    dummy_pool = [
        {
            "question": "Which programming paradigm focuses on binding data and the functions that manipulate them?",
            "type": "mcq",
            "options": ["Object-Oriented Programming", "Functional Programming", "Procedural Programming", "Logical Programming"],
            "correct_answer": "Object-Oriented Programming",
            "topic": topics[0] if topics else "Computer Science",
            "difficulty": "medium"
        },
        {
            "question": "What is the time complexity of searching in a sorted array using Binary Search?",
            "type": "mcq",
            "options": ["O(n)", "O(log n)", "O(n log n)", "O(1)"],
            "correct_answer": "O(log n)",
            "topic": topics[0] if topics else "Algorithms",
            "difficulty": "medium"
        },
        {
            "question": "What design pattern defines a one-to-many dependency between objects so that when one object changes state, all its dependents are notified?",
            "type": "mcq",
            "options": ["Singleton Pattern", "Observer Pattern", "Factory Pattern", "Strategy Pattern"],
            "correct_answer": "Observer Pattern",
            "topic": topics[1] if len(topics) > 1 else "Software Design",
            "difficulty": "medium"
        },
        {
            "question": "Which data structure follows the Last-In-First-Out (LIFO) design principle?",
            "type": "short",
            "options": [],
            "correct_answer": "Stack",
            "topic": topics[0] if topics else "Data Structures",
            "difficulty": "medium"
        },
        {
            "question": "In Git, what command is used to record changes in the local repository?",
            "type": "short",
            "options": [],
            "correct_answer": "git commit",
            "topic": topics[1] if len(topics) > 1 else "Git",
            "difficulty": "medium"
        },
        {
            "question": "Which protocol is primarily used for securely transferring data over the internet?",
            "type": "mcq",
            "options": ["HTTP", "HTTPS", "FTP", "SMTP"],
            "correct_answer": "HTTPS",
            "topic": topics[2] if len(topics) > 2 else "Networking",
            "difficulty": "medium"
        }
    ]
    
    quiz = []
    for i in range(num_questions):
        q = dummy_pool[i % len(dummy_pool)].copy()
        if topics:
            q["topic"] = random.choice(topics)
        quiz.append(q)
    return quiz

def _fallback_dynamic_quiz(study_text: str, topics: list[str], num_questions: int) -> list[dict]:
    """Generates a text-specific quiz locally based on study notes and extracted topics."""
    import random
    import re
    
    # If no study text is provided, fall back to the dummy pool
    if not study_text or len(study_text.strip()) < 50:
        return _fallback_dummy_quiz(topics, num_questions)
        
    # Split text into sentences
    sentences = [s.strip() for s in re.split(r'[.!?]\s+', study_text) if len(s.strip()) > 15]
    if not sentences:
        return _fallback_dummy_quiz(topics, num_questions)
        
    quiz = []
    # Match sentences containing topic names
    topic_sentences = {t: [] for t in topics}
    for sentence in sentences:
        for t in topics:
            if t.lower() in sentence.lower():
                topic_sentences[t].append(sentence)
                
    # Filter topics that actually appear in the text sentences
    matchable_topics = [t for t in topics if topic_sentences[t]]
    if not matchable_topics:
        matchable_topics = topics
        topic_sentences = {t: sentences for t in topics}
        
    for i in range(num_questions):
        topic = matchable_topics[i % len(matchable_topics)]
        candidate_sentences = topic_sentences[topic]
        sentence = random.choice(candidate_sentences)
        
        # Blank out the topic name in the sentence
        pattern = re.compile(re.escape(topic), re.IGNORECASE)
        blanked = pattern.sub("_______", sentence)
        
        # Limit blanked length to prevent huge questions
        if len(blanked) > 200:
            blanked = blanked[:200] + "..."
            
        q_type = "mcq" if i % 2 == 0 else "short"
        
        if q_type == "mcq":
            # Generate options with topic as correct answer
            distractors = list(set(topics) - {topic})
            if len(distractors) < 3:
                distractors = distractors + ["Concept A", "Concept B", "Concept C"]
            random.shuffle(distractors)
            options = [topic] + distractors[:3]
            random.shuffle(options)
            
            quiz.append({
                "question": f"Which concept completes the following statement: '{blanked}'?",
                "type": "mcq",
                "options": options,
                "correct_answer": topic,
                "topic": topic,
                "difficulty": "medium"
            })
        else:
            quiz.append({
                "question": f"Identify the missing concept in this statement: '{blanked}'",
                "type": "short",
                "options": [],
                "correct_answer": topic,
                "topic": topic,
                "difficulty": "medium"
            })
            
    return quiz

def extract_topics(text: str) -> tuple[list[str], bool]:
    """
    Sends input text to Gemini and returns a tuple of (list of 4-8 topics, was_truncated).
    Truncates input text to a safe character limit (20,000 chars) before sending.
    Gracefully falls back to local keyword extraction if the API is unavailable or rate-limited.
    """
    # Safe character limit (~4,000 to 5,000 tokens)
    SAFE_CHAR_LIMIT = 20000
    was_truncated = len(text) > SAFE_CHAR_LIMIT
    text_sample = text[:SAFE_CHAR_LIMIT]

    if api_key:
        model = genai.GenerativeModel(
            model_name='gemini-2.0-flash',
            system_instruction=SYSTEM_PROMPT_TOPICS
        )
        
        for attempt in range(2):
            try:
                response = model.generate_content(
                    f"Extract 4 to 8 key topics/concepts from the following text:\n\n{text_sample}",
                    generation_config={"temperature": 0.1}
                )
                cleaned = clean_json_string(response.text)
                try:
                    topics = json.loads(cleaned)
                except json.JSONDecodeError:
                    # Regex-based extraction backup if formatting is slightly off
                    topics = re.findall(r'"([^"]*)"', cleaned)
                
                if isinstance(topics, list) and all(isinstance(t, str) for t in topics) and len(topics) >= 4:
                    return [t.strip() for t in topics[:8]], was_truncated
            except Exception as e:
                print(f"[WARN] Topic extraction attempt {attempt+1} failed: {e}")
                
    # Fallback keyword extraction as a genuine last resort
    print("[INFO] Using local fallback keyword extraction.")
    fallback_topics = _fallback_keyword_extraction(text_sample)
    return fallback_topics[:8], was_truncated

def validate_quiz_json(quiz_data, topics: list[str]) -> bool:
    """Validates the structure of the quiz list returned by the model."""
    if not isinstance(quiz_data, list):
        return False
    for item in quiz_data:
        if not isinstance(item, dict):
            return False
        # Verify required keys
        for key in ["question", "type", "correct_answer", "topic", "difficulty"]:
            if key not in item:
                return False
        if item["type"] not in ["mcq", "short"]:
            return False
        if item["difficulty"] not in ["easy", "medium", "hard"]:
            return False
        if item["type"] == "mcq":
            if "options" not in item or not isinstance(item["options"], list) or len(item["options"]) != 4:
                return False
            # Ensure correct answer is in the options list (case-insensitive check first)
            options_lower = [opt.strip().lower() for opt in item["options"]]
            ans_lower = item["correct_answer"].strip().lower()
            if ans_lower not in options_lower:
                return False
    return True

def generate_quiz(topics: list[str], weak_topics: list[str] = None, num_questions: int = 5, study_text: str = "", deck_id: int = None) -> list[dict]:
    """
    Asks Gemini to generate a quiz with a mix of MCQ and short-answer questions.
    Biases ~60% of the questions towards weak_topics if provided.
    Gracefully falls back to local dynamic question generation if the API is unavailable or rate-limited.
    """
    if api_key:
        model = genai.GenerativeModel(
            model_name='gemini-2.0-flash',
            system_instruction=SYSTEM_PROMPT_QUIZ
        )

        import memory
        diff_instructions = []
        for t in topics:
            diff_level = memory.get_topic_difficulty(t, deck_id=deck_id)
            diff_instructions.append(f"- '{t}': target difficulty is {diff_level.upper()}")
        diff_str = "\n".join(diff_instructions)

        # Calculate biasing instructions
        if weak_topics:
            # Filter weak topics to only those present in the provided list
            valid_weak = [t for t in weak_topics if t in topics]
            if not valid_weak:
                valid_weak = weak_topics[:2]
            
            num_weak = max(1, int(round(num_questions * 0.6)))
            num_normal = max(0, num_questions - num_weak)
            
            prompt = (
                f"Generate a quiz with exactly {num_questions} questions covering these topics: {topics}.\n"
                f"For each question, assign the 'difficulty' field based on these topic guidelines:\n"
                f"{diff_str}\n\n"
                f"Please bias the questions: roughly {num_weak} questions must cover these WEAK topics: {valid_weak}.\n"
                f"The remaining {num_normal} questions should cover other topics: {list(set(topics) - set(valid_weak))}.\n"
                f"Make sure to provide a mix of multiple-choice (type: 'mcq') and short-answer (type: 'short') questions."
            )
        else:
            prompt = (
                f"Generate a quiz with exactly {num_questions} questions covering these topics: {topics}.\n"
                f"For each question, assign the 'difficulty' field based on these topic guidelines:\n"
                f"{diff_str}\n\n"
                f"Distribute the questions evenly across the topics.\n"
                f"Make sure to provide a mix of multiple-choice (type: 'mcq') and short-answer (type: 'short') questions."
            )

        for attempt in range(2):
            try:
                response = model.generate_content(
                    prompt,
                    generation_config={"temperature": 0.5}
                )
                cleaned = clean_json_string(response.text)
                try:
                    quiz_data = json.loads(cleaned)
                except json.JSONDecodeError:
                    # Regex-based backup parser if format has minor deviations
                    quiz_data = []
                    # Try to find all valid json objects
                    import re
                    matches = re.findall(r'\{[^{}]*\}', cleaned)
                    for m in matches:
                        try:
                            item = json.loads(m)
                            quiz_data.append(item)
                        except Exception:
                            pass
                
                if validate_quiz_json(quiz_data, topics):
                    # Standardize option mapping to avoid subtle mismatches
                    for item in quiz_data:
                        if item["type"] == "mcq":
                            # If correct answer exists in options but case doesn't match perfectly, fix it
                            opt_map = {opt.lower(): opt for opt in item["options"]}
                            ans_lower = item["correct_answer"].lower()
                            if ans_lower in opt_map:
                                item["correct_answer"] = opt_map[ans_lower]
                    return quiz_data[:num_questions]
            except Exception as e:
                print(f"[WARN] Quiz generation attempt {attempt+1} failed: {e}")

    # Fallback as a genuine last resort
    print("[INFO] Using local fallback dynamic quiz generation.")
    return _fallback_dynamic_quiz(study_text, topics, num_questions)

def evaluate_short_answer(question: str, correct_answer: str, user_answer: str) -> dict:
    """Uses Gemini to evaluate if the user's short answer is correct and explains why."""
    if not api_key:
        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
        return {
            "is_correct": is_correct,
            "explanation": f"Exact match evaluation: Expected '{correct_answer}'."
        }
        
    system_prompt_evaluation = (
        "You are an AI teaching assistant. Evaluate the user's answer to a short-answer question.\n"
        "Compare the user's answer to the reference correct answer. Allow for minor spelling mistakes, synonyms, or paraphrasing.\n"
        "Return ONLY a valid JSON object with:\n"
        "- 'is_correct': (boolean) true if the answer is conceptually correct, false otherwise.\n"
        "- 'explanation': (string) a brief, polite explanation of why it is correct or incorrect, referencing the correct answer.\n"
        "Do not include any markdown styling, code block backticks, or explanation. Return ONLY raw JSON."
    )
    
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash',
        system_instruction=system_prompt_evaluation
    )
    
    prompt = (
        f"Question: {question}\n"
        f"Reference Correct Answer: {correct_answer}\n"
        f"User's Answer: {user_answer}\n"
    )
    
    try:
        response = model.generate_content(prompt, generation_config={"temperature": 0.1})
        cleaned = clean_json_string(response.text)
        result = json.loads(cleaned)
        if isinstance(result, dict) and "is_correct" in result and "explanation" in result:
            return result
    except Exception as e:
        print(f"Error evaluating short answer: {e}")
        
    # Standard fallback
    is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
    return {
        "is_correct": is_correct,
        "explanation": f"Expected: '{correct_answer}'. You wrote: '{user_answer}'."
    }

SYSTEM_PROMPT_REVISION = (
    "You are an expert tutor. Your task is to generate a concise, well-organized revision summary in Markdown format "
    "covering the provided list of topics. For each topic, you must include:\n"
    "1. Key concepts and points to understand\n"
    "2. Common mistakes or pitfalls to avoid\n"
    "3. One clear, practical example\n\n"
    "Structure your output with clear headings, bullet points, and code blocks/examples where appropriate. "
    "Keep the tone encouraging, educational, and clean. Do not include introductory or concluding conversational filler."
)

def _fallback_revision_sheet(weak_topics: list[str]) -> str:
    """Fallback revision sheet generation in Markdown format."""
    doc = "# Revision Sheet: Focus Concepts\n\n"
    doc += "This is a fallback revision sheet generated locally because the Gemini API was unavailable.\n\n"
    for topic in weak_topics:
        doc += f"## Topic: {topic}\n\n"
        doc += "### Key Points\n"
        doc += f"- Core principles and vocabulary related to {topic}.\n"
        doc += "- Understand the basic syntax and patterns governing this concept.\n\n"
        doc += "### Common Mistakes to Avoid\n"
        doc += "- Confusing the terminology or mixing logic flows.\n"
        doc += "- Forgetting edge cases (e.g. null checks or out-of-bound indexes).\n\n"
        doc += "### Example\n"
        doc += f"```python\n# Basic example representing {topic}\nprint('Learning concept: {topic}')\n```\n\n"
    return doc

def generate_revision_sheet(weak_topics: list[str]) -> str:
    """Generates a markdown revision sheet for the given weak topics using Gemini."""
    if not api_key:
        return _fallback_revision_sheet(weak_topics)

    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash',
        system_instruction=SYSTEM_PROMPT_REVISION
    )

    prompt = f"Please generate a revision summary covering these weak topics: {weak_topics}."
    
    try:
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.7}
        )
        return response.text
    except Exception as e:
        # Fallback to local rendering on rate-limits or other exceptions
        print(f"Exception during sheet generation: {e}. Falling back to local content...")
        return _fallback_revision_sheet(weak_topics)

SYSTEM_PROMPT_EXPLAIN = (
    "You are an expert tutor. Your task is to write a concise, clear, and educational explanation for why "
    "the given correct answer is correct for the question. Keep it brief (1-3 sentences)."
)

SYSTEM_PROMPT_CRITIQUE = (
    "You are a senior educational editor reviewing explanations generated by a junior tutor.\n"
    "Your job is to read the question, the correct answer, and the draft explanation. Critique the explanation "
    "for clarity, accuracy, and conciseness. Either approve the explanation as-is or provide an improved version.\n\n"
    "Output format: Return ONLY the final approved/improved explanation text. Do not include meta-commentary, "
    "introductions, or bullet points about your edits. Just the final explanation text."
)

def generate_explanation(question: str, correct_answer: str, options: list[str] = None) -> str:
    """Generates an educational draft explanation for why the correct answer is correct."""
    if not api_key:
        return f"The correct answer is '{correct_answer}'."
        
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash',
        system_instruction=SYSTEM_PROMPT_EXPLAIN
    )
    
    prompt = f"Question: {question}\nCorrect Answer: {correct_answer}"
    if options:
        prompt += f"\nOptions: {options}"
        
    try:
        response = model.generate_content(prompt, generation_config={"temperature": 0.5})
        return response.text.strip()
    except Exception as e:
        print(f"Error generating draft explanation: {e}")
        return f"The correct answer is '{correct_answer}'."

def critique_explanation(question: str, correct_answer: str, draft_explanation: str) -> str:
    """Reviews and refines the draft explanation using an editor agent prompt."""
    if not api_key:
        return draft_explanation
        
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash',
        system_instruction=SYSTEM_PROMPT_CRITIQUE
    )
    
    prompt = (
        f"Question: {question}\n"
        f"Correct Answer: {correct_answer}\n"
        f"Draft Explanation: {draft_explanation}\n"
    )
    
    try:
        response = model.generate_content(prompt, generation_config={"temperature": 0.3})
        return response.text.strip()
    except Exception as e:
        print(f"Error critiquing explanation: {e}")
        return draft_explanation
