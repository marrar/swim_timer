import streamlit as st
import time
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="Swim Finish Timer 4000",
    layout="wide"
)

st.sidebar.header("Layout")

layout_mode = st.sidebar.radio(
    "Button layout",
    ["Auto", "Mobile", "Tablet", "Desktop"],
    index=0
)

if layout_mode == "Mobile":
    n_cols = 2
elif layout_mode == "Tablet":
    n_cols = 3
elif layout_mode == "Desktop":
    n_cols = 5
else:
    # Auto (safe default)
    n_cols = 3
st.title("🏊 Swim Finish Timer 4000m")

@st.cache_data
def load_roster():
    return pd.read_csv("swimmers.csv")

roster = load_roster()

def age_category(age):
    if age <= 29:
        return "18-29"
    elif age <= 39:
        return "30-39"
    elif age <= 49:
        return "40-49"
    elif age <= 59:
        return "50-59"
    elif age <=69:
        return "60-69"
    elif age <= 79:
        return "70-79"
    elif age <= 89:
        return "80-89"
    else:
        return "Open"

roster["Age Category"] = roster["Age"].apply(age_category)



# --- Initialize state ---
if "start_time" not in st.session_state:
    st.session_state.start_time = None
    st.session_state.results = {}

# --- Start race ---
col1, col2 = st.columns([2,3])
with col1:
    start_disabled = st.session_state.start_time is not None

    if st.button(
        "▶️ START RACE",
        use_container_width=True,
        disabled=start_disabled
    ):
        st.session_state.start_time = time.time()
        st.session_state.results = {}

with col2:
    chrono_placeholder = st.empty()

    if st.session_state.start_time:
        st_autorefresh(interval=200, key="chrono_refresh")
        elapsed = time.time() - st.session_state.start_time

        minutes = int(elapsed // 60)
        seconds = elapsed % 60

        chrono_placeholder.markdown(
            f"### ⏱️  {minutes:02d}:{seconds:05.2f}"
        )
    else:
        chrono_placeholder.markdown("### ⏱️  00:00.00")



st.divider()

# --- Swimmer buttons ---
st.subheader("Finish Buttons")

num_swimmers = 100
cols = st.columns(n_cols)  # n_cols columns for better mobile layout

for i in range(num_swimmers):
    swimmer_id = i+1
    col = cols[i % n_cols]

    with col:
        if swimmer_id in st.session_state.results:
            st.button(
                f"✅ {i+1}",
                disabled=True,
                use_container_width=True
            )
        else:
            if st.button(
                f"🏁 {i+1}",
                use_container_width=True,
                disabled=st.session_state.start_time is None
            ):
                finish_time = time.time() - st.session_state.start_time
                st.session_state.results[swimmer_id] = round(finish_time, 2)


# --- Results table ---
st.divider()
st.subheader("Results")


if st.session_state.results:
    times_df = pd.DataFrame(
        st.session_state.results.items(),
        columns=["SwimmerID", "Finish Time (s)"]
    )

    final_df = (
        times_df
        .merge(roster, on="SwimmerID", how="left")
        .sort_values("Finish Time (s)")
        .reset_index(drop=True)
    )

    st.subheader("Overall Results")
    st.dataframe(
        final_df[["SwimmerID", "Name", "Age", "Age Category", "Finish Time (s)"]],
        use_container_width=True
    )

    st.subheader("Results by Age Category")

    for category in final_df["Age Category"].unique():
        st.markdown(f"### 🏅 {category}")
        cat_df = final_df[final_df["Age Category"] == category]

        st.dataframe(
            cat_df[["SwimmerID", "Name", "Age", "Finish Time (s)"]],
            use_container_width=True
        )

    csv = final_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Results CSV",
        csv,
        "swim_results_by_age_category.csv",
        "text/csv"
    )
else:   
    st.info("No finish times recorded yet.")
