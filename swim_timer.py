import streamlit as st
import time
import pandas as pd

@st.cache_data
def load_roster():
    return pd.read_csv("swimmers.csv")

roster = load_roster()

st.set_page_config(
    page_title="Swim Finish Timer",
    layout="wide"
)

st.title("🏊 Swim Finish Timer")

# --- Initialize state ---
if "start_time" not in st.session_state:
    st.session_state.start_time = None
    st.session_state.results = {}

# --- Start race ---
col1, col2 = st.columns([1, 4])

with col1:
    if st.button("▶️ START RACE", use_container_width=True):
        st.session_state.start_time = time.time()
        st.session_state.results = {}

with col2:
    if st.session_state.start_time:
        elapsed = time.time() - st.session_state.start_time
        st.metric("Race Time", f"{elapsed:.2f} s")
    else:
        st.metric("Race Time", "—")

st.divider()

# --- Swimmer buttons ---
st.subheader("Finish Buttons")

num_swimmers = 100
cols = st.columns(5)  # 5 columns for better mobile layout

for i in range(num_swimmers):
    swimmer_id = i+1
    col = cols[i % 5]

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

    st.dataframe(
        final_df[["SwimmerID", "Name", "Age", "Finish Time (s)"]],
        use_container_width=True
    )

    csv = final_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Results CSV",
        csv,
        "swim_results_with_names.csv",
        "text/csv"
    )
else:
    st.info("No finish times recorded yet.")
