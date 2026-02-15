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
    n_cols = 1
elif layout_mode == "Tablet":
    n_cols = 3
elif layout_mode == "Desktop":
    n_cols = 5
else:
    # Auto (safe default)
    n_cols = 3
st.title("🏊 Swim Finish Timer - EcoNado Puerto Pilar")

@st.cache_data
def load_roster():
    return pd.read_csv("swimmers_real.csv")

roster = load_roster()

roster = pd.read_csv("swimmers_real.csv")

# 1️⃣ Remove swimmers where viene == "no"
roster = roster[
    roster["Viene"].fillna("").str.lower().str.strip() != "no"
]

# 3️⃣ Sort by Race Category (and optionally Name)
roster = roster.sort_values(
    by=["Race Category", "Name"]
)

# 4️⃣ Reset index
roster = roster.reset_index(drop=True)

# 5️⃣ Create SwimmerID starting at 1
roster["SwimmerID"] = range(1, len(roster) + 1)

roster.to_csv("swimmers_cleaned.csv", index=False)



st.subheader("Seleccionar Categoria")

race_started = st.session_state.get("race_started", False)

# Get unique race categories
race_categories = sorted(roster["Race Category"].dropna().unique())

selected_category = st.selectbox(
    "Choose a race category:",
    race_categories, disabled=race_started
)

filtered_swimmers = roster[
    roster["Race Category"] == selected_category
]

def age_category(age):
    if age < 14:
        return "Menores de 14"
    if age <= 19:
        return "14-19"
    if age <= 29:
        return "20-29"
    elif age <= 39:
        return "30-39"
    elif age <= 49:
        return "40-49"
    elif age <= 59:
        return "50-59"
    elif age <=69:
        return "60-69"
    elif age > 70:
        return "Mayores de 70"
    else:
        return "Open"

roster["Age Category"] = roster["Age"].apply(age_category)



# --- Initialize state ---
if "start_time" not in st.session_state:
    st.session_state.start_time = None
    st.session_state.results = {}
else:
    st.session_state.race_started = True

# --- Start race ---
col1, col2 = st.columns([2,3])
with col1:
    start_disabled = st.session_state.start_time is not None

    if st.button(
        "▶️ Comenzar carrera",
        use_container_width=True,
        disabled=start_disabled
    ):
        st.session_state.start_time = time.time()
        st.session_state.results = {}

with col2:
    chrono_placeholder = st.empty()

    if st.session_state.start_time:
        st_autorefresh(interval=200, key="chrono_refresh_col2")

        elapsed = time.time() - st.session_state.start_time

        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        centiseconds = int((elapsed - int(elapsed)) * 100)

        chrono_placeholder.markdown(
            f"### ⏱️  {hours:02d}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"
        )
    else:
        chrono_placeholder.markdown("### ⏱️  00:00:00.00")



st.divider()

# --- Swimmer buttons ---
st.subheader("Llegadas")

num_swimmers = 150
cols = st.columns(n_cols)  # n_cols columns for better mobile layout


st.subheader("Nadadores")

# Adjust columns for layout (better for mobile if 2–3 columns)
cols = st.columns(3)

num_swimmers = len(filtered_swimmers)

for i, row in enumerate(filtered_swimmers.itertuples()):
    swimmer_id = row.SwimmerID
    col = cols[i % n_cols]

    with col:
        if swimmer_id in st.session_state.results:
            st.button(
                f"✅ {swimmer_id}",
                disabled=True,
                use_container_width=True,
                key=f"done_{swimmer_id}"
            )
        else:
            if st.button(
                f"🏁 {swimmer_id}",
                use_container_width=True,
                disabled=st.session_state.start_time is None,
                key=f"btn_{swimmer_id}"
            ):
                elapsed = time.time() - st.session_state.start_time

                hours = int(elapsed // 3600)
                minutes = int((elapsed % 3600) // 60)
                seconds = int(elapsed % 60)

                finish_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

                st.session_state.results[swimmer_id] = finish_time



# --- Results table ---
st.divider()
st.subheader("Resultados Generales")

if st.session_state.results:

    times_df = pd.DataFrame(
        st.session_state.results.items(),
        columns=["SwimmerID", "Finish Time"]
    )

    final_df = (
        times_df
        .merge(roster, on="SwimmerID", how="left")
        .sort_values("Finish Time")
        .reset_index(drop=True)
    )
    final_df = final_df.drop(columns=["Viene"])

    # Get unique genders
    genders = sorted(final_df["Gender"].dropna().unique())

    if len(genders) > 0:

        # Create columns dynamically
        cols = st.columns(len(genders))

        for col, gender in zip(cols, genders):

            with col:
                st.markdown(f"### {gender}")

                gender_df = (
                    final_df[final_df["Gender"] == gender]
                    .sort_values("Finish Time")
                    .reset_index(drop=True)
                )

                gender_df.index = pd.RangeIndex(
                    start=1,
                    stop=len(gender_df) + 1
                )
                gender_df.index.name = "Rank"

                st.dataframe(
                    gender_df[[
                        "Name",
                        "SwimmerID",
                        "Age",
                        "Age Category",
                        "Club",
                        "Finish Time"
                    ]],
                    use_container_width=True
                )

    

    st.subheader("Resultados por categoria")

    for age_category in final_df["Age Category"].unique():

        st.markdown(f"## 🏅 {age_category}")

        age_df = final_df[final_df["Age Category"] == age_category]

        for gender in age_df["Gender"].unique():

            st.markdown(f"### {gender}")

            gender_df = age_df[age_df["Gender"] == gender]
            gender_df = gender_df.sort_values("Finish Time").reset_index(drop=True)

            gender_df.index = pd.RangeIndex(start=1, stop=len(gender_df)+1)
            gender_df.index.name = "Rank"

            st.dataframe(
                gender_df[[
                    "Name",
                    "SwimmerID",
                    "Age",
                    "Gender",
                    "Club",
                    "Finish Time"
                ]],
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
    st.info("Ningun tiempo registrado aun.")
st.markdown("---")

if st.button("🛑 Parar cronometro", use_container_width=True):

    st.session_state.start_time = None
    st.success("Fin!")
