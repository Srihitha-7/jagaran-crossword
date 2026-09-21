import streamlit as st
import time
from supabase import create_client

# ============================================================
# JAGARAN - NARCOTICS AWARENESS CROSSWORD
# Streamlit Web Version
# Features:
# - Username
# - Top 3 global leaderboard using Supabase
# - Enter key submits answers
# - Score, hints, timer
# - Restart game
# ============================================================

PUZZLE = [
    {
        "number": 1,
        "direction": "ACROSS",
        "row": 0,
        "col": 0,
        "answer": "ADDICTION",
        "clue": "A condition involving a strong, difficult-to-control need to use a drug."
    },
    {
        "number": 2,
        "direction": "DOWN",
        "row": 0,
        "col": 2,
        "answer": "DANGER",
        "clue": "A serious risk associated with drug misuse."
    },
    {
        "number": 3,
        "direction": "DOWN",
        "row": 3,
        "col": 7,
        "answer": "HELP",
        "clue": "Something a person should seek when struggling with substance use."
    },
    {
        "number": 4,
        "direction": "DOWN",
        "row": 3,
        "col": 9,
        "answer": "BREATHING",
        "clue": "An essential body function that some narcotics can dangerously slow."
    },
    {
        "number": 5,
        "direction": "ACROSS",
        "row": 4,
        "col": 0,
        "answer": "OVERDOSE",
        "clue": "Taking too much of a drug, potentially causing severe injury or death."
    },
    {
        "number": 6,
        "direction": "DOWN",
        "row": 4,
        "col": 4,
        "answer": "DEATH",
        "clue": "A possible result of a fatal overdose."
    },
    {
        "number": 7,
        "direction": "ACROSS",
        "row": 8,
        "col": 4,
        "answer": "HEALTH",
        "clue": "Something that long-term drug misuse can seriously harm."
    },
    {
        "number": 8,
        "direction": "ACROSS",
        "row": 10,
        "col": 5,
        "answer": "BRAIN",
        "clue": "An organ that can be affected by repeated drug use."
    },
]

GRID_SIZE = 12


# ============================================================
# PUZZLE FUNCTIONS
# ============================================================

def solution_grid():
    solution = {}

    for item in PUZZLE:
        for i, ch in enumerate(item["answer"]):

            if item["direction"] == "ACROSS":
                position = (item["row"], item["col"] + i)
            else:
                position = (item["row"] + i, item["col"])

            if position in solution and solution[position] != ch:
                raise ValueError(
                    "Puzzle has a conflicting cell."
                )

            solution[position] = ch

    return solution


SOLUTION = solution_grid()


def get_cells(item):
    result = []

    for i in range(len(item["answer"])):
        if item["direction"] == "ACROSS":
            result.append((item["row"], item["col"] + i))
        else:
            result.append((item["row"] + i, item["col"]))

    return result


# ============================================================
# SUPABASE
# ============================================================

def get_database():
    try:
        return create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )
    except Exception:
        return None


def get_top3():
    database = get_database()

    if database is None:
        return None

    try:
        response = (
            database
            .table("leaderboard")
            .select(
                "username,score,time_seconds,hints_used,created_at"
            )
            .order("score", desc=True)
            .order("time_seconds", desc=False)
            .order("created_at", desc=False)
            .limit(3)
            .execute()
        )

        return response.data

    except Exception:
        return None


def save_score(username, score, seconds, hints):
    database = get_database()

    if database is None:
        return False

    try:
        database.table("leaderboard").insert({
            "username": username,
            "score": int(score),
            "time_seconds": int(seconds),
            "hints_used": int(hints)
        }).execute()

        return True

    except Exception:
        return False


# ============================================================
# GAME STATE
# ============================================================

def reset_game():
    st.session_state.cells = {}
    st.session_state.solved = set()
    st.session_state.score = 0
    st.session_state.hints = 0
    st.session_state.start = time.time()
    st.session_state.over = False
    st.session_state.saved = False
    st.session_state.message = "Select a clue to begin."
    st.session_state.selected_clue = 0


if "cells" not in st.session_state:
    reset_game()

if "username" not in st.session_state:
    st.session_state.username = ""


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="JAGARAN - Awareness Crossword",
    page_icon="🧩",
    layout="wide"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        color: #17324d;
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        text-align: center;
        color: #526575;
        font-size: 17px;
        margin-bottom: 20px;
    }

    .grid {
        display: grid;
        grid-template-columns: repeat(12, 38px);
        grid-template-rows: repeat(12, 38px);
        width: max-content;
        margin: auto;
    }

    .cell {
        width: 38px;
        height: 38px;
        border: 1px solid #78909c;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        background: white;
        font-size: 19px;
        font-weight: 700;
        color: #17324d;
        box-sizing: border-box;
    }

    .blocked {
        background: #263238;
        border-color: #263238;
    }

    .number {
        position: absolute;
        top: 1px;
        left: 3px;
        font-size: 8px;
        color: #455a64;
    }

    .box {
        background: #eef4f7;
        padding: 12px;
        border-radius: 10px;
        color: #17324d;
        font-weight: 700;
        text-align: center;
    }

    .rank {
        padding: 9px;
        border-bottom: 1px solid #ddd;
    }

    .rank:last-child {
        border-bottom: none;
    }

    .complete {
        background: #e5f5e9;
        border: 1px solid #8bc79b;
        padding: 18px;
        border-radius: 12px;
        color: #174d28;
        font-weight: 600;
    }

    @media (max-width: 700px) {
        .grid {
            transform: scale(0.78);
            transform-origin: top left;
            margin-bottom: -100px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🧩 JAGARAN</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Learn about health risks while solving the puzzle.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# USERNAME + LEADERBOARD
# ============================================================

username_col, leaderboard_col = st.columns([1, 1])

with username_col:

    # IMPORTANT:
    # The widget itself owns the session-state value.
    # This prevents the username from disappearing after
    # pressing Submit Answer or Hint.

    st.text_input(
        "Enter your username",
        max_chars=30,
        placeholder="Example: Rohith",
        key="username"
    )

    username = st.session_state.username.strip()


with leaderboard_col:

    st.markdown("### 🏆 Top 3 Scores")

    rows = get_top3()

    if rows is None:

        st.caption(
            "Connect Supabase to enable the public leaderboard."
        )

    elif not rows:

        st.caption(
            "No scores yet. Be the first!"
        )

    else:

        medals = ["🥇", "🥈", "🥉"]

        for i, row in enumerate(rows):

            total_seconds = int(row["time_seconds"])
            row_minutes, row_seconds = divmod(
                total_seconds,
                60
            )

            st.markdown(
                f"""
                <div class="rank">
                    {medals[i]}
                    <b>{row["username"]}</b>
                    — {row["score"]} pts
                    — {row_minutes:02d}:{row_seconds:02d}
                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# SCORE + TIMER
# ============================================================

elapsed = int(
    time.time() - st.session_state.start
)

minutes, seconds = divmod(elapsed, 60)

score_col, restart_col = st.columns([1.5, 1])

with score_col:

    st.markdown(
        f"""
        <div class="box">
            ⭐ Score: {st.session_state.score}
            &nbsp;&nbsp;
            💡 Hints: {st.session_state.hints}
            &nbsp;&nbsp;
            ⏱️ Time: {minutes:02d}:{seconds:02d}
        </div>
        """,
        unsafe_allow_html=True
    )

with restart_col:

    if st.button(
        "↻ Restart Game",
        use_container_width=True
    ):

        reset_game()
        st.rerun()


st.write("")


# ============================================================
# MAIN LAYOUT
# ============================================================

left, right = st.columns([1.2, 1])


# ============================================================
# CROSSWORD
# ============================================================

with left:

    st.subheader("Crossword")

    clue_numbers = {
        (item["row"], item["col"]): item["number"]
        for item in PUZZLE
    }

    html = '<div class="grid">'

    for row in range(GRID_SIZE):

        for col in range(GRID_SIZE):

            position = (row, col)

            if position not in SOLUTION:

                html += (
                    '<div class="cell blocked"></div>'
                )

            else:

                number = ""

                if position in clue_numbers:

                    number = (
                        f'<span class="number">'
                        f'{clue_numbers[position]}'
                        f'</span>'
                    )

                letter = st.session_state.cells.get(
                    position,
                    ""
                )

                html += (
                    f'<div class="cell">'
                    f'{number}{letter}'
                    f'</div>'
                )

    html += "</div>"

    st.markdown(
        html,
        unsafe_allow_html=True
    )


# ============================================================
# CLUES + ANSWER
# ============================================================

with right:

    st.subheader("Clues")

    options = [
        (
            f"{item['number']}. "
            f"{'Across' if item['direction'] == 'ACROSS' else 'Down'}: "
            f"{item['clue']}"
        )
        for item in PUZZLE
    ]

    selected_clue = st.selectbox(
        "Select a clue",
        range(len(PUZZLE)),
        format_func=lambda i: options[i],
        index=st.session_state.selected_clue
    )

    st.session_state.selected_clue = selected_clue

    item = PUZZLE[selected_clue]

    direction = (
        "Across"
        if item["direction"] == "ACROSS"
        else "Down"
    )

    solved = (
        selected_clue
        in st.session_state.solved
    )

    st.info(
        f"{item['number']} {direction}\n\n"
        f"{item['clue']}"
    )


    # ========================================================
    # ANSWER FORM
    #
    # Pressing ENTER inside the answer field submits the form.
    # ========================================================

    with st.form(
        key=f"answer_form_{selected_clue}",
        clear_on_submit=False
    ):

        answer = st.text_input(
            "Your answer",
            key=f"answer_{selected_clue}",
            disabled=solved or st.session_state.over,
            placeholder="Type your answer and press Enter..."
        )

        submitted = st.form_submit_button(
            "Submit Answer",
            use_container_width=True,
            disabled=solved or st.session_state.over
        )


    # ========================================================
    # PROCESS ANSWER
    # ========================================================

    if submitted:

        username = st.session_state.username.strip()

        if not username:

            st.warning(
                "Please enter a username first."
            )

        elif not answer.strip():

            st.warning(
                "Please enter an answer."
            )

        elif answer.strip().upper() == item["answer"]:

            st.session_state.solved.add(
                selected_clue
            )

            st.session_state.score += 10

            for position, letter in zip(
                get_cells(item),
                item["answer"]
            ):

                st.session_state.cells[position] = letter

            st.session_state.message = (
                "✅ Correct! Great work."
            )

            # =================================================
            # FINISH GAME
            # =================================================

            if len(st.session_state.solved) == len(PUZZLE):

                st.session_state.over = True

                final_seconds = int(
                    time.time()
                    - st.session_state.start
                )

                st.session_state.saved = save_score(
                    username,
                    st.session_state.score,
                    final_seconds,
                    st.session_state.hints
                )

            st.rerun()

        else:

            st.session_state.score = max(
                0,
                st.session_state.score - 2
            )

            st.session_state.message = (
                "❌ Not quite. Try again."
            )

            st.rerun()


    # ========================================================
    # HINT BUTTON
    # ========================================================

    if st.button(
        "💡 Hint",
        use_container_width=True,
        disabled=solved or st.session_state.over
    ):

        username = st.session_state.username.strip()

        if not username:

            st.warning(
                "Please enter a username first."
            )

        else:

            for i, position in enumerate(
                get_cells(item)
            ):

                if position not in st.session_state.cells:

                    st.session_state.cells[position] = (
                        item["answer"][i]
                    )

                    st.session_state.hints += 1

                    st.session_state.score = max(
                        0,
                        st.session_state.score - 3
                    )

                    st.session_state.message = (
                        f"💡 Hint revealed: letter {i + 1}"
                    )

                    break

            st.rerun()


    st.write(
        st.session_state.message
    )


    # ========================================================
    # CLUE LIST
    # ========================================================

    st.markdown("### Clue List")

    for i, clue in enumerate(PUZZLE):

        mark = (
            "✅"
            if i in st.session_state.solved
            else "⬜"
        )

        direction = (
            "Across"
            if clue["direction"] == "ACROSS"
            else "Down"
        )

        st.write(
            mark,
            clue["number"],
            direction,
            "-",
            clue["clue"]
        )


# ============================================================
# COMPLETION MESSAGE
# ============================================================

if st.session_state.over:

    final_time = int(
        time.time()
        - st.session_state.start
    )

    final_minutes, final_seconds = divmod(
        final_time,
        60
    )

    if st.session_state.saved:

        save_message = (
            "🏆 Your score has been added "
            "to the leaderboard!"
        )

    else:

        save_message = (
            "⚠️ The score could not be saved. "
            "Check your Supabase settings."
        )

    # Use normal Streamlit Markdown instead of putting Markdown/HTML
    # tags inside an HTML div. This makes the username and line breaks
    # render correctly on all Streamlit themes.

    st.success("🎉 Puzzle Complete!")

    st.markdown(
        f"""
### Congratulations, **{st.session_state.username}**! 🎊

⭐ **Score:** {st.session_state.score}

💡 **Hints:** {st.session_state.hints}

⏱️ **Time:** {final_minutes:02d}:{final_seconds:02d}

{save_message}
"""
    )


# ============================================================
# TIMER REFRESH
# ============================================================

if not st.session_state.over:

    time.sleep(1)
    st.rerun()
